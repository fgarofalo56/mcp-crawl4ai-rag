#!/usr/bin/env python
"""
Test script to verify the MCP server wrapper and configuration.
Run this to check if your environment is properly set up.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_environment():
    """Test if environment is properly configured"""
    
    print("=" * 60)
    print("Crawl4AI RAG MCP Server - Environment Test")
    print("=" * 60)
    
    # Load .env file
    project_root = Path(__file__).resolve().parent
    env_path = project_root / ".env"
    
    if env_path.exists():
        print(f"✓ Found .env file at: {env_path}")
        load_dotenv(env_path, override=True)
    else:
        print(f"✗ No .env file found at: {env_path}")
        print("  Please create one from .env.example")
        return False
    
    # Check required environment variables
    print("\nChecking required environment variables:")
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API Key",
        "SUPABASE_URL": "Supabase URL",
        "SUPABASE_SERVICE_KEY": "Supabase Service Key",
    }
    
    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask the value for security
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✓ {description} ({var}): {masked_value}")
        else:
            print(f"  ✗ {description} ({var}): Not set")
            all_present = False
    
    # Check optional configuration
    print("\nOptional RAG strategies:")
    optional_vars = {
        "USE_CONTEXTUAL_EMBEDDINGS": "Contextual Embeddings",
        "USE_HYBRID_SEARCH": "Hybrid Search",
        "USE_AGENTIC_RAG": "Agentic RAG",
        "USE_RERANKING": "Reranking",
        "USE_KNOWLEDGE_GRAPH": "Knowledge Graph",
    }
    
    for var, description in optional_vars.items():
        value = os.getenv(var, "false")
        status = "✓ Enabled" if value.lower() == "true" else "○ Disabled"
        print(f"  {status}: {description}")
    
    # Check transport mode
    print("\nTransport configuration:")
    transport = os.getenv("TRANSPORT", "sse")
    print(f"  Transport mode: {transport}")
    
    if transport == "sse":
        host = os.getenv("HOST", "0.0.0.0")
        port = os.getenv("PORT", "8051")
        print(f"  Host: {host}")
        print(f"  Port: {port}")
    elif transport == "stdio":
        print("  Using stdio for Claude Desktop")
    
    # Check imports
    print("\nChecking Python imports:")
    try:
        import crawl4ai
        print("  ✓ crawl4ai")
    except ImportError:
        print("  ✗ crawl4ai - Run: uv pip install -e .")
        all_present = False
    
    try:
        import supabase
        print("  ✓ supabase")
    except ImportError:
        print("  ✗ supabase - Run: uv pip install -e .")
        all_present = False
    
    try:
        import openai
        print("  ✓ openai")
    except ImportError:
        print("  ✗ openai - Run: uv pip install -e .")
        all_present = False
    
    try:
        import fastmcp
        print("  ✓ fastmcp")
    except ImportError:
        print("  ✗ fastmcp - Run: uv pip install -e .")
        all_present = False
    
    # Check if knowledge graph is enabled and Neo4j is configured
    if os.getenv("USE_KNOWLEDGE_GRAPH", "false").lower() == "true":
        print("\nKnowledge Graph configuration:")
        neo4j_vars = {
            "NEO4J_URI": "Neo4j URI",
            "NEO4J_USER": "Neo4j User",
            "NEO4J_PASSWORD": "Neo4j Password",
        }
        
        neo4j_configured = True
        for var, description in neo4j_vars.items():
            value = os.getenv(var)
            if value:
                masked_value = value[:8] + "..." if len(value) > 8 and var == "NEO4J_PASSWORD" else value
                print(f"  ✓ {description}: {masked_value}")
            else:
                print(f"  ✗ {description}: Not set")
                neo4j_configured = False
        
        if neo4j_configured:
            try:
                import neo4j
                print("  ✓ neo4j package installed")
            except ImportError:
                print("  ✗ neo4j package - Run: uv pip install -e .")
                all_present = False
    
    print("\n" + "=" * 60)
    if all_present:
        print("✓ Environment is properly configured!")
        print("\nYou can now run the server with:")
        print("  python run_mcp.py")
        print("  or")
        print("  ./run_mcp.sh (Mac/Linux)")
        print("  or")
        print("  run_mcp.bat (Windows)")
        return True
    else:
        print("✗ Some configuration issues found.")
        print("Please fix the issues above and try again.")
        return False

if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)
