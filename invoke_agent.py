"""
Invocation script for AWS Bedrock AgentCore
Handles agent execution and interaction
"""
import sys
import os
import json
import boto3
from boto3.session import Session


def setup_path():
    """Add utils directory to Python path"""
    current_dir = os.path.dirname(os.path.abspath('__file__' if '__file__' in globals() else '.'))
    utils_dir = os.path.join(current_dir, '..', '..')
    utils_dir = os.path.abspath(utils_dir)
    
    sys.path.insert(0, utils_dir)


def load_agent_arn():
    """Load agent ARN from file"""
    try:
        with open('agent_arn.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Agent ARN file not found. Please run deploy_agent.py first.")
        return None


def invoke_agent(agent_arn, region, session_id=None, input_text=""):
    """Invoke the deployed agent with input text"""
    agentcore_client = boto3.client('bedrock-agentcore', region_name=region)
    
    print(f"Invoking agent: {agent_arn}")
    print(f"Session ID: {session_id}")
    print(f"Input: {input_text}")
    
    response = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        qualifier="DEFAULT",
        payload=json.dumps({"prompt": input_text})
    )
    
    return response


def process_response(response):
    """Process and display the agent response"""
    if "text/event-stream" in response.get("contentType", ""):
        content = []
        for line in response["response"].iter_lines(chunk_size=1):
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[6:]
                    print(line)
                    content.append(line)
        return "\n".join(content)
    else:
        try:
            events = []
            for event in response.get("response", []):
                events.append(event)
            if events:
                return json.loads(events[0].decode("utf-8"))
        except Exception as e:
            return f"Error reading response: {e}"
    
    return response


def main():
    """Main invocation function"""
    setup_path()
    
    # Get AWS region
    boto_session = Session()
    region = boto_session.region_name
    print(f"Region: {region}")
    
    # Load agent ARN
    agent_arn = load_agent_arn()
    if not agent_arn:
        return None
    
    # Configuration
    session_id = "test-session-001"
    input_text = "Hello, can you help me with my task?"
    
    # Invoke agent
    result = invoke_agent(
        agent_arn=agent_arn,
        region=region,
        session_id=session_id,
        input_text=input_text
    )
    
    # Process response
    processed_result = process_response(result)
    
    return processed_result


if __name__ == "__main__":
    result = main()
    print("\nInvocation result:")
    print(result)