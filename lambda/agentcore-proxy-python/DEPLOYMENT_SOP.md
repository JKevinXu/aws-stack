# Lambda Deployment SOP - AgentCore Proxy Python

## Overview
This document outlines the standard operating procedure for deploying the AgentCore Proxy Python Lambda function with InlineAgent dependencies.

## Prerequisites
- AWS CLI configured with appropriate credentials
- Python 3.11 installed
- ZIP utility available
- IAM role for Lambda execution with necessary permissions
- Access to InlineAgent source code repository

## Critical Requirements
- **MCP Package Version**: Must use `mcp>=1.12.4` (not 1.6.0) for `streamable_http` support
- **InlineAgent Package**: Must be copied directly into deployment package (not available on PyPI)
- **Platform-specific binaries**: Must use Linux-compatible packages for Lambda runtime

## File Structure Required
```
/Users/kevinxu/ws4/aws-stack/lambda/agentcore-proxy-python/
├── lambda_function_new.py      # Main Lambda handler
├── requirements.txt             # Python dependencies
├── InlineAgent/                 # Copy of InlineAgent source code
│   ├── __init__.py
│   ├── tools/
│   │   └── mcp.py              # Contains MCPHttpStreamable class
│   ├── agent/
│   ├── action_group/
│   └── ...
└── deploy.sh                    # Deployment script (optional)
```

## Deployment Steps

### 1. Prepare Environment
```bash
cd /Users/kevinxu/ws4/aws-stack/lambda/agentcore-proxy-python
```

### 2. Copy InlineAgent Source Code
```bash
# Copy only the source code directory (not the entire package structure)
cp -r /Users/kevinxu/ws4/amazon-bedrock-agent-samples/src/InlineAgent/src/InlineAgent ./
```

### 3. Update requirements.txt
Ensure the requirements.txt contains:
```
boto3==1.37.21
pydantic==2.10.2
termcolor==2.5.0
rich==13.9.4
opentelemetry-api==1.31.1
opentelemetry-sdk==1.31.1
opentelemetry-exporter-otlp==1.31.1
openinference-semantic-conventions==0.1.16
pydantic-settings==2.8.1
wrapt==1.17.2
botocore==1.37.23
mcp>=1.12.4  # Critical: Must be >=1.12.4, not 1.6.0
```

### 4. Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 5. Install Dependencies with Linux Binaries
```bash
pip install --upgrade pip
mkdir -p package

# Install with platform-specific binaries for Lambda
pip install -r requirements.txt -t ./package \
    --platform manylinux2014_x86_64 \
    --python-version 3.11 \
    --only-binary :all:
```

### 6. Copy Application Code to Package
```bash
cp -r InlineAgent ./package/
cp lambda_function_new.py ./package/
```

### 7. Create Deployment Package
```bash
cd package
zip -r ../lambda-deployment.zip . -x "*.pyc" -x "*__pycache__*" -x "*.DS_Store"
cd ..

# Verify package size (should be ~27-28MB)
ls -lh lambda-deployment.zip
```

### 8. Deploy to AWS Lambda

#### Option A: Create New Function
```bash
aws lambda create-function \
    --function-name agentcore-proxy-python \
    --runtime python3.11 \
    --role arn:aws:iam::313117444016:role/lambda-execution-role \
    --handler lambda_function_new.lambda_handler \
    --zip-file fileb://lambda-deployment.zip \
    --timeout 300 \
    --memory-size 1024 \
    --environment Variables={MCP_SERVER_URL=https://sybw5cuj41.execute-api.us-west-2.amazonaws.com/prod/mcp} \
    --description "AgentCore Proxy Python Lambda with InlineAgent"
```

#### Option B: Update Existing Function
```bash
# Update code
aws lambda update-function-code \
    --function-name agentcore-proxy-python \
    --zip-file fileb://lambda-deployment.zip

# Update configuration if needed
aws lambda update-function-configuration \
    --function-name agentcore-proxy-python \
    --timeout 300 \
    --memory-size 1024 \
    --environment Variables={MCP_SERVER_URL=https://sybw5cuj41.execute-api.us-west-2.amazonaws.com/prod/mcp}
```

### 9. Test Deployment
```bash
# Basic test
aws lambda invoke \
    --function-name agentcore-proxy-python \
    --payload '{"input":"Hello, can you help me?"}' \
    --cli-binary-format raw-in-base64-out \
    response.json

# Mathematical calculation test
aws lambda invoke \
    --function-name agentcore-proxy-python \
    --payload '{"input":"What is 384938493843948398439 + 348938439483948?"}' \
    --cli-binary-format raw-in-base64-out \
    calculation-test.json

# View response
cat response.json | python3 -m json.tool
```

## Automated Deployment Script
Use the included `deploy.sh` script for automated deployment:
```bash
# For new function creation
./deploy.sh create agentcore-proxy-python arn:aws:iam::ACCOUNT:role/ROLE_NAME

# For updating existing function
./deploy.sh update agentcore-proxy-python
```

## Troubleshooting

### Common Issues and Solutions

1. **ModuleNotFoundError: No module named 'mcp.client.streamable_http'**
   - **Cause**: Using mcp version < 1.12.4
   - **Solution**: Update requirements.txt to use `mcp>=1.12.4`

2. **ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'**
   - **Cause**: Missing Linux-compatible binary packages
   - **Solution**: Use `--platform manylinux2014_x86_64` when installing packages

3. **ImportError for InlineAgent modules**
   - **Cause**: InlineAgent source not properly copied
   - **Solution**: Ensure InlineAgent directory is copied to package directory

4. **Package size exceeds Lambda limits**
   - **Cause**: Too many dependencies or unnecessary files
   - **Solution**: Exclude unnecessary files with -x flag in zip command

## Cleanup
```bash
deactivate  # Exit virtual environment
rm -rf venv package
# Keep lambda-deployment.zip as backup
```

## Verification Checklist
- [ ] Lambda function created/updated successfully
- [ ] Function responds to test invocations
- [ ] CloudWatch logs show no errors
- [ ] Mathematical calculations work correctly
- [ ] MCP server connection established

## Rollback Procedure
If deployment fails:
1. Keep previous `lambda-deployment.zip` as backup
2. Use `aws lambda update-function-code --zip-file fileb://previous-deployment.zip`
3. Verify rollback with test invocation
4. Check CloudWatch logs for issues

## Important Notes
- Lambda function requires Python 3.11 runtime
- IAM role must have permissions for Bedrock service
- MCP_SERVER_URL environment variable must be set correctly
- Package size limit is 50MB (zipped), 250MB (unzipped)
- Current deployment package size: ~27-28MB

## Successfully Deployed Configuration
- **Function Name**: agentcore-proxy-python
- **Region**: us-west-2
- **Runtime**: Python 3.11
- **Memory**: 1024 MB
- **Timeout**: 300 seconds
- **Handler**: lambda_function_new.lambda_handler
- **MCP Version**: 1.12.4+
- **InlineAgent**: Embedded in package