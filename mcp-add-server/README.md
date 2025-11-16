# MCP Add Two Server

Simple MCP (Model Context Protocol) server written in Python that provides an `add_two` tool for adding two numbers.

## Features

- **HTTP-based MCP Server**: Compatible with AgentGateway
- **Add Two Tool**: Adds any two numbers (integers or floats)
- **Health Checks**: Built-in health monitoring
- **CORS Enabled**: Cross-origin requests supported
- **Error Handling**: Proper error responses for invalid inputs

## Setup

1. **Install dependencies**:
```bash
cd mcp-add-server
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python server.py
```

3. **Test the server**:
```bash
python test_server.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server info and documentation |
| `/health` | GET | Health check |
| `/initialize` | POST | Initialize MCP connection |
| `/tools/list` | POST | List available tools |
| `/tools/call` | POST | Execute a tool |

## Tool Usage

### add_two

Adds two numbers together.

**Request**:
```json
{
  "name": "add_two",
  "arguments": {
    "a": 5,
    "b": 3
  }
}
```

**Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "The sum of 5 + 3 = 8"
    }
  ]
}
```

## Integration with AgentGateway

This server runs on `http://localhost:5000` and can be connected to AgentGateway using HTTP MCP configuration.

Example AgentGateway config:
```yaml
backends:
- mcp:
    targets:
    - name: add-server
      http:
        url: "http://localhost:5000"
```