# Context Management Troubleshooting

## Overview

This guide addresses issues related to context management in the Claude Code Context Engineering system, including overflow problems, compaction issues, memory management, and recovery strategies.

## Context Overflow

### Problem
Context size exceeds the maximum allowed limit, causing errors or degraded performance.

### Symptoms
- "Context overflow" error messages
- Commands failing with "context too large"
- Slow response times
- Truncated responses
- Missing information in responses

### Root Causes
1. **Accumulation of data** - Too much information stored
2. **Large files** - Including oversized files in context
3. **Repetitive content** - Duplicate information
4. **No cleanup** - Old context never removed
5. **Inefficient storage** - Poor context structure

### Solutions

#### Solution 1: Monitor Context Size

```python
# monitor_context.py
import os
import json
import sys
from datetime import datetime, timedelta

class ContextMonitor:
    """Monitor and manage context size"""

    def __init__(self, max_size=100000):
        self.max_size = max_size  # tokens
        self.warning_threshold = 0.8
        self.context_path = '.claude/context'

    def get_current_size(self):
        """Calculate current context size"""
        total_size = 0

        for root, dirs, files in os.walk(self.context_path):
            for file in files:
                filepath = os.path.join(root, file)
                file_size = os.path.getsize(filepath)
                # Approximate tokens (1 token ≈ 4 characters)
                tokens = file_size // 4
                total_size += tokens

        return total_size

    def get_context_breakdown(self):
        """Get detailed breakdown of context usage"""
        breakdown = {}

        for category in os.listdir(self.context_path):
            category_path = os.path.join(self.context_path, category)
            if os.path.isdir(category_path):
                size = 0
                file_count = 0

                for root, dirs, files in os.walk(category_path):
                    for file in files:
                        filepath = os.path.join(root, file)
                        size += os.path.getsize(filepath)
                        file_count += 1

                breakdown[category] = {
                    'size_bytes': size,
                    'size_tokens': size // 4,
                    'file_count': file_count,
                    'percentage': (size // 4) / self.max_size * 100
                }

        return breakdown

    def check_status(self):
        """Check context status and warnings"""
        current_size = self.get_current_size()
        usage_percent = current_size / self.max_size

        status = {
            'current_size': current_size,
            'max_size': self.max_size,
            'usage_percent': usage_percent * 100,
            'status': 'OK'
        }

        if usage_percent >= 1.0:
            status['status'] = 'OVERFLOW'
            print("🔴 CRITICAL: Context overflow!")
        elif usage_percent >= self.warning_threshold:
            status['status'] = 'WARNING'
            print(f"🟡 WARNING: Context at {usage_percent*100:.1f}% capacity")
        else:
            print(f"🟢 Context usage: {usage_percent*100:.1f}%")

        return status

    def visualize_usage(self):
        """Visualize context usage"""
        breakdown = self.get_context_breakdown()
        total_size = self.get_current_size()

        print("\n" + "=" * 60)
        print("CONTEXT USAGE BREAKDOWN")
        print("=" * 60)
        print(f"Total: {total_size:,} tokens / {self.max_size:,} tokens")
        print(f"Usage: {(total_size/self.max_size*100):.1f}%")
        print("-" * 60)

        # Sort by size
        sorted_categories = sorted(
            breakdown.items(),
            key=lambda x: x[1]['size_tokens'],
            reverse=True
        )

        for category, info in sorted_categories:
            bar_length = int(info['percentage'] / 2)
            bar = '█' * bar_length + '░' * (50 - bar_length)
            print(f"{category:15} [{bar}] {info['percentage']:.1f}%")
            print(f"                → {info['size_tokens']:,} tokens, {info['file_count']} files")

        print("=" * 60)

# Usage
monitor = ContextMonitor()
status = monitor.check_status()
monitor.visualize_usage()

if status['status'] == 'OVERFLOW':
    print("\n⚠️ Immediate action required!")
    print("Run: /compact-context --aggressive")
```

#### Solution 2: Automatic Context Management

```python
# auto_context_manager.py
import heapq
from typing import List, Dict, Tuple
import hashlib

class AutoContextManager:
    """Automatically manage context to prevent overflow"""

    def __init__(self, max_size=100000):
        self.max_size = max_size
        self.entries = []  # Min heap of (priority, size, id, content)
        self.current_size = 0
        self.entry_map = {}  # id -> entry mapping

    def calculate_priority(self, entry: Dict) -> float:
        """Calculate priority score for context entry"""
        # Higher score = higher priority (keep in context)

        score = 0.0

        # Recency (exponential decay)
        age_hours = (datetime.now() - entry['timestamp']).total_seconds() / 3600
        recency_score = math.exp(-age_hours / 24)  # Decay over 24 hours
        score += recency_score * 10

        # Access frequency
        access_score = min(entry['access_count'] / 10, 1.0)
        score += access_score * 5

        # Importance flag
        if entry.get('important', False):
            score += 20

        # Type priority
        type_scores = {
            'error': 15,
            'configuration': 12,
            'code': 10,
            'documentation': 8,
            'conversation': 5,
            'temporary': 2
        }
        score += type_scores.get(entry['type'], 5)

        # Size penalty (prefer smaller entries)
        size_penalty = min(entry['size'] / 1000, 5)
        score -= size_penalty

        return score

    def add_entry(self, content: str, metadata: Dict) -> str:
        """Add entry to context with automatic management"""
        # Calculate size
        size = len(content) // 4  # Approximate tokens

        # Generate ID
        entry_id = hashlib.md5(content.encode()).hexdigest()[:8]

        # Check for duplicates
        if entry_id in self.entry_map:
            # Update access count
            self.entry_map[entry_id]['access_count'] += 1
            return entry_id

        # Create entry
        entry = {
            'id': entry_id,
            'content': content,
            'size': size,
            'timestamp': datetime.now(),
            'access_count': 1,
            **metadata
        }

        # Calculate priority
        priority = self.calculate_priority(entry)

        # Add to heap (negate priority for min heap)
        heapq.heappush(self.entries, (-priority, size, entry_id, entry))
        self.entry_map[entry_id] = entry
        self.current_size += size

        # Manage overflow
        self.manage_overflow()

        return entry_id

    def manage_overflow(self):
        """Remove low-priority entries if overflow"""
        removed = []

        while self.current_size > self.max_size and self.entries:
            # Remove lowest priority entry
            priority, size, entry_id, entry = heapq.heappop(self.entries)

            # Skip if important
            if entry.get('important', False):
                # Re-add to heap
                heapq.heappush(self.entries, (priority, size, entry_id, entry))
                continue

            # Remove from context
            del self.entry_map[entry_id]
            self.current_size -= size
            removed.append(entry_id)

            print(f"Removed from context: {entry_id} (priority: {-priority:.2f})")

        if removed:
            print(f"Context cleaned: Removed {len(removed)} entries")
            print(f"New size: {self.current_size}/{self.max_size} tokens")

    def compact(self, aggressive=False):
        """Compact context by removing redundancy"""
        if aggressive:
            # Remove all non-essential entries
            self.entries = [
                e for e in self.entries
                if e[3].get('important', False) or e[3]['type'] in ['error', 'configuration']
            ]
            heapq.heapify(self.entries)

            # Rebuild entry map
            self.entry_map = {e[2]: e[3] for e in self.entries}
            self.current_size = sum(e[1] for e in self.entries)

        else:
            # Smart compaction
            self.remove_duplicates()
            self.merge_similar()
            self.compress_old()

    def remove_duplicates(self):
        """Remove duplicate content"""
        seen_hashes = set()
        unique_entries = []

        for priority, size, entry_id, entry in self.entries:
            content_hash = hashlib.md5(entry['content'].encode()).hexdigest()

            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_entries.append((priority, size, entry_id, entry))

        removed = len(self.entries) - len(unique_entries)
        if removed > 0:
            print(f"Removed {removed} duplicate entries")
            self.entries = unique_entries
            heapq.heapify(self.entries)

    def merge_similar(self):
        """Merge similar entries"""
        # Group by type and merge
        grouped = {}
        for priority, size, entry_id, entry in self.entries:
            key = (entry['type'], entry.get('source', ''))
            if key not in grouped:
                grouped[key] = []
            grouped[key].append((priority, size, entry_id, entry))

        merged_entries = []
        for key, group in grouped.items():
            if len(group) > 3:  # Merge if more than 3 similar entries
                # Create merged entry
                merged_content = "\n---\n".join(e[3]['content'] for e in group[:3])
                merged_entry = {
                    'id': hashlib.md5(merged_content.encode()).hexdigest()[:8],
                    'content': merged_content + f"\n... and {len(group)-3} more",
                    'size': len(merged_content) // 4,
                    'type': key[0],
                    'source': key[1],
                    'timestamp': max(e[3]['timestamp'] for e in group),
                    'access_count': sum(e[3]['access_count'] for e in group),
                    'merged': True
                }

                # Use highest priority
                max_priority = max(-e[0] for e in group)
                merged_entries.append((
                    -max_priority,
                    merged_entry['size'],
                    merged_entry['id'],
                    merged_entry
                ))
            else:
                merged_entries.extend(group)

        if len(merged_entries) < len(self.entries):
            print(f"Merged entries: {len(self.entries)} → {len(merged_entries)}")
            self.entries = merged_entries
            heapq.heapify(self.entries)

    def compress_old(self):
        """Compress old entries"""
        now = datetime.now()
        compressed = []

        for priority, size, entry_id, entry in self.entries:
            age = now - entry['timestamp']

            if age > timedelta(days=1) and not entry.get('important', False):
                # Compress content
                summary = self.summarize_content(entry['content'])
                if len(summary) < len(entry['content']) * 0.5:
                    entry['content'] = summary
                    entry['size'] = len(summary) // 4
                    entry['compressed'] = True
                    compressed.append(entry_id)

        if compressed:
            print(f"Compressed {len(compressed)} old entries")
            # Recalculate total size
            self.current_size = sum(e[1] for e in self.entries)

    def summarize_content(self, content: str) -> str:
        """Create summary of content"""
        lines = content.split('\n')
        if len(lines) > 10:
            # Keep first and last few lines
            summary = '\n'.join(lines[:3])
            summary += f"\n... ({len(lines)-6} lines omitted) ...\n"
            summary += '\n'.join(lines[-3:])
            return summary
        return content

# Usage
manager = AutoContextManager()

# Add entries
manager.add_entry(
    "Error occurred in module X",
    {'type': 'error', 'important': True}
)

manager.add_entry(
    "Configuration settings...",
    {'type': 'configuration'}
)

# Compact when needed
if manager.current_size > manager.max_size * 0.9:
    manager.compact()
```

#### Solution 3: Context Partitioning

```python
# context_partitioner.py
class ContextPartitioner:
    """Partition context into manageable chunks"""

    def __init__(self):
        self.partitions = {
            'active': [],      # Current working context
            'recent': [],      # Recently accessed
            'archive': [],     # Archived for reference
            'permanent': []    # Never remove
        }
        self.partition_sizes = {
            'active': 40000,
            'recent': 30000,
            'archive': 20000,
            'permanent': 10000
        }

    def partition_context(self, entries: List[Dict]):
        """Partition entries into categories"""
        # Sort by priority
        sorted_entries = sorted(
            entries,
            key=lambda x: self.calculate_priority(x),
            reverse=True
        )

        for entry in sorted_entries:
            # Determine partition
            if entry.get('permanent', False):
                partition = 'permanent'
            elif self.is_active(entry):
                partition = 'active'
            elif self.is_recent(entry):
                partition = 'recent'
            else:
                partition = 'archive'

            # Check partition size
            current_size = sum(e['size'] for e in self.partitions[partition])
            if current_size + entry['size'] <= self.partition_sizes[partition]:
                self.partitions[partition].append(entry)

    def is_active(self, entry):
        """Check if entry is actively used"""
        return (
            entry['access_count'] > 5 and
            (datetime.now() - entry['timestamp']).total_seconds() < 3600
        )

    def is_recent(self, entry):
        """Check if entry is recent"""
        return (datetime.now() - entry['timestamp']).days < 1

    def get_active_context(self):
        """Get only active context for current operation"""
        return self.partitions['active'] + self.partitions['permanent']

    def rotate_partitions(self):
        """Rotate partitions based on usage"""
        # Move old active to recent
        for entry in self.partitions['active']:
            if not self.is_active(entry):
                self.partitions['recent'].append(entry)

        # Move old recent to archive
        for entry in self.partitions['recent']:
            if not self.is_recent(entry):
                self.partitions['archive'].append(entry)

        # Clean up archive
        self.partitions['archive'] = [
            e for e in self.partitions['archive']
            if (datetime.now() - e['timestamp']).days < 7
        ]
```

## Compaction Issues

### Problem
Context compaction fails or doesn't effectively reduce size.

### Symptoms
- Compaction command fails
- Size doesn't decrease after compaction
- Loss of important information
- Corrupted context after compaction

### Solutions

#### Solution 1: Safe Compaction Strategy

```python
# safe_compaction.py
import json
import shutil
from pathlib import Path

class SafeCompactor:
    """Safe context compaction with rollback"""

    def __init__(self):
        self.context_dir = Path('.claude/context')
        self.backup_dir = Path('.claude/context_backups')
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self) -> Path:
        """Create backup before compaction"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / timestamp

        shutil.copytree(self.context_dir, backup_path)
        print(f"✅ Backup created: {backup_path}")

        return backup_path

    def compact_safely(self, strategy='balanced'):
        """Compact with safety checks and rollback"""
        # Create backup
        backup_path = self.create_backup()

        try:
            # Get initial state
            initial_size = self.get_context_size()
            initial_entries = self.count_entries()

            print(f"Initial: {initial_size:,} bytes, {initial_entries} entries")

            # Apply compaction strategy
            if strategy == 'aggressive':
                self.aggressive_compact()
            elif strategy == 'smart':
                self.smart_compact()
            else:
                self.balanced_compact()

            # Verify results
            final_size = self.get_context_size()
            final_entries = self.count_entries()

            print(f"Final: {final_size:,} bytes, {final_entries} entries")
            print(f"Reduction: {((1 - final_size/initial_size) * 100):.1f}%")

            # Validate compaction
            if not self.validate_compaction():
                raise Exception("Compaction validation failed")

            # Clean old backups
            self.cleanup_old_backups()

            return True

        except Exception as e:
            print(f"❌ Compaction failed: {e}")
            print(f"Rolling back to: {backup_path}")
            self.rollback(backup_path)
            return False

    def balanced_compact(self):
        """Balanced compaction strategy"""
        # Remove duplicates
        self.remove_duplicate_files()

        # Compress large files
        self.compress_large_files()

        # Merge similar entries
        self.merge_similar_entries()

        # Archive old entries
        self.archive_old_entries(days=7)

    def aggressive_compact(self):
        """Aggressive compaction - maximum reduction"""
        # Keep only essential
        essential_types = ['error', 'configuration', 'current_task']

        for entry_file in self.context_dir.rglob('*.json'):
            with open(entry_file, 'r') as f:
                entry = json.load(f)

            if entry.get('type') not in essential_types:
                if not entry.get('important', False):
                    entry_file.unlink()

        # Aggressive summarization
        self.summarize_all_content(max_length=500)

    def smart_compact(self):
        """Smart compaction using ML-like scoring"""
        entries = []

        # Load all entries with metadata
        for entry_file in self.context_dir.rglob('*.json'):
            with open(entry_file, 'r') as f:
                entry = json.load(f)
                entry['path'] = entry_file
                entry['score'] = self.calculate_importance_score(entry)
                entries.append(entry)

        # Sort by score
        entries.sort(key=lambda x: x['score'], reverse=True)

        # Keep top entries within size limit
        total_size = 0
        size_limit = 80000 * 4  # 80k tokens in bytes

        for entry in entries:
            entry_size = len(json.dumps(entry))
            if total_size + entry_size > size_limit:
                # Remove this and remaining entries
                entry['path'].unlink()
            else:
                total_size += entry_size

    def calculate_importance_score(self, entry):
        """Calculate importance score for entry"""
        score = 0

        # Recency
        age_days = (datetime.now() - datetime.fromisoformat(entry['timestamp'])).days
        score += max(0, 10 - age_days)

        # Access frequency
        score += min(entry.get('access_count', 0), 10)

        # Type importance
        type_scores = {
            'error': 20,
            'configuration': 15,
            'code': 10,
            'documentation': 5
        }
        score += type_scores.get(entry.get('type', ''), 0)

        # Flags
        if entry.get('important', False):
            score += 50
        if entry.get('pinned', False):
            score += 100

        return score

    def compress_large_files(self, threshold=10000):
        """Compress large context files"""
        for entry_file in self.context_dir.rglob('*.json'):
            if entry_file.stat().st_size > threshold:
                with open(entry_file, 'r') as f:
                    entry = json.load(f)

                # Compress content
                if 'content' in entry and len(entry['content']) > 1000:
                    entry['content'] = self.compress_text(entry['content'])
                    entry['compressed'] = True

                    with open(entry_file, 'w') as f:
                        json.dump(entry, f, indent=2)

    def compress_text(self, text: str) -> str:
        """Compress text while maintaining key information"""
        lines = text.split('\n')

        if len(lines) <= 20:
            return text

        # Keep structure but reduce content
        compressed = []
        compressed.extend(lines[:5])  # Keep beginning
        compressed.append(f"\n... [{len(lines)-10} lines compressed] ...\n")
        compressed.extend(lines[-5:])  # Keep end

        return '\n'.join(compressed)

    def validate_compaction(self) -> bool:
        """Validate compaction didn't break context"""
        try:
            # Check structure
            if not self.context_dir.exists():
                return False

            # Check for required files
            required = ['configuration.json', 'state.json']
            for req in required:
                if not (self.context_dir / req).exists():
                    print(f"Missing required file: {req}")
                    return False

            # Check JSON validity
            for json_file in self.context_dir.rglob('*.json'):
                try:
                    with open(json_file, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    print(f"Invalid JSON: {json_file}")
                    return False

            return True

        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def rollback(self, backup_path: Path):
        """Rollback to backup"""
        # Remove current context
        shutil.rmtree(self.context_dir)

        # Restore backup
        shutil.copytree(backup_path, self.context_dir)
        print(f"✅ Rolled back to: {backup_path}")

# Usage
compactor = SafeCompactor()
compactor.compact_safely(strategy='smart')
```

## Memory Problems

### Problem
High memory usage or memory leaks in context management.

### Symptoms
- Increasing memory consumption
- Out of memory errors
- System slowdown
- Memory not released after operations

### Solutions

#### Solution 1: Memory-Efficient Context Loading

```python
# memory_efficient_context.py
import gc
import mmap
import pickle
from typing import Generator, Any

class MemoryEfficientContext:
    """Memory-efficient context management"""

    def __init__(self):
        self.cache_file = '.claude/context.cache'
        self.index_file = '.claude/context.index'
        self.memory_limit = 500 * 1024 * 1024  # 500MB
        self.current_usage = 0

    def stream_context(self) -> Generator[Dict, None, None]:
        """Stream context entries without loading all into memory"""
        with open(self.cache_file, 'rb') as f:
            # Use memory mapping for efficient reading
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped:
                position = 0
                while position < len(mmapped):
                    # Read entry size
                    size_bytes = mmapped[position:position+4]
                    if not size_bytes:
                        break

                    size = int.from_bytes(size_bytes, 'little')
                    position += 4

                    # Read entry
                    entry_bytes = mmapped[position:position+size]
                    position += size

                    # Yield deserialized entry
                    yield pickle.loads(entry_bytes)

                    # Force garbage collection periodically
                    if position % (10 * 1024 * 1024) == 0:  # Every 10MB
                        gc.collect()

    def lazy_load_entry(self, entry_id: str) -> Any:
        """Load single entry on demand"""
        # Load index
        with open(self.index_file, 'rb') as f:
            index = pickle.load(f)

        if entry_id not in index:
            return None

        # Get entry position and size
        position, size = index[entry_id]

        # Read only this entry
        with open(self.cache_file, 'rb') as f:
            f.seek(position)
            entry_bytes = f.read(size)

        return pickle.loads(entry_bytes)

    def chunked_processing(self, chunk_size=100):
        """Process context in chunks to limit memory"""
        chunk = []

        for entry in self.stream_context():
            chunk.append(entry)

            if len(chunk) >= chunk_size:
                # Process chunk
                yield chunk

                # Clear chunk and collect garbage
                chunk.clear()
                gc.collect()

        # Process remaining
        if chunk:
            yield chunk

    def memory_monitor(self):
        """Monitor memory usage during context operations"""
        import psutil
        import threading

        process = psutil.Process()

        def monitor():
            while self.monitoring:
                memory_info = process.memory_info()
                self.current_usage = memory_info.rss

                if self.current_usage > self.memory_limit:
                    print(f"⚠️ Memory limit exceeded: {self.current_usage / 1024 / 1024:.1f}MB")
                    self.trigger_cleanup()

                time.sleep(1)

        self.monitoring = True
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.start()

    def trigger_cleanup(self):
        """Trigger memory cleanup"""
        # Force garbage collection
        gc.collect()
        gc.collect()  # Second pass for circular references

        # Clear caches
        self.clear_caches()

        # Compact if needed
        if self.current_usage > self.memory_limit * 0.9:
            self.emergency_compact()

    def clear_caches(self):
        """Clear all caches"""
        # Clear Python caches
        import linecache
        import functools

        linecache.clearcache()

        # Clear function caches
        for obj in gc.get_objects():
            if isinstance(obj, functools.lru_cache):
                obj.cache_clear()

    def emergency_compact(self):
        """Emergency compaction when memory critical"""
        print("🔴 Emergency memory compaction triggered")

        # Remove all non-essential context
        essential_only = []

        for entry in self.stream_context():
            if entry.get('essential', False) or entry.get('type') == 'error':
                essential_only.append(entry)

        # Rewrite context with essential only
        self.rewrite_context(essential_only)

        # Force cleanup
        gc.collect()

# Usage
context = MemoryEfficientContext()

# Process in chunks
for chunk in context.chunked_processing(chunk_size=50):
    # Process chunk
    process_chunk(chunk)

    # Chunk is automatically cleared after processing
```

## Recovery Strategies

### Context Recovery Procedures

#### Solution 1: Context Repair Tool

```python
# repair_context.py
#!/usr/bin/env python3

import json
import os
import shutil
from pathlib import Path
from datetime import datetime

class ContextRepairTool:
    """Repair and recover corrupted context"""

    def __init__(self):
        self.context_dir = Path('.claude/context')
        self.recovery_dir = Path('.claude/recovery')
        self.recovery_dir.mkdir(exist_ok=True)

    def diagnose(self):
        """Diagnose context issues"""
        issues = []

        # Check directory structure
        if not self.context_dir.exists():
            issues.append("Context directory missing")
            return issues

        # Check for corrupted files
        for file_path in self.context_dir.rglob('*'):
            if file_path.is_file():
                try:
                    if file_path.suffix == '.json':
                        with open(file_path, 'r') as f:
                            json.load(f)
                except json.JSONDecodeError:
                    issues.append(f"Corrupted JSON: {file_path}")
                except Exception as e:
                    issues.append(f"Cannot read {file_path}: {e}")

        # Check for orphaned entries
        index_file = self.context_dir / 'index.json'
        if index_file.exists():
            with open(index_file, 'r') as f:
                index = json.load(f)

            for entry_id, entry_path in index.items():
                if not Path(entry_path).exists():
                    issues.append(f"Orphaned index entry: {entry_id}")

        # Check size issues
        total_size = sum(f.stat().st_size for f in self.context_dir.rglob('*'))
        if total_size > 100 * 1024 * 1024:  # 100MB
            issues.append(f"Context too large: {total_size / 1024 / 1024:.1f}MB")

        return issues

    def repair(self, auto_fix=True):
        """Repair context issues"""
        print("Starting context repair...")
        issues = self.diagnose()

        if not issues:
            print("✅ No issues found")
            return True

        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")

        if not auto_fix:
            response = input("\nAttempt automatic repair? (y/n): ")
            if response.lower() != 'y':
                return False

        # Create backup
        self.backup_context()

        # Repair each issue
        repaired = 0
        for issue in issues:
            if self.repair_issue(issue):
                repaired += 1

        print(f"\n✅ Repaired {repaired}/{len(issues)} issues")

        # Rebuild index
        self.rebuild_index()

        return repaired == len(issues)

    def repair_issue(self, issue: str) -> bool:
        """Repair specific issue"""
        try:
            if "Context directory missing" in issue:
                self.context_dir.mkdir(parents=True, exist_ok=True)
                self.initialize_context()
                return True

            elif "Corrupted JSON" in issue:
                file_path = issue.split(": ")[1]
                return self.repair_corrupted_json(Path(file_path))

            elif "Orphaned index entry" in issue:
                entry_id = issue.split(": ")[1]
                return self.remove_orphaned_entry(entry_id)

            elif "Context too large" in issue:
                return self.emergency_compact()

            else:
                print(f"Cannot auto-repair: {issue}")
                return False

        except Exception as e:
            print(f"Repair failed for '{issue}': {e}")
            return False

    def repair_corrupted_json(self, file_path: Path) -> bool:
        """Attempt to repair corrupted JSON file"""
        try:
            # Try to read and fix common issues
            with open(file_path, 'r') as f:
                content = f.read()

            # Common fixes
            # Remove trailing commas
            import re
            content = re.sub(r',\s*}', '}', content)
            content = re.sub(r',\s*]', ']', content)

            # Try to parse
            try:
                data = json.loads(content)
                # Write back fixed version
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"✅ Repaired: {file_path}")
                return True
            except:
                # Move to recovery
                recovery_path = self.recovery_dir / file_path.name
                shutil.move(file_path, recovery_path)
                print(f"⚠️ Moved corrupted file to recovery: {recovery_path}")
                return True

        except Exception as e:
            print(f"Failed to repair {file_path}: {e}")
            return False

    def rebuild_index(self):
        """Rebuild context index"""
        index = {}

        for file_path in self.context_dir.rglob('*.json'):
            if file_path.name != 'index.json':
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)

                    entry_id = data.get('id', file_path.stem)
                    index[entry_id] = str(file_path)

                except:
                    pass

        # Save index
        index_file = self.context_dir / 'index.json'
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)

        print(f"✅ Rebuilt index with {len(index)} entries")

    def backup_context(self):
        """Create context backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.recovery_dir / f'backup_{timestamp}'

        if self.context_dir.exists():
            shutil.copytree(self.context_dir, backup_path)
            print(f"✅ Backup created: {backup_path}")

    def restore_backup(self, backup_name: str):
        """Restore from backup"""
        backup_path = self.recovery_dir / backup_name

        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_name}")
            return False

        # Remove current context
        if self.context_dir.exists():
            shutil.rmtree(self.context_dir)

        # Restore backup
        shutil.copytree(backup_path, self.context_dir)
        print(f"✅ Restored from: {backup_name}")
        return True

    def initialize_context(self):
        """Initialize new context structure"""
        # Create default structure
        (self.context_dir / 'active').mkdir(exist_ok=True)
        (self.context_dir / 'archive').mkdir(exist_ok=True)

        # Create default files
        default_state = {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'last_compaction': None,
            'size': 0
        }

        with open(self.context_dir / 'state.json', 'w') as f:
            json.dump(default_state, f, indent=2)

        # Create empty index
        with open(self.context_dir / 'index.json', 'w') as f:
            json.dump({}, f)

        print("✅ Initialized new context structure")

# Usage
if __name__ == "__main__":
    repair_tool = ContextRepairTool()

    # Diagnose issues
    issues = repair_tool.diagnose()

    if issues:
        print(f"Found {len(issues)} issues")
        # Attempt repair
        repair_tool.repair(auto_fix=True)
    else:
        print("✅ Context is healthy")
```

#### Solution 2: Emergency Recovery

```bash
#!/bin/bash
# emergency_context_recovery.sh

echo "Emergency Context Recovery"
echo "========================="

# Function to check context health
check_context_health() {
    local status="healthy"

    # Check if context directory exists
    if [ ! -d ".claude/context" ]; then
        echo "❌ Context directory missing"
        status="critical"
    fi

    # Check context size
    if [ -d ".claude/context" ]; then
        size=$(du -sb .claude/context | cut -f1)
        if [ $size -gt 104857600 ]; then  # 100MB
            echo "⚠️ Context too large: $(($size / 1048576))MB"
            status="warning"
        fi
    fi

    # Check for corrupted files
    find .claude/context -name "*.json" -type f 2>/dev/null | while read file; do
        if ! python3 -m json.tool "$file" > /dev/null 2>&1; then
            echo "❌ Corrupted JSON: $file"
            status="critical"
        fi
    done

    echo "Context health: $status"
    return $([ "$status" = "healthy" ] && echo 0 || echo 1)
}

# Function to perform emergency recovery
emergency_recovery() {
    echo "Starting emergency recovery..."

    # 1. Create emergency backup
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir=".claude/emergency_backup_$timestamp"
    echo "Creating emergency backup: $backup_dir"
    cp -r .claude/context "$backup_dir" 2>/dev/null || true

    # 2. Clear corrupt files
    echo "Removing corrupted files..."
    find .claude/context -name "*.json" -type f 2>/dev/null | while read file; do
        if ! python3 -m json.tool "$file" > /dev/null 2>&1; then
            echo "  Removing: $file"
            rm -f "$file"
        fi
    done

    # 3. Compact context aggressively
    echo "Performing aggressive compaction..."
    python3 << 'EOF'
import os
import json
import shutil
from pathlib import Path

context_dir = Path('.claude/context')
if context_dir.exists():
    # Keep only essential files
    essential = ['state.json', 'index.json', 'configuration.json']

    for file in context_dir.rglob('*.json'):
        if file.name not in essential:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)

                # Keep only if marked as important or recent error
                if not (data.get('important') or data.get('type') == 'error'):
                    file.unlink()
                    print(f"  Removed: {file}")
            except:
                file.unlink()
                print(f"  Removed corrupted: {file}")
EOF

    # 4. Rebuild index
    echo "Rebuilding context index..."
    python3 -c "
from pathlib import Path
import json

index = {}
context_dir = Path('.claude/context')

for file in context_dir.rglob('*.json'):
    if file.name not in ['index.json', 'state.json']:
        try:
            with open(file, 'r') as f:
                data = json.load(f)
            index[data.get('id', file.stem)] = str(file)
        except:
            pass

with open(context_dir / 'index.json', 'w') as f:
    json.dump(index, f, indent=2)

print(f'  Index rebuilt with {len(index)} entries')
"

    # 5. Reset state
    echo "Resetting context state..."
    cat > .claude/context/state.json << EOF
{
  "version": "1.0",
  "last_reset": "$(date -Iseconds)",
  "emergency_recovery": true,
  "size": 0
}
EOF

    echo "✅ Emergency recovery complete"
}

# Main execution
echo "Checking context health..."
if check_context_health; then
    echo "✅ Context is healthy"
else
    echo ""
    read -p "Context needs recovery. Proceed? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        emergency_recovery
    else
        echo "Recovery cancelled"
        exit 1
    fi
fi
```

## Best Practices

### Context Management Guidelines

```markdown
# Context Management Best Practices

## 1. Size Management
- Monitor context size continuously
- Set up automatic compaction at 80% capacity
- Use partitioning for large contexts
- Implement rolling windows for temporal data

## 2. Performance
- Use lazy loading for large entries
- Stream context instead of loading all
- Implement caching for frequently accessed items
- Process in chunks to limit memory

## 3. Reliability
- Always backup before compaction
- Validate after modifications
- Implement recovery procedures
- Use checksums for integrity

## 4. Organization
- Categorize context entries
- Use consistent naming conventions
- Implement retention policies
- Archive old but important data

## 5. Monitoring
- Set up size alerts
- Track access patterns
- Monitor performance metrics
- Log compaction operations
```

### Preventive Measures

```python
# preventive_measures.py
class ContextPreventiveCare:
    """Preventive measures for context health"""

    def __init__(self):
        self.health_checks = []
        self.maintenance_tasks = []

    def setup_monitoring(self):
        """Setup continuous monitoring"""
        # Size monitoring
        self.add_health_check(
            name="size_check",
            func=self.check_size,
            interval=300,  # 5 minutes
            alert_threshold=0.8
        )

        # Integrity monitoring
        self.add_health_check(
            name="integrity_check",
            func=self.check_integrity,
            interval=3600,  # 1 hour
            alert_threshold=1  # Any corruption
        )

        # Performance monitoring
        self.add_health_check(
            name="performance_check",
            func=self.check_performance,
            interval=1800,  # 30 minutes
            alert_threshold=5  # 5 seconds response time
        )

    def setup_maintenance(self):
        """Setup regular maintenance"""
        # Daily compaction
        self.add_maintenance_task(
            name="daily_compact",
            func=self.compact_context,
            schedule="daily",
            time="03:00"
        )

        # Weekly backup
        self.add_maintenance_task(
            name="weekly_backup",
            func=self.backup_context,
            schedule="weekly",
            day="sunday",
            time="02:00"
        )

        # Monthly cleanup
        self.add_maintenance_task(
            name="monthly_cleanup",
            func=self.deep_cleanup,
            schedule="monthly",
            day=1,
            time="04:00"
        )

    def implement_limits(self):
        """Implement context limits"""
        limits = {
            'max_total_size': 100000,  # tokens
            'max_entry_size': 5000,    # tokens
            'max_entries': 1000,
            'max_age_days': 30,
            'min_importance_score': 0.2
        }

        return limits

    def create_retention_policy(self):
        """Create retention policy"""
        policy = {
            'error': {'days': 90, 'priority': 'high'},
            'configuration': {'days': 'permanent', 'priority': 'critical'},
            'conversation': {'days': 7, 'priority': 'low'},
            'temporary': {'days': 1, 'priority': 'lowest'},
            'code': {'days': 30, 'priority': 'medium'},
            'documentation': {'days': 60, 'priority': 'medium'}
        }

        return policy
```

## Summary

Context management issues typically involve:

1. **Overflow Problems** - Context size exceeding limits
2. **Compaction Issues** - Failed or ineffective compaction
3. **Memory Problems** - High usage or leaks
4. **Corruption** - Damaged context files
5. **Performance** - Slow operations or retrieval

Key solutions:
1. Monitor context size continuously
2. Implement automatic management
3. Use safe compaction strategies
4. Stream context for memory efficiency
5. Maintain backups and recovery procedures

Prevention is key:
- Set up monitoring and alerts
- Implement retention policies
- Regular maintenance tasks
- Proper partitioning strategies
- Continuous validation

Always backup before major operations and have recovery procedures ready.
