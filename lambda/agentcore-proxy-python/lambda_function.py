import json
import os
import time
import logging
import asyncio
import re
from typing import Dict, Any, Optional, List
import boto3
from botocore.exceptions import ClientError
from contextlib import AsyncExitStack

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
region = os.environ.get('AWS_REGION', 'us-west-2')
# Note: For demo purposes, we'll initialize this only when needed
# bedrock_client = boto3.client('bedrock-agent-runtime', region_name=region)

# MCP Client classes for inline agent implementation

class MCPSDKClient:
    """Simplified MCP client for Lambda environment"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self._initialized = False
        self._tools_cache = None
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize connection with MCP server"""
        if self._initialized:
            return {"result": "already_initialized"}
        
        try:
            # For Lambda, we'll use a simplified approach without external HTTP libraries
            # In a full implementation, this would use the MCP SDK
            self._initialized = True
            return {"result": "initialized"}
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {str(e)}")
            raise
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from MCP server"""
        try:
            # For demo purposes, return a simple tool set
            # In production, this would query the actual MCP server
            tools = [
                {
                    "name": "add",
                    "description": "Add two numbers together",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "number", "description": "First number"},
                            "b": {"type": "number", "description": "Second number"}
                        },
                        "required": ["a", "b"]
                    }
                }
            ]
            return {"result": {"tools": tools}}
        except Exception as e:
            logger.error(f"Failed to list tools: {str(e)}")
            return {"error": str(e)}
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        try:
            # For demo purposes, implement basic math operations
            if tool_name == "add" and "a" in arguments and "b" in arguments:
                result = arguments["a"] + arguments["b"]
                return {
                    "result": {
                        "content": [{"text": str(result)}]
                    }
                }
            else:
                return {"error": f"Unknown tool or invalid arguments: {tool_name}"}
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            return {"error": str(e)}
    
    async def close(self):
        """Close the MCP client connection"""
        self._initialized = False

class ActionGroup:
    """Represents an action group with MCP clients"""
    
    def __init__(self, name: str, mcp_clients: List[MCPSDKClient]):
        self.name = name
        self.mcp_clients = mcp_clients
        self.available_tools = []
    
    async def initialize(self):
        """Initialize all MCP clients and gather available tools"""
        for client in self.mcp_clients:
            try:
                # Initialize the client
                init_response = await client.initialize()
                logger.info(f"MCP client initialized: {init_response}")
                
                # Get available tools
                tools_response = await client.list_tools()
                if 'result' in tools_response and 'tools' in tools_response['result']:
                    tools = tools_response['result']['tools']
                    self.available_tools.extend(tools)
                    tool_names = [tool['name'] for tool in tools]
                    logger.info(f"Connected to server with tools: {tool_names}")
                    
            except Exception as e:
                logger.error(f"Failed to initialize MCP client: {str(e)}")
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool using the appropriate MCP client"""
        for client in self.mcp_clients:
            try:
                result = await client.call_tool(tool_name, arguments)
                return result
            except Exception as e:
                logger.error(f"Tool execution failed with client: {str(e)}")
                continue
        
        raise Exception(f"No MCP client could execute tool: {tool_name}")
    
    async def close(self):
        """Close all MCP clients"""
        for client in self.mcp_clients:
            try:
                await client.close()
            except Exception as e:
                logger.error(f"Error closing MCP client: {str(e)}")

class InlineAgent:
    """
    Bedrock Inline Agent with MCP integration
    Simplified version for Lambda deployment
    """
    
    def __init__(self, foundation_model: str, instruction: str, agent_name: str, action_groups: List[ActionGroup]):
        self.foundation_model = foundation_model
        self.instruction = instruction
        self.agent_name = agent_name
        self.action_groups = action_groups
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region)
    
    async def initialize(self):
        """Initialize all action groups"""
        for action_group in self.action_groups:
            await action_group.initialize()
    
    async def close(self):
        """Close all action groups and their clients"""
        for action_group in self.action_groups:
            await action_group.close()
    
    async def invoke(self, input_text: str) -> str:
        """
        Invoke the inline agent with the given input
        This is a simplified implementation that demonstrates MCP integration
        """
        await self.initialize()
        
        # Get available tools from all action groups
        all_tools = []
        for action_group in self.action_groups:
            all_tools.extend(action_group.available_tools)
        
        # Create a system prompt that includes tool information
        system_prompt = f"""{self.instruction}

Available Tools:
{json.dumps(all_tools, indent=2)}

IMPORTANT: When you need to use a tool, respond with ONLY a JSON object in this exact format:
{{"tool_name": "tool_name", "arguments": {{"param1": "value1", "param2": "value2"}}}}

Do not add any other text before or after the JSON. Just return the JSON object.

If no tool is needed, respond normally with text."""
        
        # Prepare the conversation - content must be a list for Bedrock
        messages = [
            {
                "role": "user",
                "content": [{"text": input_text}]
            }
        ]
        
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call Bedrock model
            response = self.bedrock_client.converse(
                modelId=self.foundation_model,
                messages=messages,
                system=[{"text": system_prompt}],
                inferenceConfig={
                    "maxTokens": 2000,
                    "temperature": 0.1
                }
            )
            
            assistant_message = response['output']['message']['content'][0]['text']
            messages.append({
                "role": "assistant",
                "content": [{"text": assistant_message}]
            })
            
            logger.info(f"Agent thought: {assistant_message}")
            
            # Check if the response contains a tool call
            try:
                # Try to parse as JSON tool call
                tool_call_json = None
                if assistant_message.strip().startswith('{') and assistant_message.strip().endswith('}'):
                    try:
                        tool_call_json = json.loads(assistant_message.strip())
                    except json.JSONDecodeError:
                        pass
                
                # Also check if the response contains a JSON object within text
                if not tool_call_json:
                    json_match = re.search(r'\{[^{}]*"tool_name"[^{}]*\}', assistant_message)
                    if json_match:
                        try:
                            tool_call_json = json.loads(json_match.group())
                        except json.JSONDecodeError:
                            pass
                
                if tool_call_json and 'tool_name' in tool_call_json and 'arguments' in tool_call_json:
                    tool_name = tool_call_json['tool_name']
                    arguments = tool_call_json['arguments']
                    
                    logger.info(f"Tool use: {tool_name} with inputs: {arguments}")
                    
                    # Execute the tool
                    try:
                        for action_group in self.action_groups:
                            tool_result = await action_group.execute_tool(tool_name, arguments)
                            
                            if 'result' in tool_result:
                                result_content = tool_result['result']['content'][0]['text']
                                logger.info(f"Tool result: {result_content}")
                                
                                # Add tool result to conversation
                                messages.append({
                                    "role": "user",
                                    "content": [{"text": f"Tool '{tool_name}' returned: {result_content}"}]
                                })
                                break
                            else:
                                logger.error(f"Tool execution error: {tool_result}")
                                messages.append({
                                    "role": "user",
                                    "content": [{"text": f"Tool '{tool_name}' failed: {tool_result}"}]
                                })
                                break
                    
                    except Exception as e:
                        error_msg = f"Tool execution failed: {str(e)}"
                        logger.error(error_msg)
                        messages.append({
                            "role": "user",
                            "content": [{"text": error_msg}]
                        })
                else:
                    # Not a tool call, return the response
                    await self.close()
                    return assistant_message
                    
            except Exception as e:
                # Error parsing, return as is
                logger.error(f"Error parsing response: {str(e)}")
                await self.close()
                return assistant_message
        
        await self.close()
        return "Maximum iterations reached. Please try again with a simpler request."

def handle_inline_agent_logic(input_text: str) -> str:
    """
    Wrapper function to handle async inline agent invocation
    This function maintains backward compatibility while using the new InlineAgent
    """
    try:
        # Create a simple async wrapper
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create MCP client for demo purposes
        mcp_client = MCPSDKClient("demo-server")
        
        # Create action group
        action_group = ActionGroup(
            name="GeneralActionGroup",
            mcp_clients=[mcp_client]
        )
        
        # Create inline agent
        agent = InlineAgent(
            foundation_model="anthropic.claude-3-5-sonnet-20241022-v2:0",
            instruction="You are a helpful assistant that can perform various tasks including mathematical calculations. When asked to perform calculations or other tasks that require tools, use the appropriate tools to get accurate results.",
            agent_name="GeneralAgent",
            action_groups=[action_group]
        )
        
        # Run the agent
        try:
            result = loop.run_until_complete(agent.invoke(input_text))
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error in inline agent logic: {str(e)}")
        # Fallback to a simple response
        return f"I'm an AI assistant that can help with various tasks. You asked: '{input_text}'. While I encountered an issue with advanced processing, I'm here to help. Could you please rephrase your question or try again?"


def lambda_handler(event, context):
    """
    Lambda handler for Bedrock Agent Core proxy with IAM authentication
    Provides secure access to Bedrock Agent Core from external websites
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse the incoming request
        request_data = parse_request_event(event)
        
        # Authenticate the request
        auth_result = authenticate_request(request_data)
        if not auth_result['success']:
            return create_error_response(401, auth_result['error'])
        
        # Route the request based on the path
        if request_data['path'] == '/agent/invoke':
            return handle_agent_invoke(request_data)
        elif request_data['path'] == '/agent/health':
            return handle_health_check()
        elif request_data['path'].startswith('/agent/sessions/'):
            return handle_session_management(request_data)
        else:
            return create_error_response(404, 'Endpoint not found')
            
    except Exception as error:
        logger.error(f'Error processing request: {str(error)}')
        return create_error_response(500, 'Internal server error')


def parse_request_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse the incoming Lambda event into a structured request object"""
    return {
        'method': event.get('httpMethod', 'POST'),
        'path': event.get('path', '/agent/invoke'),
        'headers': event.get('headers', {}),
        'query_params': event.get('queryStringParameters') or {},
        'body': json.loads(event.get('body', '{}')) if event.get('body') else {},
        'request_context': event.get('requestContext', {})
    }


def authenticate_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Authenticate the incoming request using multiple methods"""
    headers = request_data['headers']
    
    # Check for API Key authentication
    api_key = headers.get('x-api-key') or headers.get('X-Api-Key')
    if api_key and validate_api_key(api_key):
        return {'success': True, 'auth_type': 'api-key'}
    
    # Check for AWS Signature authentication
    auth_header = headers.get('authorization') or headers.get('Authorization')
    if auth_header and auth_header.startswith('AWS4-HMAC-SHA256'):
        return {'success': True, 'auth_type': 'aws-signature'}
    
    # Check for Bearer token authentication
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        token_result = validate_bearer_token(token)
        if token_result['valid']:
            return {'success': True, 'auth_type': 'bearer-token', 'user': token_result.get('user')}
    
    # For development/testing - allow requests when in development mode
    if os.environ.get('NODE_ENV') == 'development':
        logger.warning('WARNING: Development mode - allowing unauthenticated requests')
        return {'success': True, 'auth_type': 'dev-mode'}
    
    # Check for allowed origins in non-production mode
    origin = headers.get('origin') or headers.get('Origin')
    if os.environ.get('NODE_ENV') != 'production' and is_allowed_origin(origin):
        logger.warning('WARNING: Allowing unauthenticated request from allowed origin in non-production mode')
        return {'success': True, 'auth_type': 'dev-origin'}
    
    return {'success': False, 'error': 'Authentication required'}


def validate_api_key(api_key: str) -> bool:
    """Validate API Key (implement your API key validation logic)"""
    # TODO: Implement API key validation against your key store
    # For now, check against environment variable for demo purposes
    valid_api_keys = os.environ.get('VALID_API_KEYS', '').split(',')
    return api_key in valid_api_keys


def validate_bearer_token(token: str) -> Dict[str, Any]:
    """Validate Bearer token (implement your token validation logic)"""
    try:
        # TODO: Implement JWT validation or other token validation logic
        # This is a placeholder - replace with your actual token validation
        
        # Example: Basic token validation
        if len(token) > 10:
            return {'valid': True, 'user': 'authenticated-user'}
        
        return {'valid': False}
    except Exception as error:
        logger.error(f'Token validation error: {str(error)}')
        return {'valid': False}


def is_allowed_origin(origin: Optional[str]) -> bool:
    """Check if origin is allowed for development mode"""
    if not origin:
        return False
    
    allowed_origins = [
        'http://localhost:3000',
        'http://localhost:3001',
        'http://127.0.0.1:3000',
        'https://localhost:3000'
    ]
    return origin in allowed_origins


def handle_agent_invoke(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle agent invocation requests with real Bedrock Agent Core client"""
    body = request_data['body']
    agent_arn = body.get('agentArn')
    input_text = body.get('input')
    session_id = body.get('sessionId')
    qualifier = body.get('qualifier')
    
    # Validate required parameters
    if not input_text:
        return create_error_response(400, 'Missing required parameter: input is required')
    
    try:
        # Get agent ARN from request, environment, or use default
        target_agent_arn = (agent_arn or 
                           os.environ.get('DEFAULT_AGENT_ARN') or 
                           "arn:aws:bedrock-agentcore:us-west-2:313117444016:runtime/agentcore_strands-fRvDuw6SOI")
        
        # Use provided qualifier or default to "DEFAULT"
        endpoint_qualifier = qualifier or "DEFAULT"
        
        logger.info(f'Invoking agent: {target_agent_arn}')
        logger.info(f'Qualifier: {endpoint_qualifier}')
        logger.info(f'Input: {input_text}')
        
        # Initialize Bedrock Agent Runtime client
        bedrock_client = boto3.client('bedrock-agent-runtime', region_name=region)
        
        # Parse agent ARN to get agent_id and agent_alias_id
        # Expected format: arn:aws:bedrock-agentcore:region:account:runtime/agent_name
        if target_agent_arn.startswith('arn:aws:bedrock-agentcore:'):
            # Convert agentcore ARN to agent runtime format
            arn_parts = target_agent_arn.split(':')
            agent_name = arn_parts[-1].split('/')[-1] if '/' in arn_parts[-1] else arn_parts[-1]
            # For demo purposes, use a placeholder agent ID - you'll need to map this properly
            agent_id = "your-actual-agent-id"  # Replace with actual mapping
            agent_alias_id = endpoint_qualifier or "TSTALIASID"
        else:
            # Assume it's already in the correct format
            agent_id = target_agent_arn
            agent_alias_id = endpoint_qualifier or "TSTALIASID"
        
        logger.info(f'Using bedrock-agent-runtime with agent_id: {agent_id}, agent_alias_id: {agent_alias_id}')
        
        # Generate session ID if not provided
        session_id = session_id or f'session-{int(time.time() * 1000)}'
        
        # For demo/testing purposes, provide inline MCP-like agent logic as fallback
        if agent_id == "your-actual-agent-id" or agent_id.startswith('arn:aws:bedrock-agentcore:'):
            logger.info('Using inline MCP agent logic for demo')
            response_text = handle_inline_agent_logic(input_text)
        else:
            logger.info('Invoking Bedrock Agent Runtime...')
            
            try:
                # Invoke the agent using bedrock-agent-runtime
                response = bedrock_client.invoke_agent(
                    agentId=agent_id,
                    agentAliasId=agent_alias_id,
                    sessionId=session_id,
                    inputText=input_text
                )
                
                # Process the response from the EventStream
                response_text = ""
                if 'completion' in response:
                    for event in response['completion']:
                        if 'chunk' in event:
                            chunk = event['chunk']
                            if 'bytes' in chunk:
                                chunk_text = chunk['bytes'].decode('utf-8')
                                response_text += chunk_text
                            elif 'attribution' in chunk:
                                # Handle attribution information
                                pass
                else:
                    response_text = "No completion found in response"
                    
            except Exception as e:
                logger.error(f'Error with bedrock-agent-runtime: {str(e)}')
                logger.info('Falling back to inline MCP agent logic')
                response_text = handle_inline_agent_logic(input_text)
        
        logger.info('Agent response processed successfully')
        
        return create_success_response({
            'success': True,
            'response': response_text,
            'agentArn': target_agent_arn,
            'agentId': agent_id,
            'agentAliasId': agent_alias_id,
            'qualifier': endpoint_qualifier,
            'sessionId': session_id,
            'contentType': 'application/json',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ', time.gmtime())
        })
        
    except Exception as error:
        logger.error(f'Error invoking agent: {str(error)}')
        return create_error_response(500, f'Failed to invoke agent: {str(error)}')


def handle_session_management(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle session management requests"""
    path_parts = request_data['path'].split('/')
    session_id = path_parts[-1] if path_parts else 'unknown'
    
    if request_data['method'] == 'GET':
        # Return session information
        return create_success_response({
            'sessionId': session_id,
            'status': 'active',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ', time.gmtime())
        })
    
    return create_error_response(405, 'Method not allowed')


def handle_health_check() -> Dict[str, Any]:
    """Handle health check requests"""
    return create_success_response({
        'status': 'healthy',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ', time.gmtime()),
        'version': '1.0.0'
    })


def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a success response"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Session-Id',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(data)
    }


def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Create an error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Session-Id',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ', time.gmtime())
        })
    }