"""
Database Layer

SQLite storage for project metadata.
"""

import sqlite3
import json
from typing import Dict, Any, List
from pathlib import Path

class Database:
    def __init__(self, db_path: str = "devmind.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    path TEXT PRIMARY KEY,
                    name TEXT,
                    extension TEXT,
                    size INTEGER,
                    lines INTEGER,
                    data TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS functions (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    file TEXT,
                    line_start INTEGER,
                    line_end INTEGER,
                    args TEXT,
                    docstring TEXT,
                    code TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS dependencies (
                    file TEXT,
                    dependency TEXT,
                    PRIMARY KEY (file, dependency)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY,
                    type TEXT,
                    message TEXT,
                    file TEXT,
                    line INTEGER
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS commits (
                    hash TEXT PRIMARY KEY,
                    message TEXT,
                    author TEXT,
                    date TEXT,
                    files_changed TEXT
                )
            """)

    def save_project_data(self, data: Dict[str, Any]):
        """Save analyzed project data."""
        with sqlite3.connect(self.db_path) as conn:
            # Clear existing data
            conn.execute("DELETE FROM files")
            conn.execute("DELETE FROM functions")
            conn.execute("DELETE FROM dependencies")
            conn.execute("DELETE FROM todos")

            # Insert files
            for file_info in data["files"]:
                conn.execute("""
                    INSERT INTO files (path, name, extension, size, lines, data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    file_info["path"],
                    file_info["name"],
                    file_info["extension"],
                    file_info["size"],
                    file_info["lines"],
                    json.dumps(file_info)
                ))

            # Insert functions
            for func in data["functions"]:
                conn.execute("""
                    INSERT INTO functions (name, file, line_start, line_end, args, docstring, code)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    func["name"],
                    func["file"],
                    func["line_start"],
                    func["line_end"],
                    json.dumps(func["args"]),
                    func["docstring"],
                    func["code"]
                ))

            # Insert dependencies
            for file_path, deps in data["dependencies"].items():
                for dep in deps:
                    conn.execute("""
                        INSERT INTO dependencies (file, dependency)
                        VALUES (?, ?)
                    """, (file_path, dep))

            # Insert todos
            for todo in data["todos"]:
                conn.execute("""
                    INSERT INTO todos (type, message, file, line)
                    VALUES (?, ?, ?, ?)
                """, (
                    todo["type"],
                    todo["message"],
                    todo["file"],
                    todo["line"]
                ))

    def get_project_overview(self) -> Dict[str, Any]:
        """Get project overview statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # File stats
            cursor.execute("SELECT COUNT(*), SUM(size), SUM(lines) FROM files")
            file_count, total_size, total_lines = cursor.fetchone()

            # Function stats
            cursor.execute("SELECT COUNT(*) FROM functions")
            func_count = cursor.fetchone()[0]

            # TODO stats
            cursor.execute("SELECT type, COUNT(*) FROM todos GROUP BY type")
            todo_stats = dict(cursor.fetchall())

            return {
                "file_count": file_count or 0,
                "total_size": total_size or 0,
                "total_lines": total_lines or 0,
                "function_count": func_count or 0,
                "todos": todo_stats
            }

    def search_functions(self, query: str) -> List[Dict[str, Any]]:
        """Search functions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, file, line_start, docstring, code
                FROM functions
                WHERE name LIKE ? OR docstring LIKE ?
            """, (f"%{query}%", f"%{query}%"))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "name": row[0],
                    "file": row[1],
                    "line": row[2],
                    "docstring": row[3],
                    "code": row[4]
                })
            return results

    def get_function_context(self, func_name: str) -> Dict[str, Any]:
        """Get detailed context for a function."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, file, line_start, line_end, args, docstring, code
                FROM functions
                WHERE name = ?
            """, (func_name,))

            row = cursor.fetchone()
            if row:
                return {
                    "name": row[0],
                    "file": row[1],
                    "line_start": row[2],
                    "line_end": row[3],
                    "args": json.loads(row[4]),
                    "docstring": row[5],
                    "code": row[6]
                }
            return {}

    def find_related_files(self, file_path: str) -> List[str]:
        """Find files related to the given file."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Files that import from this file
            cursor.execute("""
                SELECT DISTINCT f.path
                FROM files f
                JOIN dependencies d ON f.path = d.file
                WHERE d.dependency LIKE ?
            """, (f"%{Path(file_path).stem}%",))

            related = [row[0] for row in cursor.fetchall()]

            # Files that this file imports
            cursor.execute("""
                SELECT DISTINCT dependency
                FROM dependencies
                WHERE file = ?
            """, (file_path,))

            imported = [row[0] for row in cursor.fetchall()]

            return list(set(related + imported))

    def save_git_data(self, commits: List[Dict[str, Any]]):
        """Save git commit data."""
        with sqlite3.connect(self.db_path) as conn:
            for commit in commits:
                conn.execute("""
                    INSERT OR REPLACE INTO commits (hash, message, author, date, files_changed)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    commit["hash"],
                    commit["message"],
                    commit["author"],
                    commit["date"],
                    json.dumps(commit["files_changed"])
                ))

    def get_recent_commits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT hash, message, author, date, files_changed
                FROM commits
                ORDER BY date DESC
                LIMIT ?
            """, (limit,))

            commits = []
            for row in cursor.fetchall():
                commits.append({
                    "hash": row[0],
                    "message": row[1],
                    "author": row[2],
                    "date": row[3],
                    "files_changed": json.loads(row[4])
                })
            return commits