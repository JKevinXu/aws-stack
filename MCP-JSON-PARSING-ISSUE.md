# MCP JSON Parsing Issue and Fix

## Problem Description

The MCP (Model Context Protocol) client encounters a JSON parsing error when handling the `notifications/initialized` method:

```
ERROR:mcp.client.streamable_http:Error parsing JSON response
pydantic_core._pydantic_core.ValidationError: 1 validation error for JSONRPCMessage
  Invalid JSON: EOF while parsing a value at line 1 column 0 [type=json_invalid, input_value=b'', input_type=bytes]
```

## Root Cause

1. **Protocol Specification**: According to MCP protocol, notification methods (like `notifications/initialized`) should NOT return JSON-RPC responses - they are one-way messages.

2. **SDK Implementation Issue**: The MCP SDK's streamable HTTP client (`mcp/client/streamable_http.py`) incorrectly tries to parse ALL HTTP responses as JSON-RPC messages, even for notifications.

3. **HTTP Transport Limitation**: Since we're using HTTP transport via API Gateway, we must return an HTTP response (unlike WebSocket/stdio transports).

## Code Location

- **Server**: `/Users/kx/ws/aws-stack/lambda/mcp-server/index.py:104-113`
- **Client Error**: `/Users/kx/ws/aws-stack/venv/lib/python3.13/site-packages/mcp/client/streamable_http.py:302`

## Attempted Fixes

### Fix 1: Return HTTP 204 No Content (Original)
```python
elif method == 'notifications/initialized':
    return {
        'statusCode': 204,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS', 
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
    }
```
**Result**: Client still tries to parse empty body as JSON

### Fix 2: Return Empty JSON Object  
```python
elif method == 'notifications/initialized':
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': '{}'
    }
```
**Result**: Client expects valid JSON-RPC message structure, `{}` fails validation

### Fix 3: Remove Content-Type Header (Current)
```python
elif method == 'notifications/initialized':
    return {
        'statusCode': 204,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
    }
```
**Result**: SDK still calls `_handle_json_response` instead of `_handle_unexpected_content_type`

## Current Status

- **Functionality**: Despite the error logs, the MCP client works correctly - it successfully connects and executes tools
- **Issue Impact**: The JSON parsing error is logged but doesn't break functionality  
- **Protocol Compliance**: Server correctly returns HTTP 204 for notifications per protocol

## Next Steps to Consider

1. **Proper Notification Handling**: Modify server to detect notifications (no `id` field) and handle them appropriately
2. **SDK Workaround**: Return a minimal valid JSON-RPC response for notifications to satisfy SDK expectations
3. **Client-Side Fix**: Patch the MCP SDK to properly handle notification responses (not recommended for production)

## Working Solution

The current implementation works despite the error logs. The error is a limitation of the MCP SDK's HTTP transport implementation when handling notification methods in HTTP environments.