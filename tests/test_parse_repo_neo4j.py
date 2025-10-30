"""
Comprehensive tests for parse_repo_into_neo4j module.
"""

import ast
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import is set up in conftest.py
try:
    from parse_repo_into_neo4j import DirectNeo4jExtractor, Neo4jCodeAnalyzer
except ModuleNotFoundError:
    pytest.skip("Neo4j dependencies not available", allow_module_level=True)


class TestNeo4jCodeAnalyzer:
    """Test Neo4jCodeAnalyzer AST parsing."""

    def setup_method(self):
        self.analyzer = Neo4jCodeAnalyzer()

    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        assert self.analyzer is not None
        assert isinstance(self.analyzer.external_modules, set)
        assert "os" in self.analyzer.external_modules

    def test_get_name_simple(self):
        """Test _get_name with ast.Name node."""
        node = ast.Name(id="TestName")
        result = self.analyzer._get_name(node)
        assert result == "TestName"

    def test_get_name_none(self):
        """Test _get_name with None."""
        result = self.analyzer._get_name(None)
        assert result == "Any"

    def test_get_name_attribute(self):
        """Test _get_name with ast.Attribute."""
        value_node = ast.Name(id="module")
        attr_node = ast.Attribute(value=value_node, attr="Class")
        result = self.analyzer._get_name(attr_node)
        assert result == "module.Class"

    def test_get_default_value_constant(self):
        """Test _get_default_value with constant."""
        const_node = ast.Constant(value=42)
        result = self.analyzer._get_default_value(const_node)
        assert result == "42"

    def test_get_default_value_list(self):
        """Test _get_default_value with empty list."""
        list_node = ast.List(elts=[])
        result = self.analyzer._get_default_value(list_node)
        assert result == "[]"

    def test_get_default_value_dict(self):
        """Test _get_default_value with empty dict."""
        dict_node = ast.Dict(keys=[], values=[])
        result = self.analyzer._get_default_value(dict_node)
        assert result == "{}"

    def test_extract_function_parameters_simple(self):
        """Test parameter extraction with simple args."""
        code = "def test_func(a: int, b: str): pass"
        tree = ast.parse(code)
        func_node = tree.body[0]
        params = self.analyzer._extract_function_parameters(func_node)
        assert len(params) == 2
        assert params[0]["name"] == "a"
        assert params[0]["type"] == "int"

    def test_extract_function_parameters_defaults(self):
        """Test parameter extraction with defaults."""
        code = "def test_func(a: int, b: str = 'default'): pass"
        tree = ast.parse(code)
        func_node = tree.body[0]
        params = self.analyzer._extract_function_parameters(func_node)
        assert params[1]["optional"] is True

    def test_is_likely_internal_relative(self):
        """Test internal import detection for relative imports."""
        assert self.analyzer._is_likely_internal(".module", set()) is True

    def test_is_likely_internal_external(self):
        """Test internal import detection for known external."""
        assert self.analyzer._is_likely_internal("os", set()) is False
        assert self.analyzer._is_likely_internal("requests", set()) is False

    def test_analyze_python_file_simple(self, tmp_path):
        """Test analyze_python_file with simple function."""
        test_file = tmp_path / "test_module.py"
        test_file.write_text("def greet(name: str) -> str: return name")
        result = self.analyzer.analyze_python_file(test_file, tmp_path, set())
        assert result is not None
        assert result["module_name"] == "test_module"
        assert len(result["functions"]) == 1

    def test_analyze_python_file_with_class(self, tmp_path):
        """Test analyze_python_file with class."""
        test_file = tmp_path / "test_module.py"
        test_file.write_text("class Person:\\n    name: str\\n    def greet(self): pass")
        result = self.analyzer.analyze_python_file(test_file, tmp_path, set())
        assert result is not None
        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "Person"

    def test_analyze_python_file_syntax_error(self, tmp_path):
        """Test analyze_python_file handles syntax errors."""
        test_file = tmp_path / "bad.py"
        test_file.write_text("def bad(:")
        result = self.analyzer.analyze_python_file(test_file, tmp_path, set())
        assert result is None


class TestDirectNeo4jExtractor:
    """Test DirectNeo4jExtractor Neo4j operations."""

    def test_extractor_initialization(self):
        """Test extractor initializes correctly."""
        extractor = DirectNeo4jExtractor("bolt://localhost:7687", "neo4j", "password")
        assert extractor.neo4j_uri == "bolt://localhost:7687"
        assert extractor.neo4j_user == "neo4j"
        assert extractor.driver is None

    def test_get_python_files(self, tmp_path):
        """Test get_python_files finds Python files."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "module.py").touch()
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.py").touch()
        extractor = DirectNeo4jExtractor("bolt://localhost:7687", "neo4j", "password")
        python_files = extractor.get_python_files(str(tmp_path))
        assert len(python_files) == 1  # Excludes tests
        assert python_files[0].name == "module.py"

    def test_get_python_files_excludes_dirs(self, tmp_path):
        """Test get_python_files excludes specified dirs."""
        (tmp_path / "venv").mkdir()
        (tmp_path / "venv" / "lib.py").touch()
        extractor = DirectNeo4jExtractor("bolt://localhost:7687", "neo4j", "password")
        python_files = extractor.get_python_files(str(tmp_path))
        assert len(python_files) == 0
