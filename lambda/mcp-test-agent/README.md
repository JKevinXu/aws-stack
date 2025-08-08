# MCP Bedrock Agent Testing

This directory contains a Bedrock Agent implementation for testing the MCP (Model Context Protocol) server.

## Architecture

- **BedrockAgentStack**: CDK stack that creates:
  - Bedrock Agent with Claude 3.5 Sonnet foundation model
  - IAM roles and permissions for agent execution
  - Action Group with Lambda function for MCP server testing
  - Agent alias for stable endpoint access

- **MCP Test Lambda**: Python function that:
  - Tests MCP initialize handshake
  - Lists available tools from MCP server
  - Executes tool calls with parameters
  - Returns formatted results to Bedrock Agent

## Deployment

```bash
# Build the project
npm run build

# Deploy the Bedrock Agent stack
npx cdk deploy BedrockAgentStack
```

## Testing the Agent

After deployment, you can interact with the Bedrock Agent through:

1. **AWS Bedrock Console**: Test the agent directly in the AWS console
2. **AWS CLI**: Use `aws bedrock-agent-runtime invoke-agent` command
3. **SDK Integration**: Call the agent from your applications

## Available Test Functions

The agent can perform these MCP server tests:

- `test-mcp-initialize`: Tests the MCP initialization handshake
- `test-mcp-tools-list`: Lists available tools from the MCP server
- `test-mcp-tools-call`: Executes specific tools with parameters

## Example Interactions

Ask the agent things like:
- "Test the MCP server initialization"
- "What tools are available on the MCP server?"
- "Call the add tool with numbers 5 and 3"
- "Run a comprehensive test of all MCP functions"