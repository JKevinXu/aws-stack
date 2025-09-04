# Strands Agent AWS Lambda Deployment

This project implements a deployment of Strands Agent to AWS Lambda following the official [Strands Agent Lambda deployment documentation](https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_aws_lambda/).

## 🏗️ Architecture Overview

The deployment consists of:

1. **Lambda Function**: Runs the Strands Agent with HTTP request capabilities
2. **Lambda Layer**: Contains Python dependencies (strands-agents, strands-agents-tools, etc.)
3. **API Gateway**: REST API endpoint for invoking the agent
4. **Function URL**: Direct HTTPS endpoint for the Lambda function
5. **IAM Permissions**: Bedrock access for AI model usage

## 📁 Project Structure

```
aws-stack/
├── lambda/strands-agent/          # Lambda function code
│   ├── agent_handler.py           # Main Lambda handler
│   └── requirements.txt           # Python dependencies
├── lib/
│   └── strands-agent-lambda-stack.ts  # CDK infrastructure
├── bin/
│   ├── package_for_lambda.py      # Packaging script
│   └── aws-stack.ts              # Main CDK app
├── deploy-strands-agent.sh        # One-click deployment script
└── packaging/                     # Generated during deployment
    ├── app.zip                   # Application code ZIP
    ├── dependencies.zip          # Dependencies ZIP
    └── _dependencies/            # Extracted dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+ with npm
- AWS CLI configured with appropriate permissions
- AWS CDK v2 installed

### One-Click Deployment

```bash
./deploy-strands-agent.sh
```

This script will:
1. Package the Lambda function and dependencies
2. Build the TypeScript CDK code
3. Bootstrap CDK (if needed)
4. Deploy the Strands Agent Lambda stack

### Manual Deployment Steps

If you prefer to run each step manually:

```bash
# 1. Package for Lambda
python3 ./bin/package_for_lambda.py

# 2. Build CDK
npm run build

# 3. Bootstrap CDK (first time only)
npx cdk bootstrap

# 4. Deploy the stack
npx cdk deploy StrandsAgentLambdaStack
```

## 🧪 Testing the Deployment

### Using AWS CLI

```bash
aws lambda invoke --function-name StrandsAgentFunction \
  --region us-east-1 \
  --cli-binary-format raw-in-base64-out \
  --payload '{"prompt": "What is the weather in Seattle?"}' \
  output.json

# View the response
cat output.json
```

### Using Function URL

The CDK deployment will output a Function URL that you can use directly:

```bash
curl -X POST "https://your-function-url.lambda-url.us-east-1.on.aws/" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the weather in Seattle?"}'
```

### Using API Gateway

You can also use the API Gateway endpoint:

```bash
curl -X POST "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/agent" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the weather in Seattle?"}'
```

## 🔧 Configuration

### Agent Types

The agent handler supports multiple agent types via the `agent_type` parameter:

- `weather` (default): Weather-focused agent using National Weather Service API
- `general`: General-purpose assistant with web browsing capabilities

Example payload:
```json
{
  "prompt": "What is the weather in Seattle?",
  "agent_type": "weather"
}
```

### Environment Variables

The Lambda function includes these environment variables:
- `PYTHONPATH`: Set to include the Lambda layer and runtime paths

### Timeouts and Memory

- **Timeout**: 60 seconds (configurable in CDK)
- **Memory**: 512 MB (configurable in CDK)
- **Architecture**: ARM64 for cost optimization

## 🏛️ Infrastructure Details

### Lambda Layer Structure

The dependencies are packaged in a Lambda layer following AWS best practices:
- All Python packages are installed for ARM64 architecture
- Dependencies are placed in `/opt/python/` structure
- Layer is compatible with Python 3.12 runtime

### IAM Permissions

The Lambda function has permissions for:
- **Bedrock**: Model invocation and streaming
- **CloudWatch Logs**: Function logging
- **Foundation Models**: Bedrock model access

### API Gateway Configuration

- **CORS**: Enabled for all origins and methods
- **Integration**: Lambda proxy integration
- **Endpoint**: `/agent` POST method

## 📊 Outputs

After deployment, the CDK will output:

- **StrandsAgentFunctionName**: Lambda function name
- **StrandsAgentFunctionArn**: Lambda function ARN  
- **StrandsAgentApiUrl**: API Gateway base URL
- **StrandsAgentFunctionUrl**: Direct Lambda function URL
- **DependenciesLayerArn**: Lambda layer ARN

## 🔍 Troubleshooting

### Common Issues

1. **Packaging Errors**: Ensure Python 3.12+ is installed and pip is up to date
2. **CDK Bootstrap**: Run `npx cdk bootstrap` if deploying for the first time
3. **Dependencies**: Check that all packages install correctly for ARM64 architecture
4. **Permissions**: Ensure your AWS credentials have sufficient permissions

### Viewing Logs

```bash
aws logs tail /aws/lambda/StrandsAgentFunction --follow
```

### Updating the Function

To update just the function code without redeploying infrastructure:

```bash
python3 ./bin/package_for_lambda.py
aws lambda update-function-code \
  --function-name StrandsAgentFunction \
  --zip-file fileb://packaging/app.zip
```

## 🔄 CI/CD Integration

This deployment can be integrated into CI/CD pipelines:

1. Add the packaging and deployment commands to your pipeline
2. Use AWS credentials from your CI/CD environment
3. Consider using CDK Pipelines for automated deployments

## 📚 Related Resources

- [Strands Agent Documentation](https://strandsagents.com/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

## 🤝 Contributing

To modify or extend this deployment:

1. Update the agent handler in `lambda/strands-agent/agent_handler.py`
2. Modify infrastructure in `lib/strands-agent-lambda-stack.ts`
3. Update dependencies in `lambda/strands-agent/requirements.txt`
4. Test locally before deploying

## 📄 License

This implementation follows the AWS CDK licensing and the Strands Agent licensing terms.
