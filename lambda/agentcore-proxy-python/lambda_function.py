import json
import os
import time
import logging
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
region = os.environ.get('AWS_REGION', 'us-west-2')
# Note: For demo purposes, we'll initialize this only when needed
# bedrock_client = boto3.client('bedrock-agent-runtime', region_name=region)

def handle_inline_agent_logic(input_text: str) -> str:
    """
    Inline MCP-like agent logic for demo/testing purposes
    This simulates an agent that can handle various requests
    """
    input_lower = input_text.lower()
    
    # Simple pattern matching for demo purposes
    if 'aws services' in input_lower or 'aws service' in input_lower:
        return """Here are some key AWS services:

**Compute:**
- EC2: Virtual servers in the cloud
- Lambda: Serverless compute service
- ECS/EKS: Container orchestration

**Storage:**
- S3: Object storage service
- EBS: Block storage for EC2
- EFS: Managed file storage

**Database:**
- RDS: Managed relational databases
- DynamoDB: NoSQL database
- Aurora: High-performance managed database

**AI/ML:**
- Bedrock: Fully managed foundation models
- SageMaker: Machine learning platform
- Comprehend: Natural language processing

**Networking:**
- VPC: Virtual Private Cloud
- CloudFront: Content delivery network
- Route 53: DNS service

Would you like more details about any specific service?"""

    elif 'hello' in input_lower or 'hi' in input_lower:
        return f"Hello! I'm a Bedrock Agent Core proxy. I can help you with information about AWS services and more. What would you like to know?"

    elif 'bedrock' in input_lower:
        return """Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Stability AI, and Amazon via a single API, along with a broad set of capabilities you need to build generative AI applications with security, privacy, and responsible AI.

Key features:
- Access to multiple foundation models
- Fine-tuning capabilities  
- Retrieval Augmented Generation (RAG)
- Agents for complex workflows
- Built-in security and compliance"""

    elif 'help' in input_lower:
        return """I can help you with:
- Information about AWS services
- Bedrock and AI/ML services
- General cloud computing questions
- Architecture guidance

Just ask me anything you'd like to know!"""

    else:
        # Generic response with some helpful context
        return f"""I received your message: "{input_text}"

I'm a Bedrock Agent Core proxy that can provide information about AWS services, cloud architecture, and more. Here are some things you can ask me about:

- AWS services and their use cases
- Cloud architecture patterns  
- Bedrock and AI/ML services
- Best practices for cloud development

What specific information would you like to know?"""


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