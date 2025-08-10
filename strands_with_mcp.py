#!/usr/bin/env python3
"""
Strands Agent with MCP Integration
Combines Strands framework with MCP tools for enhanced capabilities
"""

gatewayURL = "https://sybw5cuj41.execute-api.us-west-2.amazonaws.com/prod/mcp"

import asyncio
from strands import Agent, tool
from strands_tools import calculator
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel
from mcp_client import MCPSDKClient, MCPClientFactory
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()

# Create MCP tool wrapper
@tool
async def mcp_tool(name: str, arguments: dict):
    """Execute MCP tools via gateway"""
    try:
        mcp_client = MCPClientFactory.create_sdk_client(gatewayURL)
        async with mcp_client:
            result = await mcp_client.call_tool(name, arguments)
            return result.get("result", {}).get("content", [{}])[0].get("text", str(result))
    except Exception as e:
        logger.error(f"MCP tool execution failed: {e}")
        return f"Error executing MCP tool {name}: {str(e)}"

# Model configuration
model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
model = BedrockModel(model_id=model_id)

# Create agent with MCP tools
agent = Agent(
    model=model,
    tools=[calculator, mcp_tool],
    system_prompt="You're a helpful assistant with access to calculator and MCP tools. Use MCP tools for advanced functionality."
)

@app.entrypoint
def strands_agent_with_mcp(payload):
    """
    Invoke the agent with MCP integration
    """
    user_input = payload.get("prompt", "")
    print(f"User input: {user_input}")
    
    try:
        response = agent(user_input)
        return response.message['content'][0]['text']
    except Exception as e:
        logger.error(f"Agent invocation failed: {e}")
        return f"Error processing request: {str(e)}"

async def list_mcp_tools():
    """List available MCP tools from the gateway"""
    try:
        mcp_client = MCPClientFactory.create_sdk_client(gatewayURL)
        async with mcp_client:
            tools_response = await mcp_client.list_tools()
            tools = tools_response.get("result", {}).get("tools", [])
            print("Available MCP tools:")
            for tool in tools:
                print(f"- {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            return tools
    except Exception as e:
        logger.error(f"Failed to list MCP tools: {e}")
        return []

if __name__ == "__main__":
    # List available tools first
    print("Initializing Strands agent with MCP integration...")
    asyncio.run(list_mcp_tools())
    
    # Run the agent
    app.run()