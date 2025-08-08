#!/usr/bin/env python3
import boto3
import json
import time

def test_bedrock_agent():
    """Test the Bedrock MCP agent"""
    
    # Initialize Bedrock agent runtime client
    client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    
    agent_id = '5P2V4NOJIY'
    agent_alias_id = 'D7BVF65I0Z'
    
    try:
        print("🚀 Testing Bedrock Agent for MCP Server...")
        print(f"Agent ID: {agent_id}")
        print(f"Alias ID: {agent_alias_id}")
        print("-" * 50)
        
        # Test 1: Initialize MCP server
        print("Test 1: Testing MCP server initialization")
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId='test-session-001',
            inputText="Please test the MCP server initialization to verify it's working correctly"
        )
        
        # Process response
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    print(f"Response: {text}")
        
        print("\n" + "="*50)
        
        # Test 2: List MCP tools
        print("Test 2: Listing available MCP tools")
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId='test-session-002',
            inputText="List all available tools from the MCP server"
        )
        
        # Process response
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    print(f"Response: {text}")
        
        print("\n" + "="*50)
        
        # Test 3: Execute MCP tool
        print("Test 3: Executing the add tool with parameters")
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId='test-session-003',
            inputText='Call the add tool from the MCP server with numbers 15 and 25'
        )
        
        # Process response
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    print(f"Response: {text}")
                    
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Error testing agent: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_bedrock_agent()