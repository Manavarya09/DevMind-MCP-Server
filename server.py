#!/usr/bin/env python3
"""
DevMind MCP Server

An MCP server that provides structured project context to AI models.
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, List
from context.analyzer import ProjectAnalyzer
from storage.db import Database
from tools.registry import ToolRegistry
from analyzers.git_analyzer import GitAnalyzer

class DevMindMCPServer:
    def __init__(self):
        self.analyzer = ProjectAnalyzer()
        self.db = Database()
        self.git_analyzer = GitAnalyzer()
        self.tools = ToolRegistry(self.analyzer, self.db, self.git_analyzer)

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            id = request.get("id")

            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "devmind-mcp",
                            "version": "0.1.0"
                        }
                    }
                }
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {
                        "tools": self.tools.list_tools()
                    }
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                result = await self.tools.call_tool(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": result
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }

    async def run(self):
        """Run the MCP server."""
        # Index the project on startup
        project_root = os.getcwd()
        self.analyzer.index_project(project_root)
        self.db.save_project_data(self.analyzer.get_data())

        # Index git data
        commits = self.git_analyzer.get_recent_commits(50)  # Get more for storage
        self.db.save_git_data(commits)

        # Read from stdin, write to stdout
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                continue
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    server = DevMindMCPServer()
    asyncio.run(server.run())

def main():
    """Entry point for the devmind-mcp command."""
    server = DevMindMCPServer()
    asyncio.run(server.run())