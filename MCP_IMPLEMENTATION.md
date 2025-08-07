# MCP Server Implementation

This project implements a Model Context Protocol (MCP) server using AWS Lambda and API Gateway.

## Architecture

- **Lambda Function**: Python-based MCP server (`lambda/mcp-server/index.py`)
- **API Gateway**: REST API endpoint for MCP communication
- **CDK Stack**: Infrastructure as code for deployment

## API Endpoint

**Base URL**: `https://sybw5cuj41.execute-api.us-west-2.amazonaws.com/prod/mcp`

## MCP Protocol Support

The server implements the following MCP methods:

### Initialize
Establishes connection and returns server capabilities.

```bash
curl -X POST https://sybw5cuj41.execute-api.us-west-2.amazonaws.com/prod/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","id":1}'
```

Response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "1.0.0",
    "serverInfo": {
      "name": "simple-mcp-server",
      "version": "1.0.0",
      "capabilities": {
        "tools": true
      }
    }
  },
  "id": 1
}
```

### Tools List
Returns available tools.

```bash
curl -X POST https://sybw5cuj41.execute-api.us-west-2.amazonaws.com/prod/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":2}'
```

Response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "add",
        "description": "Add two numbers",
        "inputSchema": {
          "type": "object",
          "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"}
          },
          "required": ["a", "b"]
        }
      }
    ]
  },
  "id": 2
}
```

### Tools Call
Executes the add tool with provided arguments.

```bash
curl -X POST https://sybw5cuj41.execute-api.us-west-2.amazonaws.com/prod/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"add","arguments":{"a":5,"b":3}},"id":3}'
```

Response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "8"
      }
    ]
  },
  "id": 3
}
```

## Deployment

The stack is deployed using AWS CDK:

```bash
# Build the project
npm run build

# Deploy the stack
npx cdk deploy ApiGatewayMcpStack
```

## Project Structure

```
├── bin/
│   └── aws-stack.ts          # CDK app entry point
├── lib/
│   ├── aws-stack-stack.ts    # Main stack
│   └── api-gateway-mcp-stack.ts # MCP API Gateway stack
├── lambda/
│   └── mcp-server/
│       └── index.py          # MCP server implementation
└── package.json              # Dependencies and scripts
```

## Features

- **CORS Enabled**: Cross-origin requests supported
- **Error Handling**: Proper JSON-RPC error responses
- **Logging**: CloudWatch logging for debugging
- **Scalable**: Lambda auto-scaling based on demand

## Testing

All MCP protocol methods have been tested and verified:
- ✅ Initialize handshake
- ✅ Tools listing
- ✅ Tool execution (add operation)