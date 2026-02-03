"""
Project Analyzer

Analyzes the codebase to extract structure, functions, dependencies, and TODOs.
"""

import os
import ast
import re
from typing import Dict, List, Set, Any
from pathlib import Path

class ProjectAnalyzer:
    def __init__(self):
        self.files: List[Dict[str, Any]] = []
        self.functions: List[Dict[str, Any]] = []
        self.dependencies: Dict[str, Set[str]] = {}
        self.todos: List[Dict[str, Any]] = []

    def index_project(self, root_path: str):
        """Index the entire project."""
        root = Path(root_path)
        for file_path in root.rglob("*.py"):
            if not self._should_ignore(file_path):
                self._analyze_file(file_path)

    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored."""
        ignore_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            ".venv",
            "venv",
            "env",
            ".env"
        ]
        return any(pattern in str(path) for pattern in ignore_patterns)

    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic file info
            file_info = {
                "path": str(file_path),
                "name": file_path.name,
                "extension": file_path.suffix,
                "size": len(content),
                "lines": len(content.splitlines())
            }
            self.files.append(file_info)

            # Parse AST for functions and dependencies
            tree = ast.parse(content, filename=str(file_path))
            self._extract_functions(tree, file_path, content)
            self._extract_dependencies(tree, file_path)
            self._extract_todos(content, file_path)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def _extract_functions(self, tree: ast.AST, file_path: Path, content: str):
        """Extract function definitions from AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "file": str(file_path),
                    "line_start": node.lineno,
                    "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node) or "",
                    "code": self._get_code_snippet(content, node.lineno, node.end_lineno)
                }
                self.functions.append(func_info)

    def _extract_dependencies(self, tree: ast.AST, file_path: Path):
        """Extract import dependencies."""
        deps = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    deps.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    deps.add(node.module.split('.')[0])

        if deps:
            self.dependencies[str(file_path)] = deps

    def _extract_todos(self, content: str, file_path: Path):
        """Extract TODO and FIXME comments."""
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            # Look for TODO, FIXME, XXX in comments
            match = re.search(r'#\s*(TODO|FIXME|XXX):\s*(.+)', line, re.IGNORECASE)
            if match:
                self.todos.append({
                    "type": match.group(1).upper(),
                    "message": match.group(2).strip(),
                    "file": str(file_path),
                    "line": i
                })

    def _get_code_snippet(self, content: str, start_line: int, end_line: int) -> str:
        """Get code snippet for a function."""
        lines = content.splitlines()
        if start_line <= len(lines) and end_line <= len(lines):
            return '\n'.join(lines[start_line-1:end_line])
        return ""

    def get_data(self) -> Dict[str, Any]:
        """Get all analyzed data."""
        return {
            "files": self.files,
            "functions": self.functions,
            "dependencies": {k: list(v) for k, v in self.dependencies.items()},
            "todos": self.todos
        }

    def search_functions(self, query: str) -> List[Dict[str, Any]]:
        """Search functions by name or content."""
        results = []
        query_lower = query.lower()
        for func in self.functions:
            if query_lower in func["name"].lower() or query_lower in func["docstring"].lower():
                results.append(func)
        return results

    def find_related_files(self, file_path: str) -> List[str]:
        """Find files related to the given file based on dependencies."""
        related = set()
        file_deps = self.dependencies.get(file_path, set())

        for other_file, deps in self.dependencies.items():
            if file_path != other_file:
                # Files that import from this file
                if any(dep in file_path for dep in deps):
                    related.add(other_file)
                # Files that this file imports from
                if any(dep in other_file for dep in file_deps):
                    related.add(other_file)

        return list(related)