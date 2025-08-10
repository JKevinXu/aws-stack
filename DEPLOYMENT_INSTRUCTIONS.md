# Bedrock Agent Core Proxy - Deployment Instructions

## Quick Start

Follow these steps to deploy the proxy and start using it with your external website:

### 1. Deploy the Infrastructure

```bash
# Navigate to your project directory
cd /Users/kx/ws/aws-stack

# Install dependencies (if not already done)
npm install

# Build the CDK project
npm run build

# Deploy the proxy stack
npx cdk deploy BedrockAgentCoreProxyStack
```

### 2. Note the Deployment Outputs

After deployment, CDK will output important URLs. Note these values:

```
BedrockAgentCoreProxyStack.ApiEndpoint = https://abcd1234.execute-api.us-west-2.amazonaws.com/prod/
BedrockAgentCoreProxyStack.ApiUrl = https://abcd1234.execute-api.us-west-2.amazonaws.com/prod/agent/invoke
BedrockAgentCoreProxyStack.LambdaFunctionArn = arn:aws:lambda:us-west-2:ACCOUNT:function:BedrockAgentCoreProxyStack-...
```

### 3. Configure Environment Variables (Optional)

Set these environment variables in the Lambda function for enhanced functionality:

```bash
# Set your default agent ARN (already configured in the code)
DEFAULT_AGENT_ARN=arn:aws:bedrock-agentcore:us-west-2:313117444016:runtime/agentcore_strands-fRvDuw6SOI

# Configure API keys for authentication
VALID_API_KEYS=key1,key2,key3

# Set environment mode
NODE_ENV=production
```

To update Lambda environment variables:

```bash
aws lambda update-function-configuration \
  --function-name YOUR-LAMBDA-FUNCTION-NAME \
  --environment Variables='{
    "DEFAULT_AGENT_ARN": "arn:aws:bedrock-agentcore:us-west-2:313117444016:runtime/agentcore_strands-fRvDuw6SOI",
    "VALID_API_KEYS": "your-secret-key-1,your-secret-key-2",
    "NODE_ENV": "production"
  }'
```

### 4. Test the Deployment

Update the test script with your API Gateway URL:

```bash
# Edit test-proxy.js and update the apiUrl
nano test-proxy.js

# Run the test
node test-proxy.js
```

### 5. Integration with Your Website

Use the API endpoint in your external website:

#### JavaScript/React Example:

```javascript
const response = await fetch('https://YOUR-API-GATEWAY-URL/prod/agent/invoke', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': 'your-api-key'  // Optional if using dev mode
  },
  body: JSON.stringify({
    input: 'Hello, how can you assist me today?',
    qualifier: 'DEFAULT',  // Optional
    sessionId: 'user-session-123'  // Optional
  })
});

const data = await response.json();
console.log('Agent response:', data.response);
```

#### cURL Example:

```bash
curl -X POST https://YOUR-API-GATEWAY-URL/prod/agent/invoke \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: your-api-key" \
  -d '{
    "input": "Hello, how can you assist me today?",
    "qualifier": "DEFAULT",
    "sessionId": "test-session-123"
  }'
```

## API Reference

### Endpoints

1. **POST /agent/invoke** - Invoke the Bedrock agent
2. **GET /agent/health** - Health check
3. **GET /agent/sessions/{sessionId}** - Session info

### Request Format for /agent/invoke

```json
{
  "input": "Your message to the agent (required)",
  "agentArn": "Agent ARN (optional, uses default if not provided)",
  "qualifier": "Endpoint qualifier (optional, defaults to 'DEFAULT')",
  "sessionId": "Session identifier (optional, auto-generated if not provided)"
}
```

### Response Format

```json
{
  "success": true,
  "response": "Agent's response text",
  "agentArn": "arn:aws:bedrock-agentcore:us-west-2:313117444016:runtime/agentcore_strands-fRvDuw6SOI",
  "qualifier": "DEFAULT",
  "sessionId": "session-1234567890",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Authentication Methods

### 1. Development Mode (No Auth Required)
For localhost development, requests are automatically allowed from:
- http://localhost:3000
- http://localhost:3001
- http://127.0.0.1:3000
- https://localhost:3000

### 2. API Key Authentication
Include header: `X-Api-Key: your-secret-key`

### 3. Bearer Token Authentication
Include header: `Authorization: Bearer your-jwt-token`

### 4. AWS Signature v4
Use AWS SDK signing for server-to-server communication.

## Security Configuration

### For Production Use:

1. **Set API Keys**: Configure `VALID_API_KEYS` environment variable
2. **Enable Production Mode**: Set `NODE_ENV=production`
3. **Restrict CORS**: Update the CDK stack to limit allowed origins
4. **Monitor Usage**: Enable CloudWatch logging and monitoring

### Update CORS for Production:

Edit `lib/bedrock-agentcore-proxy-stack.ts`:

```typescript
defaultCorsPreflightOptions: {
  allowOrigins: ['https://yourwebsite.com'],  // Replace with your domain
  allowMethods: ['POST', 'GET', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization', 'X-Api-Key']
}
```

Then redeploy:

```bash
npm run build
npx cdk deploy BedrockAgentCoreProxyStack
```

## Troubleshooting

### Common Issues:

1. **502 Bad Gateway**: Lambda function error - check CloudWatch logs
2. **401 Unauthorized**: Authentication failed - verify API key or auth method
3. **403 Forbidden**: IAM permissions issue - check Lambda execution role
4. **CORS errors**: Update CORS configuration in CDK stack

### Check Logs:

```bash
# View Lambda logs
aws logs tail /aws/lambda/BedrockAgentCoreProxyStack-AgentCoreProxyFunction --follow

# View API Gateway logs  
aws logs tail API-Gateway-Execution-Logs_YOUR-API-ID/prod --follow
```

## Cost Optimization

- The proxy adds minimal cost (API Gateway + Lambda invocation)
- Lambda is billed per request and execution time
- API Gateway is billed per request
- Monitor usage through CloudWatch metrics

## Next Steps

1. **Custom Authentication**: Implement JWT validation or OAuth integration
2. **Rate Limiting**: Add request throttling per user/API key
3. **Caching**: Implement response caching for common queries
4. **Monitoring**: Set up comprehensive monitoring and alerts
5. **Load Testing**: Test the proxy under expected traffic loads

For detailed configuration options, see `BEDROCK_AGENTCORE_PROXY_GUIDE.md`.