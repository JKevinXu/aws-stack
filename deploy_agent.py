"""
Deployment script for AWS Bedrock AgentCore
Creates IAM role and configures the agentcore runtime
"""
import sys
import os
from boto3.session import Session
from bedrock_agentcore_starter_toolkit import Runtime


def setup_path():
    """Add utils directory to Python path"""
    current_dir = os.path.dirname(os.path.abspath('__file__' if '__file__' in globals() else '.'))
    utils_dir = os.path.join(current_dir, '..', '..')
    utils_dir = os.path.abspath(utils_dir)
    
    sys.path.insert(0, utils_dir)
    print(f"sys.path[0]: {utils_dir}")


def create_iam_role(agent_name):
    """Create IAM role for the agent"""
    from utils import create_agentcore_role
    return create_agentcore_role(agent_name=agent_name)


def deploy_and_launch_agent(agent_name, iam_role_arn, region):
    """Configure and launch the agentcore runtime"""
    agentcore_runtime = Runtime()
    
    # Configure runtime
    config_response = agentcore_runtime.configure(
        entrypoint="strands_claude.py",
        execution_role=iam_role_arn,
        auto_create_ecr=True,
        requirements_file="requirements.txt",
        region=region,
        agent_name=agent_name
    )
    
    # Launch the agent with auto-update
    launch_response = agentcore_runtime.launch(auto_update_on_conflict=True)
    
    return config_response, launch_response


def main():
    """Main deployment function"""
    setup_path()
    
    # Configuration
    agent_name = "agentcore_strands"
    
    # Get AWS region
    boto_session = Session()
    region = boto_session.region_name
    print(f"Region: {region}")
    
    # Create IAM role
    print(f"Creating IAM role for agent: {agent_name}")
    agentcore_iam_role = create_iam_role(agent_name)
    iam_role_arn = agentcore_iam_role['Role']['Arn']
    print(f"IAM Role ARN: {iam_role_arn}")
    
    # Configure and launch runtime
    print("Configuring and launching agentcore runtime...")
    config_response, launch_response = deploy_and_launch_agent(agent_name, iam_role_arn, region)
    
    # Extract agent ARN
    agent_arn = launch_response.agent_arn
    print(f"Agent ARN: {agent_arn}")
    
    # Save agent ARN to a file for invocation script
    with open('agent_arn.txt', 'w') as f:
        f.write(agent_arn)
    print("Agent ARN saved to agent_arn.txt")
    
    return {
        'config_response': config_response,
        'launch_response': launch_response,
        'agent_arn': agent_arn
    }


if __name__ == "__main__":
    result = main()
    print("\nDeployment result:")
    print(result)