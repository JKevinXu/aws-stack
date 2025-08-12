import json
import os
import time
import logging
import asyncio

from InlineAgent.tools.mcp import MCPHttpStreamable
from InlineAgent.action_group import ActionGroup
from InlineAgent.agent import InlineAgent

logger = logging.getLogger()
logger.setLevel(logging.INFO)

mcp_server_url = os.environ.get('MCP_SERVER_URL', 'https://sybw5cuj41.execute-api.us-west-2.amazonaws.com/prod/mcp')

async def process_with_bedrock(input_text: str) -> str:
    """Process request using Bedrock Inline Agent with MCP"""
    mcp_client = await MCPHttpStreamable.create(url=mcp_server_url)
    
    try:
        # Create action group and agent
        action_group = ActionGroup(name="MCPGroup", mcp_clients=[mcp_client])
        agent = InlineAgent(
            foundation_model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            instruction="You are a helpful AI assistant with MCP tools.",
            agent_name="mcp_agent",
            action_groups=[action_group]
        )
        
        # Process request
        return await agent.invoke(input_text=input_text)
        
    finally:
        await mcp_client.cleanup()

def lambda_handler(event, context):
    """Lambda handler with Bedrock Inline Agent integration"""
    # Log the incoming event and context for debugging
    logger.info(f"Event: {json.dumps(event, indent=2)}")
    logger.info(f"Context: {context}")
    logger.info(f"Context type: {type(context)}")
    if hasattr(context, '__dict__'):
        logger.info(f"Context attributes: {context.__dict__}")
    
    try:
        # Parse input
        body = json.loads(event.get('body', '{}')) if event.get('body') else event
        input_text = body.get('input')
        
        # Process with Bedrock agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response_text = loop.run_until_complete(process_with_bedrock(input_text))
        finally:
            loop.close()
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'success': True,
                'response': response_text,
                'sessionId': body.get('sessionId', f'session-{int(time.time() * 1000)}'),
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ', time.gmtime())
            })
        }
        
    except Exception as error:
        logger.error(f'Error: {str(error)}')
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(error),
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ', time.gmtime())
            })
        }

# For local testing
if __name__ == "__main__":
    test_event = {"input": "Please add 5 and 3 together using your available tools"}
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))