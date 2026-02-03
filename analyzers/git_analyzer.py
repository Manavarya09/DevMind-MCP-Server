"""
Git Analyzer

Analyzes git history and provides commit context.
"""

import os
from typing import List, Dict, Any
from git import Repo
from pathlib import Path

class GitAnalyzer:
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.repo = None
        try:
            self.repo = Repo(repo_path)
        except Exception:
            pass  # Not a git repo

    def get_recent_commits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits with details."""
        if not self.repo:
            return []

        commits = []
        for commit in list(self.repo.iter_commits())[:limit]:
            files_changed = []
            if commit.parents:
                # Get changed files
                diff = commit.diff(commit.parents[0])
                files_changed = [d.a_path for d in diff]

            commits.append({
                "hash": commit.hexsha,
                "message": commit.message.strip(),
                "author": commit.author.name,
                "date": commit.authored_datetime.isoformat(),
                "files_changed": files_changed
            })

        return commits

    def get_file_history(self, file_path: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get commit history for a specific file."""
        if not self.repo:
            return []

        commits = []
        try:
            for commit in list(self.repo.iter_commits(paths=file_path))[:limit]:
                commits.append({
                    "hash": commit.hexsha,
                    "message": commit.message.strip(),
                    "author": commit.author.name,
                    "date": commit.authored_datetime.isoformat()
                })
        except Exception:
            pass

        return commits

    def explain_changes(self, file_path: str) -> str:
        """Provide a summary of recent changes to a file."""
        if not self.repo:
            return "Not a git repository."

        history = self.get_file_history(file_path, 10)
        if not history:
            return f"No git history found for {file_path}."

        summary = f"Recent changes to {file_path}:\n\n"
        for commit in history:
            summary += f"- {commit['date'][:10]}: {commit['message']}\n"

        return summary