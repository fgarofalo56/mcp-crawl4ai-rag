# Multi-Agent Coordination Examples

## Comprehensive Multi-Agent System Implementation

This guide demonstrates sophisticated multi-agent coordination using the Claude Code Context Engineering system, showing how multiple AI agents work together to solve complex problems.

## Table of Contents

1. [Agent Architecture](#architecture)
2. [Basic Agent Coordination](#basic-coordination)
3. [Complex Workflow](#complex-workflow)
4. [Agent Communication](#communication)
5. [Task Distribution](#task-distribution)
6. [Complete System](#complete-system)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Architecture

### Multi-Agent System Design

#### System Overview

```yaml
# agent-architecture.yaml
agents:
  research-agent:
    role: Information Gatherer
    capabilities:
      - Web research
      - Documentation analysis
      - Pattern identification
      - Knowledge synthesis
    tools:
      - WebSearch
      - WebFetch
      - DocumentAnalyzer

  architect-agent:
    role: System Designer
    capabilities:
      - Architecture design
      - Component planning
      - Interface definition
      - Technology selection
    tools:
      - DiagramGenerator
      - ArchitectureValidator
      - TechStackAnalyzer

  developer-agent:
    role: Code Implementation
    capabilities:
      - Code generation
      - API implementation
      - Database design
      - Testing
    tools:
      - CodeGenerator
      - TestCreator
      - DatabaseDesigner

  reviewer-agent:
    role: Quality Assurance
    capabilities:
      - Code review
      - Security analysis
      - Performance testing
      - Best practice validation
    tools:
      - CodeAnalyzer
      - SecurityScanner
      - PerformanceProfiler

  devops-agent:
    role: Deployment & Operations
    capabilities:
      - CI/CD setup
      - Infrastructure provisioning
      - Monitoring configuration
      - Deployment automation
    tools:
      - AzureProvisioner
      - DockerBuilder
      - KubernetesDeployer

coordination:
  communication: event-driven
  state-management: shared-context
  conflict-resolution: priority-based
  error-handling: supervisor-pattern
```

#### Agent Implementation

```python
# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import asyncio
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(self, name: str, capabilities: List[str]):
        self.name = name
        self.capabilities = capabilities
        self.state = "idle"
        self.current_task = None
        self.message_queue = asyncio.Queue()
        self.knowledge_base = {}

    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a specific task"""
        pass

    async def receive_message(self, message: Dict[str, Any]):
        """Receive message from other agents"""
        await self.message_queue.put(message)

    async def send_message(self, recipient: str, content: Dict[str, Any]):
        """Send message to another agent"""
        message = {
            'from': self.name,
            'to': recipient,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        # Send through coordinator
        await self.coordinator.route_message(message)

    async def run(self):
        """Main agent loop"""
        while True:
            # Process messages
            if not self.message_queue.empty():
                message = await self.message_queue.get()
                await self.handle_message(message)

            # Process current task
            if self.current_task and self.state == "working":
                result = await self.process_task(self.current_task)
                await self.complete_task(result)

            await asyncio.sleep(0.1)

    @abstractmethod
    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming message"""
        pass

    async def complete_task(self, result: Dict[str, Any]):
        """Complete current task and notify coordinator"""
        self.state = "idle"
        await self.send_message("coordinator", {
            'type': 'task_complete',
            'task_id': self.current_task['id'],
            'result': result
        })
        self.current_task = None
```

## Basic Coordination

### Two-Agent Collaboration Example

#### Step 1: Research and Development Agents

```python
# agents/research_agent.py
class ResearchAgent(BaseAgent):
    """Agent responsible for research and information gathering"""

    def __init__(self):
        super().__init__(
            name="research-agent",
            capabilities=["web_search", "documentation_analysis", "pattern_extraction"]
        )

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Research a topic and gather information"""

        topic = task['topic']
        self.state = "researching"

        # Perform web search
        search_results = await self.web_search(topic)

        # Analyze documentation
        docs = await self.analyze_documentation(search_results)

        # Extract patterns
        patterns = await self.extract_patterns(docs)

        # Synthesize findings
        synthesis = {
            'topic': topic,
            'key_findings': self.summarize_findings(search_results),
            'best_practices': patterns,
            'recommendations': self.generate_recommendations(patterns),
            'sources': [r['url'] for r in search_results[:5]]
        }

        return synthesis

    async def web_search(self, query: str) -> List[Dict]:
        """Perform web search"""
        # Use WebSearch tool
        results = await tools.web_search(query)
        return results

    async def analyze_documentation(self, sources: List[Dict]) -> List[Dict]:
        """Analyze documentation from sources"""
        analyzed = []
        for source in sources:
            content = await tools.web_fetch(source['url'])
            analysis = await self.analyze_content(content)
            analyzed.append(analysis)
        return analyzed

    async def extract_patterns(self, docs: List[Dict]) -> List[str]:
        """Extract common patterns from documentation"""
        patterns = []
        # Pattern extraction logic
        for doc in docs:
            if 'patterns' in doc:
                patterns.extend(doc['patterns'])
        return list(set(patterns))  # Unique patterns

# agents/developer_agent.py
class DeveloperAgent(BaseAgent):
    """Agent responsible for code implementation"""

    def __init__(self):
        super().__init__(
            name="developer-agent",
            capabilities=["code_generation", "api_implementation", "testing"]
        )
        self.research_context = None

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Implement code based on research"""

        if task['type'] == 'implement':
            # Wait for research if needed
            if not self.research_context:
                await self.request_research(task['requirements'])
                return {'status': 'waiting_for_research'}

            # Generate implementation
            code = await self.generate_implementation(
                task['requirements'],
                self.research_context
            )

            # Create tests
            tests = await self.generate_tests(code)

            # Validate implementation
            validation = await self.validate_code(code, tests)

            return {
                'code': code,
                'tests': tests,
                'validation': validation,
                'files_created': self.get_created_files()
            }

    async def generate_implementation(self, requirements: Dict, research: Dict) -> str:
        """Generate code implementation"""

        # Apply best practices from research
        best_practices = research.get('best_practices', [])

        code_template = f"""
# Generated based on research findings
# Best practices applied: {', '.join(best_practices)}

import asyncio
from typing import Dict, Any

class Implementation:
    '''Implementation based on research and requirements'''

    def __init__(self):
        # Apply patterns from research
        {self.apply_patterns(best_practices)}

    async def execute(self, data: Dict[str, Any]):
        '''Main execution method'''
        # Implementation logic
        {self.generate_logic(requirements)}

        return result
"""
        return code_template

    async def request_research(self, requirements: Dict):
        """Request research from research agent"""
        await self.send_message("research-agent", {
            'type': 'research_request',
            'requirements': requirements
        })

    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming messages"""
        if message['from'] == 'research-agent':
            if message['content']['type'] == 'research_complete':
                self.research_context = message['content']['data']
```

#### Step 2: Coordination Implementation

```bash
# Start two-agent collaboration
/agent-coordinate "Build a REST API for user management" \
  --agents "research,developer"

# System output:
# ✓ Starting research-agent...
# ✓ Starting developer-agent...
# ✓ Coordinator initialized
#
# Research Agent: Researching REST API best practices...
# Research Agent: Found 15 relevant sources
# Research Agent: Extracted 8 best practice patterns
#
# Developer Agent: Waiting for research...
# Developer Agent: Received research context
# Developer Agent: Implementing based on findings...
#
# ✓ Task completed successfully
# Files created:
# - api/user_management.py
# - tests/test_user_management.py
# - docs/api_documentation.md
```

## Complex Workflow

### Four-Agent System for Full Application Development

#### Step 1: Complete Agent System

```python
# coordinator/orchestrator.py
class AgentOrchestrator:
    """Orchestrates multiple agents for complex workflows"""

    def __init__(self):
        self.agents = {}
        self.task_queue = asyncio.Queue()
        self.completed_tasks = []
        self.workflow = None
        self.shared_context = {}

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        agent.coordinator = self

    async def execute_workflow(self, workflow: Dict[str, Any]):
        """Execute a complex multi-agent workflow"""

        self.workflow = workflow
        stages = workflow['stages']

        for stage in stages:
            print(f"Executing stage: {stage['name']}")

            # Parallel tasks within stage
            if stage.get('parallel'):
                await self.execute_parallel_tasks(stage['tasks'])
            else:
                # Sequential tasks
                for task in stage['tasks']:
                    await self.execute_task(task)

            # Wait for stage completion
            await self.wait_for_stage_completion(stage)

            # Update shared context
            self.update_context(stage)

        return self.generate_workflow_report()

    async def execute_task(self, task: Dict[str, Any]):
        """Execute a single task"""
        agent_name = task['agent']
        agent = self.agents.get(agent_name)

        if not agent:
            raise ValueError(f"Agent {agent_name} not found")

        # Add context to task
        task['context'] = self.shared_context

        # Assign task to agent
        agent.current_task = task
        agent.state = "working"

        # Track task
        self.task_queue.put_nowait(task)

    async def execute_parallel_tasks(self, tasks: List[Dict]):
        """Execute multiple tasks in parallel"""
        coroutines = []
        for task in tasks:
            coroutines.append(self.execute_task(task))

        await asyncio.gather(*coroutines)

    async def route_message(self, message: Dict[str, Any]):
        """Route messages between agents"""
        recipient = message['to']

        if recipient == "coordinator":
            await self.handle_coordinator_message(message)
        elif recipient == "broadcast":
            await self.broadcast_message(message)
        elif recipient in self.agents:
            await self.agents[recipient].receive_message(message)

    async def handle_coordinator_message(self, message: Dict[str, Any]):
        """Handle messages sent to coordinator"""
        if message['content']['type'] == 'task_complete':
            task_id = message['content']['task_id']
            result = message['content']['result']

            # Update completed tasks
            self.completed_tasks.append({
                'task_id': task_id,
                'agent': message['from'],
                'result': result,
                'timestamp': message['timestamp']
            })

            # Update shared context
            self.shared_context[f"{message['from']}_result"] = result
```

#### Step 2: Complex Workflow Definition

```yaml
# workflows/ecommerce_platform.yaml
name: E-Commerce Platform Development
description: Build complete e-commerce platform with microservices

stages:
  - name: Research and Planning
    parallel: true
    tasks:
      - agent: research-agent
        type: research
        topic: "E-commerce platform architecture patterns"
        output: architecture_patterns

      - agent: research-agent
        type: research
        topic: "Payment processing best practices"
        output: payment_patterns

      - agent: research-agent
        type: research
        topic: "Inventory management systems"
        output: inventory_patterns

  - name: Architecture Design
    tasks:
      - agent: architect-agent
        type: design
        input:
          - architecture_patterns
          - payment_patterns
          - inventory_patterns
        requirements:
          - Microservices architecture
          - Event-driven communication
          - Horizontal scalability
        output: system_architecture

  - name: Implementation
    parallel: true
    tasks:
      - agent: developer-agent
        type: implement
        service: user-service
        architecture: system_architecture
        output: user_service_code

      - agent: developer-agent
        type: implement
        service: product-service
        architecture: system_architecture
        output: product_service_code

      - agent: developer-agent
        type: implement
        service: order-service
        architecture: system_architecture
        output: order_service_code

      - agent: developer-agent
        type: implement
        service: payment-service
        architecture: system_architecture
        output: payment_service_code

  - name: Quality Assurance
    tasks:
      - agent: reviewer-agent
        type: review
        input:
          - user_service_code
          - product_service_code
          - order_service_code
          - payment_service_code
        checks:
          - code_quality
          - security
          - performance
          - best_practices
        output: review_report

  - name: Deployment
    tasks:
      - agent: devops-agent
        type: deploy
        input:
          - review_report
          - all_services
        environment: staging
        infrastructure:
          - kubernetes
          - azure
        output: deployment_status

  - name: Validation
    tasks:
      - agent: reviewer-agent
        type: validate
        deployment: deployment_status
        tests:
          - smoke_tests
          - integration_tests
          - load_tests
        output: validation_report
```

#### Step 3: Execution

```python
# execute_workflow.py
import asyncio
from coordinator.orchestrator import AgentOrchestrator
from agents import (
    ResearchAgent, ArchitectAgent, DeveloperAgent,
    ReviewerAgent, DevOpsAgent
)

async def build_ecommerce_platform():
    """Execute complete e-commerce platform build"""

    # Initialize orchestrator
    orchestrator = AgentOrchestrator()

    # Register agents
    orchestrator.register_agent(ResearchAgent())
    orchestrator.register_agent(ArchitectAgent())
    orchestrator.register_agent(DeveloperAgent())
    orchestrator.register_agent(ReviewerAgent())
    orchestrator.register_agent(DevOpsAgent())

    # Load workflow
    with open('workflows/ecommerce_platform.yaml', 'r') as f:
        workflow = yaml.safe_load(f)

    # Execute workflow
    result = await orchestrator.execute_workflow(workflow)

    # Generate report
    print("Workflow Execution Report")
    print("=" * 50)
    print(f"Total stages: {len(workflow['stages'])}")
    print(f"Total tasks: {len(orchestrator.completed_tasks)}")
    print(f"Success rate: {calculate_success_rate(result)}%")
    print("\nArtifacts created:")
    for artifact in result['artifacts']:
        print(f"  - {artifact}")

    return result

# Run the workflow
if __name__ == "__main__":
    asyncio.run(build_ecommerce_platform())
```

## Communication

### Agent Communication Patterns

#### Step 1: Event-Driven Communication

```python
# communication/event_bus.py
class EventBus:
    """Central event bus for agent communication"""

    def __init__(self):
        self.subscribers = {}
        self.event_log = []

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    async def publish(self, event: Dict[str, Any]):
        """Publish an event to all subscribers"""
        event_type = event['type']
        self.event_log.append(event)

        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                asyncio.create_task(handler(event))

# communication/messages.py
class MessageProtocol:
    """Define message protocols for agent communication"""

    @staticmethod
    def create_request(
        from_agent: str,
        to_agent: str,
        request_type: str,
        data: Any
    ) -> Dict:
        """Create a request message"""
        return {
            'id': str(uuid.uuid4()),
            'type': 'request',
            'from': from_agent,
            'to': to_agent,
            'request_type': request_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

    @staticmethod
    def create_response(
        request_id: str,
        from_agent: str,
        status: str,
        data: Any
    ) -> Dict:
        """Create a response message"""
        return {
            'id': str(uuid.uuid4()),
            'type': 'response',
            'request_id': request_id,
            'from': from_agent,
            'status': status,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

    @staticmethod
    def create_broadcast(
        from_agent: str,
        event_type: str,
        data: Any
    ) -> Dict:
        """Create a broadcast message"""
        return {
            'id': str(uuid.uuid4()),
            'type': 'broadcast',
            'from': from_agent,
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
```

#### Step 2: Agent Negotiation

```python
# agents/negotiation.py
class NegotiationProtocol:
    """Protocol for agent negotiation and consensus"""

    async def negotiate_task_assignment(
        self,
        task: Dict,
        available_agents: List[BaseAgent]
    ) -> BaseAgent:
        """Negotiate which agent should handle a task"""

        bids = []

        # Collect bids from agents
        for agent in available_agents:
            capability_score = self.calculate_capability_score(
                task,
                agent.capabilities
            )
            workload = agent.get_current_workload()

            bid = {
                'agent': agent,
                'capability_score': capability_score,
                'availability': 1.0 - (workload / 10),  # Normalize workload
                'estimated_time': agent.estimate_task_time(task)
            }
            bids.append(bid)

        # Select best agent
        best_bid = max(
            bids,
            key=lambda x: x['capability_score'] * x['availability']
        )

        return best_bid['agent']

    async def consensus_decision(
        self,
        decision_type: str,
        agents: List[BaseAgent],
        data: Dict
    ) -> Dict:
        """Reach consensus among multiple agents"""

        votes = {}

        # Collect votes
        for agent in agents:
            vote = await agent.vote_on_decision(decision_type, data)
            votes[agent.name] = vote

        # Determine consensus
        vote_counts = {}
        for vote in votes.values():
            vote_counts[vote['choice']] = vote_counts.get(vote['choice'], 0) + 1

        # Majority wins
        consensus = max(vote_counts.items(), key=lambda x: x[1])

        return {
            'decision': consensus[0],
            'votes': votes,
            'confidence': consensus[1] / len(agents)
        }
```

## Task Distribution

### Intelligent Task Distribution System

#### Step 1: Task Queue Management

```python
# task_distribution/task_manager.py
class TaskManager:
    """Manages task distribution among agents"""

    def __init__(self):
        self.task_queue = PriorityQueue()
        self.agent_queues = {}
        self.task_history = []
        self.performance_metrics = {}

    async def distribute_tasks(self, tasks: List[Dict], agents: List[BaseAgent]):
        """Intelligently distribute tasks among agents"""

        # Analyze task dependencies
        task_graph = self.build_dependency_graph(tasks)

        # Topological sort for execution order
        execution_order = self.topological_sort(task_graph)

        for task_batch in execution_order:
            # Tasks in same batch can be parallel
            assignments = await self.assign_tasks(task_batch, agents)

            # Execute assignments
            await self.execute_assignments(assignments)

    def build_dependency_graph(self, tasks: List[Dict]) -> Dict:
        """Build task dependency graph"""
        graph = {}

        for task in tasks:
            task_id = task['id']
            dependencies = task.get('depends_on', [])
            graph[task_id] = dependencies

        return graph

    async def assign_tasks(
        self,
        tasks: List[Dict],
        agents: List[BaseAgent]
    ) -> List[Dict]:
        """Assign tasks to agents based on capabilities"""

        assignments = []

        for task in tasks:
            # Find suitable agents
            suitable_agents = self.find_suitable_agents(task, agents)

            if not suitable_agents:
                raise ValueError(f"No suitable agent for task: {task['id']}")

            # Select best agent
            selected_agent = await self.select_best_agent(
                task,
                suitable_agents
            )

            assignments.append({
                'task': task,
                'agent': selected_agent,
                'estimated_duration': selected_agent.estimate_task_time(task)
            })

            # Update agent workload
            selected_agent.add_to_workload(task)

        return assignments

    def find_suitable_agents(
        self,
        task: Dict,
        agents: List[BaseAgent]
    ) -> List[BaseAgent]:
        """Find agents capable of handling the task"""
        suitable = []

        required_capabilities = task.get('required_capabilities', [])

        for agent in agents:
            if all(cap in agent.capabilities for cap in required_capabilities):
                suitable.append(agent)

        return suitable

    async def select_best_agent(
        self,
        task: Dict,
        agents: List[BaseAgent]
    ) -> BaseAgent:
        """Select the best agent for a task"""

        scores = []

        for agent in agents:
            # Calculate score based on multiple factors
            capability_match = self.calculate_capability_match(task, agent)
            past_performance = self.get_past_performance(agent, task['type'])
            current_load = agent.get_current_workload()

            score = (
                capability_match * 0.4 +
                past_performance * 0.4 +
                (1 - current_load / 10) * 0.2
            )

            scores.append((agent, score))

        # Return agent with highest score
        return max(scores, key=lambda x: x[1])[0]
```

#### Step 2: Load Balancing

```python
# task_distribution/load_balancer.py
class LoadBalancer:
    """Load balancing for agent tasks"""

    def __init__(self):
        self.agent_loads = {}
        self.rebalance_threshold = 0.3  # 30% difference triggers rebalance

    async def monitor_and_balance(self, agents: List[BaseAgent]):
        """Monitor agent loads and rebalance if needed"""

        while True:
            # Calculate load metrics
            loads = self.calculate_loads(agents)

            # Check if rebalancing needed
            if self.needs_rebalancing(loads):
                await self.rebalance_tasks(agents)

            # Wait before next check
            await asyncio.sleep(5)

    def calculate_loads(self, agents: List[BaseAgent]) -> Dict:
        """Calculate current load for each agent"""
        loads = {}

        for agent in agents:
            loads[agent.name] = {
                'task_count': len(agent.current_tasks),
                'estimated_time': sum(t['estimated_time'] for t in agent.current_tasks),
                'cpu_usage': agent.get_cpu_usage(),
                'memory_usage': agent.get_memory_usage()
            }

        return loads

    def needs_rebalancing(self, loads: Dict) -> bool:
        """Check if load rebalancing is needed"""
        if not loads:
            return False

        task_counts = [l['task_count'] for l in loads.values()]
        max_tasks = max(task_counts)
        min_tasks = min(task_counts)

        if max_tasks == 0:
            return False

        imbalance = (max_tasks - min_tasks) / max_tasks

        return imbalance > self.rebalance_threshold

    async def rebalance_tasks(self, agents: List[BaseAgent]):
        """Rebalance tasks among agents"""

        # Find overloaded and underloaded agents
        overloaded = []
        underloaded = []
        avg_load = self.calculate_average_load(agents)

        for agent in agents:
            load = len(agent.current_tasks)
            if load > avg_load * 1.2:
                overloaded.append(agent)
            elif load < avg_load * 0.8:
                underloaded.append(agent)

        # Move tasks from overloaded to underloaded
        for source in overloaded:
            for target in underloaded:
                # Find transferable task
                task = self.find_transferable_task(source, target)

                if task:
                    await self.transfer_task(task, source, target)
                    print(f"Transferred task {task['id']} from {source.name} to {target.name}")
```

## Complete System

### Full Multi-Agent System Example

#### Step 1: System Configuration

```yaml
# config/multi_agent_system.yaml
system:
  name: "Enterprise Development Platform"
  version: "1.0.0"
  mode: "production"

agents:
  - id: research-1
    type: research
    instances: 2
    capabilities:
      - web_research
      - documentation_analysis
      - pattern_extraction
      - knowledge_synthesis

  - id: architect-1
    type: architect
    instances: 1
    capabilities:
      - system_design
      - database_modeling
      - api_specification
      - architecture_validation

  - id: developer-1
    type: developer
    instances: 3
    capabilities:
      - backend_development
      - frontend_development
      - api_implementation
      - database_implementation

  - id: tester-1
    type: tester
    instances: 2
    capabilities:
      - unit_testing
      - integration_testing
      - e2e_testing
      - performance_testing

  - id: reviewer-1
    type: reviewer
    instances: 1
    capabilities:
      - code_review
      - security_audit
      - performance_analysis
      - compliance_check

  - id: devops-1
    type: devops
    instances: 1
    capabilities:
      - ci_cd_setup
      - containerization
      - kubernetes_deployment
      - monitoring_setup

communication:
  protocol: async_messaging
  broker: redis
  channels:
    - research
    - development
    - testing
    - deployment
    - monitoring

workflows:
  - name: feature_development
    stages:
      - research
      - design
      - implementation
      - testing
      - review
      - deployment

monitoring:
  metrics:
    - task_completion_rate
    - agent_utilization
    - error_rate
    - response_time
  alerts:
    - type: agent_failure
      threshold: 1
      action: restart_agent
    - type: task_timeout
      threshold: 3600
      action: reassign_task
```

#### Step 2: Complete Implementation

```python
# multi_agent_system.py
import asyncio
import yaml
from typing import Dict, List, Any
from agents import AgentFactory
from coordinator import AgentOrchestrator
from monitoring import SystemMonitor
from communication import EventBus

class MultiAgentSystem:
    """Complete multi-agent system implementation"""

    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.orchestrator = AgentOrchestrator()
        self.event_bus = EventBus()
        self.monitor = SystemMonitor()
        self.agents = {}
        self.initialize_system()

    def load_config(self, config_path: str) -> Dict:
        """Load system configuration"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def initialize_system(self):
        """Initialize all system components"""

        # Create agents from configuration
        for agent_config in self.config['agents']:
            for i in range(agent_config['instances']):
                agent = AgentFactory.create(
                    agent_type=agent_config['type'],
                    agent_id=f"{agent_config['id']}-{i}",
                    capabilities=agent_config['capabilities']
                )
                self.register_agent(agent)

        # Setup communication channels
        for channel in self.config['communication']['channels']:
            self.event_bus.create_channel(channel)

        # Initialize monitoring
        self.monitor.setup_metrics(self.config['monitoring']['metrics'])
        self.monitor.setup_alerts(self.config['monitoring']['alerts'])

    def register_agent(self, agent: BaseAgent):
        """Register an agent in the system"""
        self.agents[agent.id] = agent
        self.orchestrator.register_agent(agent)
        agent.event_bus = self.event_bus
        agent.monitor = self.monitor

    async def execute_project(self, project: Dict[str, Any]):
        """Execute a complete project using multi-agent system"""

        print(f"Starting project: {project['name']}")
        print(f"Description: {project['description']}")
        print(f"Requirements: {len(project['requirements'])} items")
        print("-" * 50)

        # Phase 1: Research and Planning
        research_results = await self.execute_research_phase(project)

        # Phase 2: Architecture Design
        architecture = await self.execute_design_phase(
            project,
            research_results
        )

        # Phase 3: Implementation
        implementation = await self.execute_implementation_phase(
            architecture,
            project['requirements']
        )

        # Phase 4: Testing
        test_results = await self.execute_testing_phase(implementation)

        # Phase 5: Review and Quality Assurance
        review_results = await self.execute_review_phase(
            implementation,
            test_results
        )

        # Phase 6: Deployment
        deployment = await self.execute_deployment_phase(
            implementation,
            review_results
        )

        # Generate final report
        report = self.generate_project_report(
            project,
            research_results,
            architecture,
            implementation,
            test_results,
            review_results,
            deployment
        )

        return report

    async def execute_research_phase(self, project: Dict) -> Dict:
        """Execute research phase with multiple research agents"""

        research_tasks = []

        # Create research tasks for each requirement area
        for requirement in project['requirements']:
            task = {
                'type': 'research',
                'topic': requirement['description'],
                'context': requirement.get('context', {}),
                'priority': requirement.get('priority', 'medium')
            }
            research_tasks.append(task)

        # Distribute research tasks among research agents
        research_agents = self.get_agents_by_type('research')
        results = await self.orchestrator.execute_parallel_tasks(
            research_tasks,
            research_agents
        )

        # Synthesize research results
        synthesis = await self.synthesize_research(results)

        return synthesis

    async def execute_design_phase(
        self,
        project: Dict,
        research: Dict
    ) -> Dict:
        """Execute architecture design phase"""

        architect = self.get_agents_by_type('architect')[0]

        design_task = {
            'type': 'design',
            'project': project,
            'research': research,
            'constraints': project.get('constraints', []),
            'quality_attributes': project.get('quality_attributes', [])
        }

        architecture = await architect.process_task(design_task)

        # Validate architecture
        validation = await self.validate_architecture(architecture)

        if not validation['valid']:
            # Request revision
            architecture = await self.revise_architecture(
                architecture,
                validation['issues']
            )

        return architecture

    async def execute_implementation_phase(
        self,
        architecture: Dict,
        requirements: List[Dict]
    ) -> Dict:
        """Execute implementation phase with multiple developers"""

        # Break down into implementation tasks
        impl_tasks = self.create_implementation_tasks(
            architecture,
            requirements
        )

        # Distribute among developer agents
        developer_agents = self.get_agents_by_type('developer')

        # Execute tasks with dependency management
        implementation = await self.orchestrator.execute_workflow({
            'name': 'implementation',
            'tasks': impl_tasks,
            'agents': developer_agents,
            'parallel': True
        })

        return implementation

    async def execute_testing_phase(self, implementation: Dict) -> Dict:
        """Execute comprehensive testing phase"""

        test_types = ['unit', 'integration', 'e2e', 'performance']
        test_results = {}

        tester_agents = self.get_agents_by_type('tester')

        for test_type in test_types:
            task = {
                'type': 'test',
                'test_type': test_type,
                'implementation': implementation,
                'coverage_threshold': 0.8
            }

            # Assign to available tester
            tester = await self.orchestrator.select_agent(
                task,
                tester_agents
            )

            result = await tester.process_task(task)
            test_results[test_type] = result

        return test_results

    async def execute_review_phase(
        self,
        implementation: Dict,
        test_results: Dict
    ) -> Dict:
        """Execute code review and quality assurance"""

        reviewer = self.get_agents_by_type('reviewer')[0]

        review_task = {
            'type': 'review',
            'implementation': implementation,
            'test_results': test_results,
            'criteria': [
                'code_quality',
                'security',
                'performance',
                'maintainability',
                'documentation'
            ]
        }

        review_results = await reviewer.process_task(review_task)

        # Handle review feedback
        if review_results['issues']:
            # Create fix tasks for developers
            fix_tasks = self.create_fix_tasks(review_results['issues'])

            # Execute fixes
            await self.execute_fixes(fix_tasks)

            # Re-review
            review_results = await reviewer.process_task(review_task)

        return review_results

    async def execute_deployment_phase(
        self,
        implementation: Dict,
        review_results: Dict
    ) -> Dict:
        """Execute deployment phase"""

        devops = self.get_agents_by_type('devops')[0]

        deployment_task = {
            'type': 'deploy',
            'implementation': implementation,
            'review_approval': review_results['approved'],
            'environment': 'staging',
            'strategy': 'blue-green',
            'monitoring': True
        }

        deployment = await devops.process_task(deployment_task)

        # Run smoke tests
        smoke_test = await self.run_smoke_tests(deployment)

        if smoke_test['passed']:
            # Deploy to production
            deployment_task['environment'] = 'production'
            deployment = await devops.process_task(deployment_task)

        return deployment

    def generate_project_report(self, **kwargs) -> Dict:
        """Generate comprehensive project report"""

        report = {
            'project': kwargs['project'],
            'summary': {
                'duration': self.calculate_duration(),
                'agents_used': len(self.agents),
                'tasks_completed': self.orchestrator.get_completed_task_count(),
                'success_rate': self.calculate_success_rate()
            },
            'phases': {
                'research': kwargs['research_results'],
                'architecture': kwargs['architecture'],
                'implementation': kwargs['implementation'],
                'testing': kwargs['test_results'],
                'review': kwargs['review_results'],
                'deployment': kwargs['deployment']
            },
            'artifacts': self.collect_artifacts(),
            'metrics': self.monitor.get_metrics_summary(),
            'recommendations': self.generate_recommendations()
        }

        return report

# Example execution
async def main():
    """Run complete multi-agent project"""

    # Initialize system
    system = MultiAgentSystem('config/multi_agent_system.yaml')

    # Define project
    project = {
        'name': 'Customer Portal',
        'description': 'Build a customer self-service portal',
        'requirements': [
            {
                'id': 'req-001',
                'description': 'User authentication and authorization',
                'priority': 'high'
            },
            {
                'id': 'req-002',
                'description': 'Dashboard with analytics',
                'priority': 'high'
            },
            {
                'id': 'req-003',
                'description': 'Ticket management system',
                'priority': 'medium'
            },
            {
                'id': 'req-004',
                'description': 'Knowledge base integration',
                'priority': 'medium'
            },
            {
                'id': 'req-005',
                'description': 'Real-time chat support',
                'priority': 'low'
            }
        ],
        'constraints': [
            'Must integrate with existing CRM',
            'Response time < 2 seconds',
            'Support 10,000 concurrent users'
        ],
        'quality_attributes': [
            'scalability',
            'reliability',
            'security',
            'usability'
        ]
    }

    # Execute project
    report = await system.execute_project(project)

    # Print report
    print("\n" + "=" * 50)
    print("PROJECT COMPLETION REPORT")
    print("=" * 50)
    print(f"Project: {report['project']['name']}")
    print(f"Duration: {report['summary']['duration']}")
    print(f"Success Rate: {report['summary']['success_rate']}%")
    print(f"Artifacts Created: {len(report['artifacts'])}")

    # Save detailed report
    with open('project_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### Common Multi-Agent Issues and Solutions

#### Issue 1: Agent Communication Deadlock

```python
# troubleshooting/deadlock_detection.py
class DeadlockDetector:
    """Detect and resolve agent communication deadlocks"""

    def __init__(self):
        self.waiting_graph = {}
        self.detection_interval = 5  # seconds

    async def monitor_deadlocks(self, agents: List[BaseAgent]):
        """Monitor for deadlocks continuously"""

        while True:
            # Build waiting graph
            self.build_waiting_graph(agents)

            # Detect cycles (deadlocks)
            cycles = self.detect_cycles()

            if cycles:
                print(f"Deadlock detected involving agents: {cycles}")
                await self.resolve_deadlock(cycles, agents)

            await asyncio.sleep(self.detection_interval)

    def build_waiting_graph(self, agents: List[BaseAgent]):
        """Build graph of agent dependencies"""
        self.waiting_graph = {}

        for agent in agents:
            if agent.waiting_for:
                self.waiting_graph[agent.id] = agent.waiting_for

    def detect_cycles(self) -> List[List[str]]:
        """Detect cycles in waiting graph"""
        cycles = []
        visited = set()
        rec_stack = set()

        for node in self.waiting_graph:
            if node not in visited:
                if self.detect_cycle_util(node, visited, rec_stack):
                    cycles.append(self.get_cycle(node))

        return cycles

    async def resolve_deadlock(self, cycles: List[List[str]], agents: List[BaseAgent]):
        """Resolve detected deadlocks"""

        for cycle in cycles:
            # Find lowest priority task in cycle
            victim = self.select_victim(cycle, agents)

            # Cancel victim's task
            victim_agent = next(a for a in agents if a.id == victim)
            await victim_agent.cancel_current_task()

            print(f"Resolved deadlock by canceling task on agent: {victim}")
```

#### Issue 2: Agent Failure Recovery

```python
# troubleshooting/failure_recovery.py
class AgentRecovery:
    """Handle agent failures and recovery"""

    def __init__(self):
        self.failure_history = {}
        self.recovery_strategies = {
            'restart': self.restart_agent,
            'reassign': self.reassign_tasks,
            'replace': self.replace_agent
        }

    async def handle_agent_failure(self, agent: BaseAgent, error: Exception):
        """Handle agent failure with appropriate recovery"""

        # Log failure
        self.log_failure(agent, error)

        # Determine recovery strategy
        strategy = self.determine_strategy(agent, error)

        # Execute recovery
        await self.recovery_strategies[strategy](agent)

    def determine_strategy(self, agent: BaseAgent, error: Exception) -> str:
        """Determine best recovery strategy"""

        failure_count = self.get_failure_count(agent)

        if failure_count < 3:
            return 'restart'
        elif failure_count < 5:
            return 'reassign'
        else:
            return 'replace'

    async def restart_agent(self, agent: BaseAgent):
        """Restart failed agent"""
        print(f"Restarting agent: {agent.id}")

        # Save current state
        state = agent.get_state()

        # Restart agent
        await agent.shutdown()
        await agent.initialize()

        # Restore state
        agent.restore_state(state)

    async def reassign_tasks(self, agent: BaseAgent):
        """Reassign tasks from failed agent"""
        print(f"Reassigning tasks from agent: {agent.id}")

        tasks = agent.get_current_tasks()

        for task in tasks:
            # Find alternative agent
            alternative = await self.find_alternative_agent(task)

            if alternative:
                await alternative.assign_task(task)
```

## Best Practices

### Multi-Agent System Best Practices

#### 1. Agent Design Principles

```python
# best_practices/agent_design.py

# GOOD: Single Responsibility
class DataFetchAgent(BaseAgent):
    """Agent with single, clear responsibility"""
    def __init__(self):
        super().__init__("data-fetch", ["fetch", "cache"])

    async def process_task(self, task):
        if task['type'] == 'fetch':
            return await self.fetch_data(task['source'])

# BAD: Multiple Responsibilities
class DoEverythingAgent(BaseAgent):
    """Agent trying to do too much"""
    def __init__(self):
        super().__init__("everything", ["fetch", "process", "store", "analyze"])
    # Too complex, hard to maintain
```

#### 2. Communication Patterns

```yaml
# best_practices/communication.yaml
patterns:
  request-response:
    use_when: "Need synchronous, guaranteed response"
    example: "API call, database query"

  publish-subscribe:
    use_when: "Multiple agents need notification"
    example: "Status updates, event notifications"

  message-queue:
    use_when: "Asynchronous, guaranteed delivery"
    example: "Task distribution, work items"

  direct-messaging:
    use_when: "Point-to-point communication"
    example: "Agent negotiation, private data"
```

#### 3. Error Handling

```python
# best_practices/error_handling.py

class RobustAgent(BaseAgent):
    """Agent with comprehensive error handling"""

    async def process_task_safely(self, task):
        """Process task with full error handling"""
        try:
            # Validate input
            self.validate_task(task)

            # Process with timeout
            result = await asyncio.wait_for(
                self.process_task(task),
                timeout=task.get('timeout', 300)
            )

            # Validate output
            self.validate_result(result)

            return result

        except asyncio.TimeoutError:
            # Handle timeout
            await self.handle_timeout(task)
            raise

        except ValidationError as e:
            # Handle validation errors
            await self.handle_validation_error(task, e)
            raise

        except Exception as e:
            # Handle unexpected errors
            await self.handle_unexpected_error(task, e)
            raise
        finally:
            # Cleanup
            await self.cleanup(task)
```

#### 4. Performance Optimization

```python
# best_practices/performance.py

class OptimizedOrchestrator:
    """Orchestrator with performance optimizations"""

    def __init__(self):
        self.task_cache = {}
        self.result_cache = TTLCache(maxsize=100, ttl=300)

    async def execute_with_caching(self, task):
        """Execute task with result caching"""
        cache_key = self.generate_cache_key(task)

        # Check cache
        if cache_key in self.result_cache:
            return self.result_cache[cache_key]

        # Execute task
        result = await self.execute_task(task)

        # Cache result
        self.result_cache[cache_key] = result

        return result

    async def batch_similar_tasks(self, tasks):
        """Batch similar tasks for efficiency"""
        batches = {}

        for task in tasks:
            task_type = task['type']
            if task_type not in batches:
                batches[task_type] = []
            batches[task_type].append(task)

        results = []
        for task_type, batch in batches.items():
            # Process batch together
            batch_results = await self.process_batch(batch)
            results.extend(batch_results)

        return results
```

## Summary

This comprehensive multi-agent coordination guide demonstrates:

1. **Architecture**: Complete system design and implementation
2. **Basic Coordination**: Two-agent collaboration patterns
3. **Complex Workflows**: Four+ agent orchestration
4. **Communication**: Event-driven and message-passing patterns
5. **Task Distribution**: Intelligent work allocation
6. **Complete System**: Production-ready implementation
7. **Troubleshooting**: Common issues and solutions
8. **Best Practices**: Design principles and patterns

The multi-agent system enables:
- Parallel task execution
- Complex problem decomposition
- Scalable development workflows
- Intelligent task distribution
- Robust error handling
- Comprehensive monitoring

Use these patterns to build sophisticated multi-agent systems with the Claude Code Context Engineering system.
