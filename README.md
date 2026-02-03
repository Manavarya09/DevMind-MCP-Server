# DevMind MCP

An MCP (Model Context Protocol) server that provides deep, structured project context to AI models, enabling them to understand your codebase like a senior developer teammate.

## What is DevMind MCP?

DevMind MCP analyzes your codebase and git history to provide AI models with comprehensive context about:
- Project structure and organization
- Function definitions and relationships
- Code dependencies and imports
- Recent changes and development intent
- TODO items and technical debt
- File relationships and dependencies

This allows AI assistants to answer sophisticated questions like:
- "Why does this function exist?"
- "Where should I implement this new feature?"
- "What files are related to this bug?"
- "What's the recent development context for this code?"

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/devmind-mcp.git
cd devmind-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Navigate to your project directory:
```bash
cd /path/to/your/project
```

2. Run the MCP server:
```bash
python /path/to/devmind-mcp/server.py
```

The server will automatically index your codebase and git history on startup.

## MCP Tools

DevMind MCP exposes the following tools to AI models:

### get_project_overview
Get a high-level overview of the project structure and statistics.

**Example call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_project_overview",
    "arguments": {}
  }
}
```

**Response:**
```json
{
  "overview": {
    "file_count": 42,
    "total_size": 125000,
    "total_lines": 8500,
    "function_count": 156,
    "todos": {"TODO": 5, "FIXME": 2}
  },
  "description": "This project contains 42 files with 8500 lines of code and 156 functions."
}
```

### search_codebase
Search for functions and code patterns across the codebase.

**Example call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "search_codebase",
    "arguments": {
      "query": "authentication"
    }
  }
}
```

### get_function_context
Get detailed information about a specific function including its code, documentation, and related files.

**Example call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_function_context",
    "arguments": {
      "function_name": "validate_user"
    }
  }
}
```

### explain_recent_changes
Get recent commit history and explanations of changes.

**Example call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "explain_recent_changes",
    "arguments": {
      "file_path": "src/auth.py",
      "limit": 5
    }
  }
}
```

### find_related_files
Find files that are related to a given file based on import dependencies.

**Example call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "find_related_files",
    "arguments": {
      "file_path": "src/models/user.py"
    }
  }
}
```

## Architecture

DevMind MCP consists of several key components:

- **Server** (`server.py`): MCP protocol implementation and request handling
- **Context Analyzer** (`context/analyzer.py`): Codebase analysis using AST parsing
- **Git Analyzer** (`analyzers/git_analyzer.py`): Git history and commit analysis
- **Database** (`storage/db.py`): SQLite storage for indexed data
- **Tools** (`tools/registry.py`): MCP tool definitions and implementations

## Data Storage

The server uses SQLite to store:
- File metadata (paths, sizes, line counts)
- Function definitions and signatures
- Import dependencies between files
- TODO/FIXME comments
- Git commit history and changes

Data is indexed on server startup and updated as needed.

## Requirements

- Python 3.8+
- Git (for repository analysis)
- SQLite3 (built into Python)

## Development

To extend DevMind MCP:

1. Add new analysis features in the `analyzers/` directory
2. Define new MCP tools in `tools/registry.py`
3. Update the database schema in `storage/db.py` as needed
4. Add corresponding data extraction in `context/analyzer.py`

## Future Roadmap

- Support for additional languages (JavaScript, TypeScript, Go)
- Real-time code analysis and incremental indexing
- Integration with issue trackers (GitHub Issues, Jira)
- Code quality metrics and suggestions
- Dependency graph visualization
- Performance profiling data integration

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.