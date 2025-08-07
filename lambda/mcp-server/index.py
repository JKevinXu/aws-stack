import json
import logging
import base64

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def decode_token(token):
    """Decode JWT token without verification (for debugging only)"""
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Split the JWT
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Decode header and payload (add padding if needed)
        header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
        
        return {
            'header': header,
            'payload': payload
        }
    except Exception as e:
        logger.error(f"Error decoding token: {str(e)}")
        return None


def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Extract and decode ID token if present
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization') or headers.get('authorization')
    
    if auth_header:
        logger.info(f"Authorization header present: {auth_header[:20]}...")
        decoded = decode_token(auth_header)
        if decoded:
            logger.info(f"Decoded token header: {json.dumps(decoded['header'])}")
            logger.info(f"Decoded token payload: {json.dumps(decoded['payload'])}")
        else:
            logger.warning("Failed to decode token")
    else:
        logger.info("No Authorization header present")
    
    try:
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        
        method = body.get('method')
        params = body.get('params', {})
        request_id = body.get('id')
        
        if method == 'initialize':
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "simple-mcp-server",
                    "version": "1.0.0"
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
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
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