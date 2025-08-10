# AWS Bedrock AgentCore Deployment

This document describes the deployment and testing of AWS Bedrock AgentCore agents using the provided infrastructure.

## Overview

The infrastructure provides a streamlined way to deploy and invoke AWS Bedrock AgentCore agents with automatic IAM role creation, Docker containerization via CodeBuild, and response processing.

## Files Structure

```
├── deploy_agent.py          # Main deployment script
├── invoke_agent.py          # Agent invocation script
├── utils.py                 # IAM role creation utilities
├── requirements.txt         # Python dependencies
├── strands_claude.py        # Agent entrypoint
├── agent_arn.txt           # Generated agent ARN (gitignored)
├── .bedrock_agentcore.yaml # AgentCore config (gitignored)
├── Dockerfile              # Generated Docker config (gitignored)
└── .dockerignore          # Generated Docker ignore (gitignored)
```

## Prerequisites

1. AWS CLI configured with appropriate permissions
2. Python environment with required dependencies
3. AWS account with Bedrock AgentCore access

## Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `bedrock-agentcore-starter-toolkit` - AgentCore SDK
- `boto3` - AWS SDK
- `strands-agents` and `strands-agents-tools` - Agent framework

## Deployment Process

### 1. Deploy Agent

Run the deployment script to create IAM roles, configure the runtime, and launch the agent:

```bash
python deploy_agent.py
```

This script will:
- Create/update IAM role with necessary permissions for AgentCore
- Configure the AgentCore runtime with Docker containerization
- Launch the agent using CodeBuild for ARM64 container building
- Save the agent ARN to `agent_arn.txt` for invocation

**Expected Output:**
```
Region: us-west-2
Creating IAM role for agent: agentcore_strands
IAM Role ARN: arn:aws:iam::ACCOUNT:role/agentcore-agentcore_strands-role
Configuring and launching agentcore runtime...
🎉 CodeBuild completed successfully in ~2m
Agent ARN: arn:aws:bedrock-agentcore:us-west-2:ACCOUNT:runtime/agentcore_strands-ID
Agent ARN saved to agent_arn.txt
```

### 2. Invoke Agent

Test the deployed agent with a sample prompt:

```bash
python invoke_agent.py
```

This script will:
- Load the agent ARN from `agent_arn.txt`
- Invoke the deployed agent with a test message
- Process and display the response

**Expected Output:**
```
Region: us-west-2
Invoking agent: arn:aws:bedrock-agentcore:us-west-2:ACCOUNT:runtime/agentcore_strands-ID
Session ID: test-session-001
Input: Hello, can you help me with my task?

Invocation result:
Hello! I'd be happy to help you with your task. I can assist with:
1. Mathematical calculations - anything from basic arithmetic to advanced operations
2. Weather information - I can get current weather data for you
What specific task would you like help with?
```

## Configuration Details

### IAM Role Permissions

The deployment script creates an IAM role with permissions for:
- Bedrock model invocation
- ECR repository access
- CloudWatch logging
- X-Ray tracing
- AgentCore workload access tokens

### Runtime Configuration

- **Platform**: `linux/arm64`
- **Container Runtime**: Docker
- **Build Mode**: CodeBuild (cloud-based)
- **Network**: Public
- **Protocol**: HTTP
- **Observability**: Enabled

### Generated Files

During deployment, several files are automatically generated:
- `.bedrock_agentcore.yaml` - Runtime configuration
- `Dockerfile` - Container definition
- `.dockerignore` - Docker build exclusions
- `agent_arn.txt` - Agent ARN for invocation

## Monitoring and Logs

Agent logs are available in CloudWatch:
- Runtime logs: `/aws/bedrock-agentcore/runtimes/AGENT-ID-DEFAULT/runtime-logs`
- General logs: `/aws/bedrock-agentcore/runtimes/AGENT-ID-DEFAULT`

View logs using AWS CLI:
```bash
# Tail live logs
aws logs tail /aws/bedrock-agentcore/runtimes/AGENT-ID-DEFAULT --follow

# View recent logs
aws logs tail /aws/bedrock-agentcore/runtimes/AGENT-ID-DEFAULT --since 1h
```

## Troubleshooting

### Common Issues

1. **Agent already exists error**: 
   - The deployment script uses `auto_update_on_conflict=True` to handle this automatically

2. **IAM role conflicts**:
   - Script automatically deletes and recreates roles if they exist

3. **Build failures**:
   - Check CodeBuild logs in AWS Console
   - Verify dependencies in `requirements.txt`

4. **Invocation errors**:
   - Ensure `agent_arn.txt` exists and contains valid ARN
   - Check agent endpoint status in AWS Console

### Verification Steps

1. **Check agent status**:
   ```bash
   python -c "from bedrock_agentcore_starter_toolkit import Runtime; r = Runtime(); r.load_config(); print(r.status())"
   ```

2. **Validate agent ARN**:
   ```bash
   cat agent_arn.txt
   ```

3. **Test with different prompts**:
   Modify the `input_text` variable in `invoke_agent.py` to test various scenarios.

## Cleanup

To remove the deployed resources:

1. Delete the agent through AWS Console or CLI
2. Remove IAM roles created by the script
3. Delete ECR repository if no longer needed
4. Remove CodeBuild project

## Next Steps

- Customize `strands_claude.py` for specific use cases
- Add error handling and retry logic for production use
- Implement session management for multi-turn conversations
- Add authentication and authorization for production deployments