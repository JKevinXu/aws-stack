# Bedrock Agent Core Proxy - IAM Authentication Guide

## Overview

This guide explains how to use the Bedrock Agent Core Proxy to securely invoke your Bedrock agents from external websites with proper IAM authentication. The proxy provides a secure gateway that handles authentication and forwards requests to your Bedrock Agent Core instances.

## Architecture

```
External Website → API Gateway → Lambda Proxy → Bedrock Agent Core
                     ↓
                 Authentication
                 (API Key, JWT, AWS Sig)
```

### Components

1. **API Gateway**: Public endpoint with CORS support for web applications
2. **Lambda Proxy**: Authentication layer and request forwarding
3. **IAM Roles**: Secure permissions for Bedrock Agent Core access
4. **Bedrock Agent Core**: Your deployed AI agents

## Deployment

### 1. Deploy the Proxy Stack

```bash
# Build the CDK project
npm run build

# Deploy the proxy stack
npx cdk deploy BedrockAgentCoreProxyStack
```

### 2. Configure Environment Variables

After deployment, configure these environment variables in the Lambda function:

```bash
# Optional: Set a default agent ARN
DEFAULT_AGENT_ARN=arn:aws:bedrock-agentcore:us-west-2:ACCOUNT:runtime/agentcore_strands-ID

# For API Key authentication
VALID_API_KEYS=key1,key2,key3

# Environment mode
NODE_ENV=production
```

## Authentication Methods

The proxy supports multiple authentication methods:

### 1. API Key Authentication

Add an `X-Api-Key` header to your requests:

```javascript
fetch('https://your-api-gateway-url/prod/agent/invoke', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': 'your-api-key'
  },
  body: JSON.stringify({
    agentArn: 'arn:aws:bedrock-agentcore:us-west-2:ACCOUNT:runtime/your-agent',
    input: 'Hello, can you help me?',
    sessionId: 'optional-session-id'
  })
})
```

### 2. Bearer Token Authentication

Use JWT or other bearer tokens:

```javascript
fetch('https://your-api-gateway-url/prod/agent/invoke', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-jwt-token'
  },
  body: JSON.stringify({
    agentArn: 'arn:aws:bedrock-agentcore:us-west-2:ACCOUNT:runtime/your-agent',
    input: 'Hello, can you help me?'
  })
})
```

### 3. AWS Signature v4

For server-to-server communication using AWS credentials:

```javascript
import { SignatureV4 } from '@aws-sdk/signature-v4';

// Use AWS SDK's signing capabilities
const signedRequest = await signRequest(request, credentials);
```

### 4. Development Mode (Origin-based)

For development only, requests from allowed localhost origins are permitted:

```javascript
// Automatically allowed in non-production mode from:
// - http://localhost:3000
// - http://localhost:3001  
// - http://127.0.0.1:3000
// - https://localhost:3000
```

## API Endpoints

### POST /agent/invoke

Invoke a Bedrock Agent Core agent:

**Request Body:**
```json
{
  "agentArn": "arn:aws:bedrock-agentcore:us-west-2:ACCOUNT:runtime/your-agent",
  "input": "Your message to the agent",
  "sessionId": "optional-session-id"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Agent's response text",
  "sessionId": "session-12345",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### GET /agent/health

Health check endpoint:

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0.0"
}
```

### GET /agent/sessions/{sessionId}

Get session information:

**Response:**
```json
{
  "sessionId": "session-12345",
  "status": "active", 
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Integration Examples

### React Application

```javascript
import React, { useState } from 'react';

function BedrockChat() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    setLoading(true);
    try {
      const res = await fetch('https://your-api-gateway-url/prod/agent/invoke', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Api-Key': process.env.REACT_APP_BEDROCK_API_KEY
        },
        body: JSON.stringify({
          input: message,
          sessionId: `session-${Date.now()}`
        })
      });

      const data = await res.json();
      setResponse(data.response);
    } catch (error) {
      console.error('Error:', error);
      setResponse('Error communicating with agent');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input 
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Ask the agent..."
      />
      <button onClick={sendMessage} disabled={loading}>
        {loading ? 'Sending...' : 'Send'}
      </button>
      {response && <div>Agent: {response}</div>}
    </div>
  );
}
```

### Node.js Backend

```javascript
const express = require('express');
const app = express();

app.post('/chat', async (req, res) => {
  try {
    const response = await fetch('https://your-api-gateway-url/prod/agent/invoke', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.JWT_TOKEN}`
      },
      body: JSON.stringify({
        input: req.body.message,
        sessionId: req.body.sessionId
      })
    });

    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to communicate with agent' });
  }
});
```

### Python Application

```python
import requests
import os

def invoke_bedrock_agent(message, session_id=None):
    url = 'https://your-api-gateway-url/prod/agent/invoke'
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': os.getenv('BEDROCK_API_KEY')
    }
    
    payload = {
        'input': message,
        'sessionId': session_id or f'session-{int(time.time())}'
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Usage
result = invoke_bedrock_agent("Hello, how can you help me?")
print(result['response'])
```

## Security Considerations

### 1. API Key Management

- Store API keys securely (environment variables, secret managers)
- Rotate keys regularly
- Use different keys for different environments
- Implement rate limiting in production

### 2. CORS Configuration

The proxy allows all origins by default. For production, configure specific origins:

```typescript
// In bedrock-agentcore-proxy-stack.ts
defaultCorsPreflightOptions: {
  allowOrigins: ['https://yourapp.com', 'https://www.yourapp.com'],
  allowMethods: ['POST', 'GET', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization', 'X-Api-Key']
}
```

### 3. Network Security

- Use HTTPS only
- Consider API Gateway throttling
- Implement request size limits
- Monitor for unusual traffic patterns

### 4. Logging and Monitoring

- Enable CloudWatch logging
- Monitor authentication failures
- Track usage patterns
- Set up alerts for errors

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check API key validity
   - Verify authentication headers
   - Ensure proper token format

2. **403 Forbidden**
   - Verify IAM permissions
   - Check agent ARN format
   - Ensure Lambda execution role has Bedrock permissions

3. **500 Internal Server Error**
   - Check CloudWatch logs
   - Verify agent ARN exists
   - Check network connectivity

4. **CORS Errors**
   - Verify origin is allowed
   - Check preflight OPTIONS requests
   - Ensure proper headers are included

### Debug Mode

Enable detailed logging by setting `LOG_LEVEL=DEBUG` in the Lambda environment variables.

## Next Steps

1. **Enhanced Authentication**: Implement custom JWT validation or integrate with AWS Cognito
2. **Rate Limiting**: Add request rate limiting per API key
3. **Caching**: Implement response caching for frequently asked questions
4. **Monitoring**: Set up comprehensive monitoring and alerting
5. **Multi-Agent Support**: Add routing logic for multiple agents

## Support

For issues and questions:
1. Check CloudWatch logs for detailed error information
2. Verify IAM permissions and agent configurations
3. Test authentication with simple curl commands
4. Review the proxy Lambda function code for customization needs