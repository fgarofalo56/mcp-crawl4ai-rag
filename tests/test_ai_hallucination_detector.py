"""
Comprehensive tests for ai_hallucination_detector module.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "knowledge_graphs"))

from ai_hallucination_detector import AIHallucinationDetector


class TestAIHallucinationDetector:
    """Test AIHallucinationDetector orchestration."""

    def test_detector_initialization(self):
        """Test detector initializes correctly."""
        detector = AIHallucinationDetector("bolt://localhost:7687", "neo4j", "password")
        assert detector is not None
        assert detector.validator is not None
        assert detector.reporter is not None

    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test initialize method."""
        detector = AIHallucinationDetector("bolt://localhost:7687", "neo4j", "password")
        detector.validator.initialize = AsyncMock()
        await detector.initialize()
        detector.validator.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self):
        """Test close method."""
        detector = AIHallucinationDetector("bolt://localhost:7687", "neo4j", "password")
        detector.validator.close = AsyncMock()
        await detector.close()
        detector.validator.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_detect_file_not_found(self):
        """Test with non-existent file."""
        detector = AIHallucinationDetector("bolt://localhost:7687", "neo4j", "password")
        with pytest.raises(FileNotFoundError):
            await detector.detect_hallucinations("/nonexistent.py")

    @pytest.mark.asyncio
    async def test_detect_invalid_extension(self):
        """Test with non-Python file."""
        detector = AIHallucinationDetector("bolt://localhost:7687", "neo4j", "password")
        with pytest.raises(ValueError, match="Python"):
            await detector.detect_hallucinations("file.txt")

    @pytest.mark.asyncio
    async def test_detect_success(self, tmp_path):
        """Test successful detection."""
        script = tmp_path / "test.py"
        script.write_text("def test(): pass")

        detector = AIHallucinationDetector("bolt://localhost:7687", "neo4j", "password")

        mock_analysis = Mock(
            imports=[],
            class_instantiations=[],
            method_calls=[],
            function_calls=[],
            attribute_accesses=[],
            errors=[],
        )
        detector.analyzer.analyze_script = Mock(return_value=mock_analysis)

        mock_validation = Mock(overall_confidence=0.9)
        detector.validator.validate_script = AsyncMock(return_value=mock_validation)

        mock_report = {
            "validation_summary": {"overall_confidence": 0.9},
            "hallucinations_detected": [],
        }
        detector.reporter.generate_comprehensive_report = Mock(return_value=mock_report)
        detector.reporter.save_json_report = Mock()
        detector.reporter.save_markdown_report = Mock()
        detector.reporter.print_summary = Mock()

        result = await detector.detect_hallucinations(str(script), print_summary=False)
        assert result is not None

    @pytest.mark.asyncio
    async def test_batch_detect(self, tmp_path):
        """Test batch detection."""
        script1 = tmp_path / "s1.py"
        script1.write_text("def f1(): pass")
        script2 = tmp_path / "s2.py"
        script2.write_text("def f2(): pass")

        detector = AIHallucinationDetector("bolt://localhost:7687", "neo4j", "password")

        mock_report = {
            "validation_summary": {
                "total_validations": 5,
                "valid_count": 4,
                "invalid_count": 1,
                "not_found_count": 0,
                "overall_confidence": 0.8,
            },
            "hallucinations_detected": [],
            "analysis_metadata": {"script_path": str(script1)},
        }
        detector.detect_hallucinations = AsyncMock(return_value=mock_report)
        detector._print_batch_summary = Mock()

        results = await detector.batch_detect([str(script1), str(script2)])
        assert len(results) == 2
