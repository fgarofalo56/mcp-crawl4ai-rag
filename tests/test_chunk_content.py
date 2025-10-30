import sys
from pathlib import Path

import pytest

pytest.importorskip("supabase")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils import chunk_content


def test_chunk_content_splits_large_paragraph():
    text = "Paragraph " + "x" * 2000
    chunks = chunk_content(text, max_chunk_size=500)
    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_chunk_content_merges_small_tail():
    text = "First paragraph." + "\n\n" + "Small tail"
    chunks = chunk_content(text, max_chunk_size=200, min_chunk_size=50)
    assert len(chunks) == 1
    assert "Small tail" in chunks[0]
