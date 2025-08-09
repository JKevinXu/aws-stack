#!/usr/bin/env python3
"""
AWS Bedrock Inline Agent with MCP Integration
Uses the existing MCP server to demonstrate inline agent capabilities
"""

import asyncio
import json
from typing import Dict, Any, List
import boto3
import logging

# Import our new MCP client
from mcp_client import MCPSDKClient, MCPClientFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                    print(f"Connected to server with tools: {tool_names}")
                    
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
    Simplified version for demonstration purposes
    """
    
    def __init__(self, foundation_model: str, instruction: str, agent_name: str, action_groups: List[ActionGroup]):
        self.foundation_model = foundation_model
        self.instruction = instruction
        self.agent_name = agent_name
        self.action_groups = action_groups
        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-west-2')
    
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
            
            print(f"\nThought: {assistant_message}")
            
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
                    import re
                    json_match = re.search(r'\{[^{}]*"tool_name"[^{}]*\}', assistant_message)
                    if json_match:
                        try:
                            tool_call_json = json.loads(json_match.group())
                        except json.JSONDecodeError:
                            pass
                
                if tool_call_json and 'tool_name' in tool_call_json and 'arguments' in tool_call_json:
                    tool_name = tool_call_json['tool_name']
                    arguments = tool_call_json['arguments']
                    
                    print(f"\nTool use: {tool_name} with inputs: {arguments}")
                    
                    # Execute the tool
                    try:
                        for action_group in self.action_groups:
                            tool_result = await action_group.execute_tool(tool_name, arguments)
                            
                            if 'result' in tool_result:
                                result_content = tool_result['result']['content'][0]['text']
                                print(f"\nTool result: {result_content}")
                                
                                # Add tool result to conversation
                                messages.append({
                                    "role": "user",
                                    "content": [{"text": f"Tool '{tool_name}' returned: {result_content}"}]
                                })
                                break
                            else:
                                print(f"Tool execution error: {tool_result}")
                                messages.append({
                                    "role": "user",
                                    "content": [{"text": f"Tool '{tool_name}' failed: {tool_result}"}]
                                })
                                break
                    
                    except Exception as e:
                        error_msg = f"Tool execution failed: {str(e)}"
                        print(f"\nError: {error_msg}")
                        messages.append({
                            "role": "user",
                            "content": [{"text": error_msg}]
                        })
                else:
                    # Not a tool call, return the response
                    return assistant_message
                    
            except Exception as e:
                # Error parsing, return as is
                return assistant_message
        
        return "Maximum iterations reached. Please try again with a simpler request."

async def main():
    """Main function to demonstrate the inline agent with MCP integration"""
    
    # Your existing MCP server URL
    mcp_server_url = "https://sybw5cuj41.execute-api.us-west-2.amazonaws.com/prod/mcp"
    
    # Create MCP client using the factory
    mcp_client = MCPClientFactory.create_sdk_client(mcp_server_url)
    
    # Create action group with MCP client
    action_group = ActionGroup(
        name="MathActionGroup",
        mcp_clients=[mcp_client]
    )
    
    # Create inline agent
    agent = InlineAgent(
        foundation_model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instruction="You are a helpful assistant that can perform mathematical calculations using available tools. When asked to perform calculations, use the appropriate tools to get accurate results.",
        agent_name="MathAgent",
        action_groups=[action_group]
    )
    
    # Test queries
    test_queries = [
        "What tools do you have available?",
        "Add 15 and 27",
        "Calculate 100 plus 50",
        "What's 7 + 8?"
    ]
    
    for query in test_queries:
        print(f"\n" + "="*60)
        print(f"Query: {query}")
        print("="*60)
        
        try:
            result = await agent.invoke(query)
            print(f"\nFinal Answer: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            # Clean up MCP connections
            await agent.close()
        
        print("\n" + "-"*60)

if __name__ == "__main__":
    # Install required dependencies if not present - MCP SDK is now used instead of aiohttp
    try:
        from mcp_client import MCPSDKClient
    except ImportError:
        print("MCP client module not found. Make sure mcp_client.py is in the same directory.")
        exit(1)
    
    # Run the demonstration
    asyncio.run(main())