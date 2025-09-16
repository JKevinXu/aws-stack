from strands import Agent
from strands_tools import http_request
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from typing import Dict, Any, Optional
import json

# MCP server configuration
MCP_SERVER_URL = "https://bwzo9wnhy3.execute-api.us-west-2.amazonaws.com/beta/mcp"

# Define the MCP-enabled assistant system prompt
MCP_ASSISTANT_PROMPT = """You are a helpful AI assistant with access to external tools and services. You can:

1. Use specialized tools from connected MCP servers
2. Process and analyze various types of content

Choose the most appropriate tool for each task and provide clear explanations of your actions.
"""

# The handler function is called by the FastAPI wrapper in main.py
# for Bedrock Agent Core invocations.
def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Bedrock Agent Core handler function for Strands Agent with MCP integration
    
    Args:
        event: Bedrock Agent Core event (via FastAPI wrapper)
        context: Lambda context object (unused)
        
    Returns:
        Dictionary containing the agent's response
    """
    try:
        # Log the incoming event for debugging
        print(f"Received event: {json.dumps(event)}")
        
        # Handle Bedrock Agent Core event (via FastAPI wrapper)
        payload = event
        print(f"Bedrock Agent Core event: {payload}")
        
        print(f"Extracted payload: {json.dumps(payload)}")
        
        # Extract prompt from payload
        prompt = payload.get('prompt', '')
        if not prompt:
            return {
                'error': 'No prompt provided',
                'message': 'Please provide a prompt in the event payload'
            }
        
        # Extract MCP authorization token from Bedrock Agent Core payload
        mcp_authorization_token = event.get('mcp_authorization_token')
        
        print(f"MCP token status: {'Found' if mcp_authorization_token else 'Not found'}")
        
        # MCP is always enabled
        
        # Use the MCP-enabled assistant prompt
        system_prompt = MCP_ASSISTANT_PROMPT
        
        # Initialize tools list with basic HTTP request capability
        tools = [http_request]
        
        # Add MCP tools if authorization token is provided
        if mcp_authorization_token:
            try:
                # Configure MCP client with streamable HTTP transport
                # Add Bearer prefix automatically to the token
                headers = {"Authorization": f"Bearer {mcp_authorization_token}"}
                
                mcp_client = MCPClient(
                    lambda: streamablehttp_client(
                        url=MCP_SERVER_URL,
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
                    
                    # Return response for Bedrock Agent Core
                    return {
                        'response': str(response)
                    }
                    
            except Exception as mcp_error:
                # Log MCP error and fall back to basic functionality
                print(f"MCP connection failed: {mcp_error}")
                # Continue with basic tools only
                
        # Create agent with basic tools (fallback or when MCP token not provided)
        agent = Agent(
            system_prompt=system_prompt,
            tools=tools,
        )

        # Process the prompt through the agent
        response = agent(prompt)
        
        # Return response for Bedrock Agent Core
        return {
            'response': str(response)
        }
        
    except Exception as e:
        # Handle any errors that occur during processing
        print(f"Handler error: {str(e)}")
        
        # Return error response for Bedrock Agent Core
        return {
            'error': str(e),
            'message': 'An error occurred while processing the request'
        }
