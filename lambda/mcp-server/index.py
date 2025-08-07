import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        
        method = body.get('method')
        params = body.get('params', {})
        request_id = body.get('id')
        
        if method == 'initialize':
            result = {
                "protocolVersion": "1.0.0",
                "serverInfo": {
                    "name": "simple-mcp-server",
                    "version": "1.0.0",
                    "capabilities": {
                        "tools": True
                    }
                }
            }
        elif method == 'tools/list':
            result = {
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
            }
        elif method == 'tools/call':
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "add":
                a = arguments.get("a", 0)
                b = arguments.get("b", 0)
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": str(a + b)
                        }
                    ]
                }
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'jsonrpc': '2.0',
                'result': result,
                'id': request_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32602,
                    'message': str(e)
                },
                'id': body.get('id') if 'body' in locals() else None
            })
        }