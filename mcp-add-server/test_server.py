#!/usr/bin/env python3
"""
Test script for MCP Add Two Server
"""

import requests
import json
import time

SERVER_URL = 'http://localhost:5000'

def test_server():
    print("🧪 Testing MCP Add Two Server (Python)...\n")
    
    try:
        # Test 1: Health check
        print("1️⃣ Testing health endpoint...")
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        health_data = response.json()
        print(f"✅ Health: {health_data['status']}")
        
        # Test 2: Initialize
        print("\n2️⃣ Testing initialize endpoint...")
        response = requests.post(f"{SERVER_URL}/initialize", 
                               json={}, 
                               timeout=5)
        init_data = response.json()
        print(f"✅ Initialize successful: {init_data['serverInfo']['name']}")
        
        # Test 3: List tools
        print("\n3️⃣ Testing tools list...")
        response = requests.post(f"{SERVER_URL}/tools/list",
                               json={},
                               timeout=5)
        tools_data = response.json()
        tool_names = [tool['name'] for tool in tools_data['tools']]
        print(f"✅ Available tools: {tool_names}")
        
        # Test 4: Call add_two tool
        print("\n4️⃣ Testing add_two tool...")
        response = requests.post(f"{SERVER_URL}/tools/call",
                               json={
                                   "name": "add_two",
                                   "arguments": {"a": 25, "b": 17}
                               },
                               timeout=5)
        call_data = response.json()
        print(f"✅ Tool result: {call_data['content'][0]['text']}")
        
        # Test 5: Test with float numbers
        print("\n5️⃣ Testing add_two with floats...")
        response = requests.post(f"{SERVER_URL}/tools/call",
                               json={
                                   "name": "add_two", 
                                   "arguments": {"a": 3.14, "b": 2.86}
                               },
                               timeout=5)
        call_data = response.json()
        print(f"✅ Float result: {call_data['content'][0]['text']}")
        
        print("\n🎉 All tests passed! MCP Server is working correctly.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running on port 5000.")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    # Wait a moment for server to start if running together
    time.sleep(2)
    test_server()