#!/usr/bin/env python3
"""
MCP Server for adding two numbers
Implements Model Context Protocol over HTTP
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging
from datetime import datetime
import json
import uuid

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server info
SERVER_INFO = {
    "name": "add-two-server",
    "version": "1.0.0", 
    "description": "MCP Server for adding two numbers",
    "protocol_version": "2024-11-05"
}

# Available tools
TOOLS = [
    {
        "name": "add_two",
        "description": "Add two numbers together", 
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "First number to add"
                },
                "b": {
                    "type": "number",
                    "description": "Second number to add" 
                }
            },
            "required": ["a", "b"]
        }
    }
]

def call_add_two_tool(arguments):
    """Helper function to execute add_two tool"""
    try:
        a = arguments.get('a')
        b = arguments.get('b')
        
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return {
                "error": {
                    "code": "InvalidArgument",
                    "message": "Both 'a' and 'b' must be numbers"
                }
            }
        
        result = a + b
        return {
            "content": [{
                "type": "text", 
                "text": f"The sum of {a} + {b} = {result}"
            }]
        }
    except Exception as e:
        return {
            "error": {
                "code": "ToolExecutionError",
                "message": f"Error executing add_two: {str(e)}"
            }
        }

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with server information"""
    return jsonify({
        "message": "🧮 Add Two MCP Server (Python)",
        "info": SERVER_INFO,
        "endpoints": {
            "initialize": "POST /initialize",
            "list_tools": "POST /tools/list",
            "call_tool": "POST /tools/call", 
            "health": "GET /health",
            "mcp_base": "GET /mcp/"
        },
        "available_tools": TOOLS
    })

@app.route('/mcp/', methods=['GET', 'POST'])
def mcp_base():
    """MCP base endpoint for AgentGateway"""
    if request.method == 'GET':
        return jsonify({
            "message": "MCP Server ready",
            "protocol_version": SERVER_INFO["protocol_version"],
            "server_info": SERVER_INFO,
            "endpoints": {
                "initialize": "POST /mcp/initialize",
                "tools_list": "POST /mcp/tools/list", 
                "tools_call": "POST /mcp/tools/call"
            }
        })
    else:
        # Handle POST requests to base MCP endpoint
        data = request.get_json()
        method = data.get('method') if data else None
        
        if method == 'initialize':
            return mcp_initialize()
        elif method == 'tools/list':
            return mcp_tools_list()
        elif method == 'tools/call':
            return mcp_tools_call()
        else:
            return jsonify({
                "jsonrpc": "2.0",
                "id": data.get("id", "unknown"),
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }), 404

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "server": SERVER_INFO["name"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/initialize', methods=['POST'])
def initialize():
    """Initialize MCP server"""
    logger.info("🚀 MCP Server initialized")
    return jsonify({
        "protocolVersion": SERVER_INFO["protocol_version"],
        "capabilities": {
            "tools": {}
        },
        "serverInfo": SERVER_INFO
    })

@app.route('/tools/list', methods=['POST'])
def list_tools():
    """List available tools"""
    logger.info("📋 Tools list requested")
    return jsonify({
        "tools": TOOLS
    })

@app.route('/tools/call', methods=['POST'])
def call_tool():
    """Call a specific tool"""
    data = request.get_json()
    tool_name = data.get('name')
    arguments = data.get('arguments', {})
    
    logger.info(f"🔧 Tool called: {tool_name} with args: {arguments}")
    
    if tool_name == 'add_two':
        try:
            a = arguments.get('a')
            b = arguments.get('b')
            
            # Validate inputs
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                return jsonify({
                    "error": {
                        "code": "InvalidArgument",
                        "message": "Both 'a' and 'b' must be numbers"
                    }
                }), 400
            
            result = a + b
            
            return jsonify({
                "content": [
                    {
                        "type": "text", 
                        "text": f"The sum of {a} + {b} = {result}"
                    }
                ]
            })
            
        except Exception as e:
            return jsonify({
                "error": {
                    "code": "ToolExecutionError",
                    "message": f"Error executing add_two: {str(e)}"
                }
            }), 500
    
    else:
        return jsonify({
            "error": {
                "code": "ToolNotFound", 
                "message": f"Tool '{tool_name}' not found"
            }
        }), 404

@app.route('/sse', methods=['GET', 'POST'])
def sse_endpoint():
    """
    SSE endpoint for MCP protocol communication compatible with AgentGateway
    """
    if request.method == 'GET':
        # Basic SSE handshake
        return Response(
            "data: {}\n\n".format(json.dumps({
                "jsonrpc": "2.0",
                "method": "notifications/initialized", 
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": SERVER_INFO
                }
            })),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )
    
    else:
        # Handle POST requests for MCP protocol 
        data = request.get_json()
        method = data.get('method') if data else None
        
        if method == 'initialize':
            result = {
                "jsonrpc": "2.0",
                "id": data.get("id", str(uuid.uuid4())),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": SERVER_INFO
                }
            }
        elif method == 'tools/list':
            result = {
                "jsonrpc": "2.0",
                "id": data.get("id", str(uuid.uuid4())),
                "result": {"tools": TOOLS}
            }
        elif method == 'tools/call':
            # Extract tool call params
            params = data.get('params', {})
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name == 'add_two':
                tool_result = call_add_two_tool(arguments)
                result = {
                    "jsonrpc": "2.0", 
                    "id": data.get("id", str(uuid.uuid4())),
                    "result": tool_result
                }
            else:
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", str(uuid.uuid4())),
                    "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
                }
        else:
            result = {
                "jsonrpc": "2.0", 
                "id": data.get("id", "unknown"),
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            }
        
        return jsonify(result)

@app.route('/mcp/initialize', methods=['POST'])
def mcp_initialize():
    """
    MCP protocol initialize endpoint
    """
    return jsonify({
        "jsonrpc": "2.0",
        "id": request.json.get("id", str(uuid.uuid4())),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": False
                }
            },
            "serverInfo": SERVER_INFO
        }
    })

@app.route('/mcp/tools/list', methods=['POST'])  
def mcp_tools_list():
    """
    MCP protocol tools list endpoint
    """
    return jsonify({
        "jsonrpc": "2.0", 
        "id": request.json.get("id", str(uuid.uuid4())),
        "result": {
            "tools": TOOLS
        }
    })

@app.route('/mcp/tools/call', methods=['POST'])
def mcp_tools_call():
    """
    MCP protocol tools call endpoint  
    """
    req_data = request.json
    tool_name = req_data.get("params", {}).get("name")
    arguments = req_data.get("params", {}).get("arguments", {})
    
    if tool_name == "add_two":
        result = call_add_two_tool(arguments)
        return jsonify({
            "jsonrpc": "2.0",
            "id": req_data.get("id", str(uuid.uuid4())),
            "result": result
        })
    else:
        return jsonify({
            "jsonrpc": "2.0",
            "id": req_data.get("id", str(uuid.uuid4())),
            "error": {
                "code": -32601,
                "message": f"Tool '{tool_name}' not found"
            }
        })

if __name__ == '__main__':
    print('===============================================')
    print('🚀 Add Two MCP Server (Python) Starting...')
    print('===============================================')
    print('📡 Server will run on http://localhost:5000')
    print('🔧 Available tool: add_two(a, b)')
    print('💡 Example: POST /tools/call')
    print('   Body: {"name": "add_two", "arguments": {"a": 5, "b": 3}}')
    print('📊 Health check: GET /health')
    print('===============================================')
    
    app.run(host='0.0.0.0', port=5000, debug=False)