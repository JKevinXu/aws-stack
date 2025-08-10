#!/usr/bin/env python3
import boto3
import json
import time
from typing import Dict, Any, Optional

class StrandsAgentDeployer:
    """Deploy and manage Strands agent using Bedrock Agent Core"""
    
    def __init__(self, region: str = 'us-west-2'):
        self.region = region
        self.bedrock_client = boto3.client('bedrock-agent', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        
    def create_agent_role(self, role_name: str) -> str:
        """Create IAM role for Bedrock agent"""
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "bedrock.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Role for Strands Bedrock Agent"
            )
            
            # Attach required policies
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
            )
            
            return response['Role']['Arn']
            
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            response = self.iam_client.get_role(RoleName=role_name)
            return response['Role']['Arn']
    
    def create_lambda_execution_role(self, role_name: str) -> str:
        """Create IAM role for Lambda function"""
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Execution role for Strands Lambda functions"
            )
            
            # Attach basic Lambda execution policy
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            return response['Role']['Arn']
            
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            response = self.iam_client.get_role(RoleName=role_name)
            return response['Role']['Arn']
    
    def deploy_strands_agent(self, agent_name: str, agent_description: str) -> Dict[str, str]:
        """Deploy the Strands agent with Bedrock Agent Core"""
        
        # Create IAM role for the agent
        agent_role_arn = self.create_agent_role(f"{agent_name}-role")
        
        # Wait for role to be available
        time.sleep(10)
        
        agent_instruction = """
        You are the Strands agent, designed to help users with word puzzles and pattern recognition tasks.
        
        Your capabilities include:
        - Analyzing word patterns and relationships
        - Solving word connection puzzles
        - Providing hints and strategies for word games
        - Understanding semantic relationships between words
        
        When users present you with word puzzles:
        1. Analyze the given words for common themes, categories, or patterns
        2. Look for connections based on meaning, etymology, or wordplay
        3. Provide clear explanations for your reasoning
        4. Offer helpful hints without giving away complete solutions
        
        Always be encouraging and educational in your responses.
        """
        
        try:
            # Create the agent
            response = self.bedrock_client.create_agent(
                agentName=agent_name,
                description=agent_description,
                instruction=agent_instruction,
                foundationModel='anthropic.claude-3-5-sonnet-20240620-v1:0',
                agentResourceRoleArn=agent_role_arn,
                idleSessionTTLInSeconds=1800
            )
            
            agent_id = response['agent']['agentId']
            
            # Prepare the agent
            print(f"Preparing agent {agent_id}...")
            self.bedrock_client.prepare_agent(agentId=agent_id)
            
            # Wait for preparation to complete
            self._wait_for_agent_status(agent_id, 'PREPARED')
            
            # Create an alias
            alias_response = self.bedrock_client.create_agent_alias(
                agentId=agent_id,
                agentAliasName='live',
                description='Live alias for Strands agent'
            )
            
            agent_alias_id = alias_response['agentAlias']['agentAliasId']
            
            return {
                'agent_id': agent_id,
                'agent_alias_id': agent_alias_id,
                'agent_role_arn': agent_role_arn,
                'status': 'deployed'
            }
            
        except Exception as e:
            print(f"Error deploying agent: {str(e)}")
            raise
    
    def _wait_for_agent_status(self, agent_id: str, target_status: str, max_wait: int = 300):
        """Wait for agent to reach target status"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = self.bedrock_client.get_agent(agentId=agent_id)
            current_status = response['agent']['agentStatus']
            
            print(f"Agent status: {current_status}")
            
            if current_status == target_status:
                return
            elif current_status == 'FAILED':
                raise Exception(f"Agent preparation failed")
            
            time.sleep(10)
        
        raise Exception(f"Timeout waiting for agent to reach {target_status} status")
    
    def test_strands_agent(self, agent_id: str, agent_alias_id: str) -> bool:
        """Test the deployed Strands agent"""
        runtime_client = boto3.client('bedrock-agent-runtime', region_name=self.region)
        
        test_cases = [
            "Help me find connections between these words: RAINBOW, PRISM, SPECTRUM, LIGHT",
            "What patterns can you see in: APPLE, ORANGE, BANANA, GRAPE?",
            "Give me a hint for grouping: MARS, VENUS, JUPITER, EARTH, MERCURY"
        ]
        
        try:
            for i, test_input in enumerate(test_cases, 1):
                print(f"\nTest {i}: {test_input}")
                print("-" * 60)
                
                response = runtime_client.invoke_agent(
                    agentId=agent_id,
                    agentAliasId=agent_alias_id,
                    sessionId=f'strands-test-{i}',
                    inputText=test_input
                )
                
                # Process response
                for event in response['completion']:
                    if 'chunk' in event:
                        chunk = event['chunk']
                        if 'bytes' in chunk:
                            text = chunk['bytes'].decode('utf-8')
                            print(f"Agent Response: {text}")
                
                time.sleep(2)  # Brief pause between tests
            
            return True
            
        except Exception as e:
            print(f"Error testing agent: {str(e)}")
            return False

def main():
    """Main deployment function"""
    deployer = StrandsAgentDeployer()
    
    agent_config = {
        'name': 'strands-puzzle-agent',
        'description': 'AI agent specialized in word puzzles, pattern recognition, and connection games like Strands'
    }
    
    try:
        print("🎯 Deploying Strands Agent using Bedrock Agent Core...")
        print("=" * 60)
        
        # Deploy the agent
        result = deployer.deploy_strands_agent(
            agent_name=agent_config['name'],
            agent_description=agent_config['description']
        )
        
        print(f"\n✅ Strands Agent deployed successfully!")
        print(f"Agent ID: {result['agent_id']}")
        print(f"Agent Alias ID: {result['agent_alias_id']}")
        print(f"Role ARN: {result['agent_role_arn']}")
        
        # Test the deployed agent
        print("\n🧪 Testing deployed agent...")
        test_success = deployer.test_strands_agent(
            result['agent_id'], 
            result['agent_alias_id']
        )
        
        if test_success:
            print("\n🎉 Strands Agent is ready for word puzzle challenges!")
        else:
            print("\n⚠️ Agent deployed but testing encountered issues")
            
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")

if __name__ == "__main__":
    main()