from strands import Agent
from strands_tools import http_request
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from typing import Dict, Any, Optional
import json

# Define the MCP-enabled assistant system prompt
MCP_ASSISTANT_PROMPT = """You are a helpful AI assistant with access to external tools and services. You can:

1. Use specialized tools from connected MCP servers
2. Process and analyze various types of content

Choose the most appropriate tool for each task and provide clear explanations of your actions.
"""

# The handler function signature `def handler(event, context)` is what Lambda
# looks for when invoking your function.
def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    AWS Lambda handler function for Strands Agent with MCP integration
    
    Args:
        event: Lambda event containing the prompt, optional configuration, and MCP authorization token
        context: Lambda context object
        
    Returns:
        Dictionary containing the agent's response
    """
    try:
        # Extract prompt from event
        prompt = event.get('prompt', '')
        if not prompt:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No prompt provided',
                    'message': 'Please provide a prompt in the event payload'
                })
            }
        
        # Extract MCP configuration
        mcp_authorization_token = event.get('mcp_authorization_token')
        use_mcp = event.get('use_mcp', True)  # Enable MCP by default
        
        # Use the MCP-enabled assistant prompt
        system_prompt = MCP_ASSISTANT_PROMPT
        
        # Initialize tools list with basic HTTP request capability
        tools = [http_request]
        
        # Add MCP tools if enabled and authorization token is provided
        if use_mcp and mcp_authorization_token:
            try:
                # Configure MCP client with streamable HTTP transport
                mcp_url = "https://bwzo9wnhy3.execute-api.us-west-2.amazonaws.com/beta/mcp"
                # Add Bearer prefix automatically to the token
                headers = {"Authorization": f"Bearer {mcp_authorization_token}"}
                
                mcp_client = MCPClient(
                    lambda: streamablehttp_client(
                        url=mcp_url,
                        headers=headers
                    )
                )
                
                # Use MCP client within context manager as required by the protocol
                with mcp_client:
                    # Get tools from MCP server
                    mcp_tools = mcp_client.list_tools_sync()
                    tools.extend(mcp_tools)
                    
                    # Create the Strands agent with all available tools
                    agent = Agent(
                        system_prompt=system_prompt,
                        tools=tools,
                    )

                    # Process the prompt through the agent
                    response = agent(prompt)
                    
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({
                            'response': str(response),
                            'mcp_enabled': True,
                            'mcp_tools_count': len(mcp_tools),
                            'prompt': prompt
                        })
                    }
                    
            except Exception as mcp_error:
                # Log MCP error and fall back to basic functionality
                print(f"MCP connection failed: {mcp_error}")
                # Continue with basic tools only
                
        # Create agent with basic tools (fallback or when MCP is disabled)
        agent = Agent(
            system_prompt=system_prompt,
            tools=tools,
        )

        # Process the prompt through the agent
        response = agent(prompt)
        
        # Return the response in the expected Lambda format
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': str(response),
                'mcp_enabled': False,
                'mcp_tools_count': 0,
                'prompt': prompt
            })
        }
        
    except Exception as e:
        # Handle any errors that occur during processing
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'An error occurred while processing the request'
            })
        }
