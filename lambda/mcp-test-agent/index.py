import json
import urllib3
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create HTTP client
http = urllib3.PoolManager()

# MCP Server endpoint
MCP_SERVER_URL = "https://sybw5cuj41.execute-api.us-west-2.amazonaws.com/prod/mcp"

def make_mcp_request(method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a JSON-RPC request to the MCP server"""
    
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1
    }
    
    if params:
        payload["params"] = params
    
    try:
        response = http.request(
            'POST',
            MCP_SERVER_URL,
            body=json.dumps(payload),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'bedrock-agent-mcp-tester/1.0'
            }
        )
        
        logger.info(f"MCP Request: {method} - Status: {response.status}")
        logger.info(f"Response body: {response.data.decode('utf-8')}")
        
        if response.status == 200:
            return {
                "success": True,
                "result": json.loads(response.data.decode('utf-8'))
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status}: {response.data.decode('utf-8')}"
            }
            
    except Exception as e:
        logger.error(f"Error making MCP request: {str(e)}")
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }

def test_mcp_initialize() -> Dict[str, Any]:
    """Test MCP server initialization"""
    logger.info("Testing MCP initialize")
    return make_mcp_request("initialize")

def test_mcp_tools_list() -> Dict[str, Any]:
    """Test MCP server tools listing"""
    logger.info("Testing MCP tools/list")
    return make_mcp_request("tools/list")

def test_mcp_tools_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Test MCP server tool execution"""
    logger.info(f"Testing MCP tools/call with tool: {tool_name}")
    
    params = {
        "name": tool_name,
        "arguments": arguments
    }
    
    return make_mcp_request("tools/call", params)

def lambda_handler(event, context):
    """AWS Lambda handler for Bedrock Agent action group"""
    
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract the action group, api path, and parameters from the event
        action_group = event.get('actionGroup', '')
        api_path = event.get('apiPath', '')
        parameters = event.get('parameters', [])
        
        # Convert parameters list to dictionary for easier access
        param_dict = {}
        for param in parameters:
            param_dict[param['name']] = param['value']
        
        logger.info(f"Action: {action_group}, Path: {api_path}, Params: {param_dict}")
        
        # Route to appropriate MCP test function
        if api_path == '/test-mcp-initialize':
            result = test_mcp_initialize()
            
        elif api_path == '/test-mcp-tools-list':
            result = test_mcp_tools_list()
            
        elif api_path == '/test-mcp-tools-call':
            tool_name = param_dict.get('toolName', 'add')
            arguments = json.loads(param_dict.get('arguments', '{}'))
            result = test_mcp_tools_call(tool_name, arguments)
            
        else:
            result = {
                "success": False,
                "error": f"Unknown API path: {api_path}"
            }
        
        # Format response for Bedrock Agent
        response = {
            "actionGroup": action_group,
            "apiPath": api_path,
            "httpMethod": event.get('httpMethod', 'POST'),
            "httpStatusCode": 200,
            "responseBody": {
                "application/json": {
                    "body": json.dumps(result)
                }
            }
        }
        
        logger.info(f"Returning response: {json.dumps(response)}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        
        error_response = {
            "actionGroup": event.get('actionGroup', ''),
            "apiPath": event.get('apiPath', ''),
            "httpMethod": event.get('httpMethod', 'POST'),
            "httpStatusCode": 500,
            "responseBody": {
                "application/json": {
                    "body": json.dumps({
                        "success": False,
                        "error": f"Internal error: {str(e)}"
                    })
                }
            }
        }
        
        return error_response