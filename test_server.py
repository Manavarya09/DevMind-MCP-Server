#!/usr/bin/env python3
"""
Test script for DevMind MCP server.
"""

import json
import asyncio
from server import DevMindMCPServer

async def test_server():
    server = DevMindMCPServer()

    # Test initialize
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    response = await server.handle_request(init_request)
    print("Initialize response:", json.dumps(response, indent=2))

    # Test tools/list
    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    response = await server.handle_request(list_request)
    print("Tools list response:", json.dumps(response, indent=2))

    # Test get_project_overview
    overview_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_project_overview",
            "arguments": {}
        }
    }
    response = await server.handle_request(overview_request)
    print("Project overview response:", json.dumps(response, indent=2))

if __name__ == "__main__":
    asyncio.run(test_server())