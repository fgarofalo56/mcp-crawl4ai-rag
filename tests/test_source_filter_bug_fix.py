"""
Simple verification tests for source_filter parameter bug fix.

Bug Reference: Task-011 - Parameter naming inconsistency fix
"""

import inspect

import pytest


class TestSourceFilterBugFix:
    """Verify the source_filter parameter bug is fixed."""

    def test_perform_rag_query_has_source_filter_parameter(self):
        """Test that perform_rag_query function signature has 'source_filter' parameter."""
        # Import the MCP tool and get the underlying function
        from src.tools.rag_tools import perform_rag_query

        # Get the underlying function from the FunctionTool
        if hasattr(perform_rag_query, "fn"):
            actual_function = perform_rag_query.fn
        else:
            actual_function = perform_rag_query

        sig = inspect.signature(actual_function)
        params = list(sig.parameters.keys())

        # Verify 'source_filter' is in parameters
        assert "source_filter" in params, (
            "Function signature should have 'source_filter' parameter. "
            f"Found parameters: {params}"
        )

        # Verify 'source' is NOT in parameters (old bug)
        assert "source" not in params, (
            "Function signature should NOT have 'source' parameter (this was the bug). "
            f"Found parameters: {params}"
        )

    def test_perform_rag_query_source_filter_default_value(self):
        """Test that source_filter has correct default value of None."""
        from src.tools.rag_tools import perform_rag_query

        # Get the underlying function
        if hasattr(perform_rag_query, "fn"):
            actual_function = perform_rag_query.fn
        else:
            actual_function = perform_rag_query

        sig = inspect.signature(actual_function)
        source_filter_param = sig.parameters["source_filter"]

        assert (
            source_filter_param.default is None
        ), f"source_filter should default to None, got {source_filter_param.default}"

    def test_perform_rag_query_parameters_order(self):
        """Test that parameters are in expected order."""
        from src.tools.rag_tools import perform_rag_query

        # Get the underlying function
        if hasattr(perform_rag_query, "fn"):
            actual_function = perform_rag_query.fn
        else:
            actual_function = perform_rag_query

        sig = inspect.signature(actual_function)
        params = list(sig.parameters.keys())

        # Expected order: ctx, query, source_filter, match_count
        expected_params = ["ctx", "query", "source_filter", "match_count"]
        assert (
            params == expected_params
        ), f"Parameters should be in order {expected_params}, got {params}"

    def test_docstring_updated_with_source_filter(self):
        """Test that docstring mentions source_filter not source."""
        from src.tools.rag_tools import perform_rag_query

        # Get the underlying function
        if hasattr(perform_rag_query, "fn"):
            actual_function = perform_rag_query.fn
        else:
            actual_function = perform_rag_query

        docstring = actual_function.__doc__

        assert docstring is not None, "Function should have a docstring"

        # Check that source_filter is mentioned in docstring
        assert "source_filter" in docstring, "Docstring should mention 'source_filter' parameter"

        # Check that it's not using old 'source:' parameter documentation
        # (we check for "source:" with colon to avoid false positives from "source" as a word)
        lines = docstring.split("\n")
        param_lines = [line for line in lines if ":" in line and "source" in line.lower()]

        for line in param_lines:
            if ": " in line:  # Parameter documentation line
                assert (
                    "source_filter:" in line.lower()
                ), f"Parameter documentation should use 'source_filter:', not 'source:'. Found: {line}"


class TestGraphRAGQueryConsistency:
    """Verify consistency with graphrag_query tool."""

    def test_graphrag_query_uses_source_filter(self):
        """Test that graphrag_query uses source_filter parameter."""
        from src.tools.graphrag_tools import graphrag_query

        # Get the underlying function
        actual_function = graphrag_query.fn if hasattr(graphrag_query, "fn") else graphrag_query

        sig = inspect.signature(actual_function)
        params = list(sig.parameters.keys())

        # Verify graphrag_query uses source_filter
        assert (
            "source_filter" in params
        ), "graphrag_query should use 'source_filter' parameter for consistency"

    def test_both_tools_use_same_parameter_name(self):
        """Test that both perform_rag_query and graphrag_query use same parameter name."""
        from src.tools.graphrag_tools import graphrag_query
        from src.tools.rag_tools import perform_rag_query

        # Get underlying functions
        perform_rag_fn = (
            perform_rag_query.fn if hasattr(perform_rag_query, "fn") else perform_rag_query
        )
        graphrag_fn = graphrag_query.fn if hasattr(graphrag_query, "fn") else graphrag_query

        perform_rag_params = list(inspect.signature(perform_rag_fn).parameters.keys())
        graphrag_params = list(inspect.signature(graphrag_fn).parameters.keys())

        # Both should have source_filter
        assert "source_filter" in perform_rag_params, "perform_rag_query should have source_filter"
        assert "source_filter" in graphrag_params, "graphrag_query should have source_filter"

        # Neither should have 'source'
        assert "source" not in perform_rag_params, "perform_rag_query should not have 'source'"
        # graphrag_query doesn't need this check as it was already correct


@pytest.mark.unit
class TestBugFixValidation:
    """Unit tests to validate the specific bug is fixed."""

    def test_validation_error_should_not_occur(self):
        """
        Test that the ValidationError from the bug report should not occur.

        Original error:
            ValidationError: 1 validation error for call[perform_rag_query]
            source_filter
              Unexpected keyword argument
        """
        from src.tools.rag_tools import perform_rag_query

        # Get underlying function
        if hasattr(perform_rag_query, "fn"):
            actual_function = perform_rag_query.fn
        else:
            actual_function = perform_rag_query

        sig = inspect.signature(actual_function)

        # The bug was that 'source_filter' was not in the function signature
        # This caused Pydantic validation to fail when FastMCP tried to validate arguments
        assert "source_filter" in sig.parameters, (
            "The fix requires 'source_filter' to be in function parameters "
            "to prevent Pydantic ValidationError"
        )

    def test_old_parameter_name_removed(self):
        """Test that the old incorrect parameter name 'source' is removed."""
        from src.tools.rag_tools import perform_rag_query

        # Get underlying function
        if hasattr(perform_rag_query, "fn"):
            actual_function = perform_rag_query.fn
        else:
            actual_function = perform_rag_query

        sig = inspect.signature(actual_function)

        assert (
            "source" not in sig.parameters
        ), "Old parameter name 'source' should be renamed to 'source_filter'"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
