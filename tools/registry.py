"""
Tool Registry

Defines and handles MCP tools.
"""

from typing import Dict, Any, List
from context.analyzer import ProjectAnalyzer
from storage.db import Database
from analyzers.git_analyzer import GitAnalyzer

class ToolRegistry:
    def __init__(self, analyzer: ProjectAnalyzer, db: Database, git_analyzer: GitAnalyzer):
        self.analyzer = analyzer
        self.db = db
        self.git_analyzer = git_analyzer

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools."""
        return [
            {
                "name": "get_project_overview",
                "description": "Get an overview of the project structure and statistics",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "search_codebase",
                "description": "Search for functions and code patterns in the codebase",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (function name, keyword, etc.)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_function_context",
                "description": "Get detailed information about a specific function",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "function_name": {
                            "type": "string",
                            "description": "Name of the function to analyze"
                        }
                    },
                    "required": ["function_name"]
                }
            },
            {
                "name": "explain_recent_changes",
                "description": "Explain recent changes and commit history",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Optional file path to focus on"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of commits to include",
                            "default": 10
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "find_related_files",
                "description": "Find files related to a given file based on dependencies",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to find relations for"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        ]

    async def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool."""
        if name == "get_project_overview":
            return self._get_project_overview()
        elif name == "search_codebase":
            return self._search_codebase(args.get("query", ""))
        elif name == "get_function_context":
            return self._get_function_context(args.get("function_name", ""))
        elif name == "explain_recent_changes":
            return self._explain_recent_changes(
                args.get("file_path"),
                args.get("limit", 10)
            )
        elif name == "find_related_files":
            return self._find_related_files(args.get("file_path", ""))
        else:
            raise ValueError(f"Unknown tool: {name}")

    def _get_project_overview(self) -> Dict[str, Any]:
        """Get project overview."""
        overview = self.db.get_project_overview()
        return {
            "overview": overview,
            "description": f"This project contains {overview['file_count']} files with {overview['total_lines']} lines of code and {overview['function_count']} functions."
        }

    def _search_codebase(self, query: str) -> Dict[str, Any]:
        """Search codebase."""
        if not query:
            return {"results": [], "message": "No search query provided"}

        functions = self.db.search_functions(query)
        return {
            "results": functions,
            "count": len(functions),
            "query": query
        }

    def _get_function_context(self, func_name: str) -> Dict[str, Any]:
        """Get function context."""
        if not func_name:
            return {"error": "Function name required"}

        context = self.db.get_function_context(func_name)
        if not context:
            return {"error": f"Function '{func_name}' not found"}

        return {
            "function": context,
            "related_files": self.db.find_related_files(context["file"])
        }

    def _explain_recent_changes(self, file_path: str = None, limit: int = 10) -> Dict[str, Any]:
        """Explain recent changes."""
        commits = self.git_analyzer.get_recent_commits(limit)

        if file_path:
            file_history = self.git_analyzer.get_file_history(file_path, limit)
            explanation = self.git_analyzer.explain_changes(file_path)
            return {
                "commits": commits,
                "file_history": file_history,
                "file_explanation": explanation
            }
        else:
            return {
                "commits": commits,
                "summary": f"Recent {len(commits)} commits across the project"
            }

    def _find_related_files(self, file_path: str) -> Dict[str, Any]:
        """Find related files."""
        if not file_path:
            return {"error": "File path required"}

        related = self.db.find_related_files(file_path)
        return {
            "file_path": file_path,
            "related_files": related,
            "count": len(related)
        }