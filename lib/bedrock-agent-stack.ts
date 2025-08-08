import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as bedrock from 'aws-cdk-lib/aws-bedrock';
import * as path from 'path';

export class BedrockAgentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create Lambda function for MCP server testing actions
    const mcpTestLambda = new lambda.Function(this, 'McpTestLambda', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda/mcp-test-agent')),
      timeout: cdk.Duration.seconds(30),
      memorySize: 512,
      environment: {
        MCP_SERVER_URL: 'https://sybw5cuj41.execute-api.us-west-2.amazonaws.com/prod/mcp',
        LOG_LEVEL: 'INFO'
      }
    });

    // Create IAM role for Bedrock Agent
    const agentRole = new iam.Role(this, 'BedrockAgentRole', {
      assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      inlinePolicies: {
        InvokeModel: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'bedrock:InvokeModel'
              ],
              resources: [
                `arn:aws:bedrock:${this.region}::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0`
              ]
            })
          ]
        })
      }
    });

    // Create action group schema for MCP testing (simplified for Bedrock)
    const actionGroupSchema = {
      openapi: "3.0.0",
      info: {
        title: "MCP Server Testing API",
        version: "1.0.0",
        description: "API for testing Model Context Protocol server endpoints"
      },
      paths: {
        "/test-mcp-initialize": {
          post: {
            description: "Test MCP server initialization handshake",
            operationId: "testMcpInitialize",
            responses: {
              "200": {
                description: "Successful initialization test",
                content: {
                  "application/json": {
                    schema: {
                      type: "object",
                      properties: {
                        success: { type: "boolean" },
                        result: { type: "object" },
                        error: { type: "string" }
                      }
                    }
                  }
                }
              }
            }
          }
        },
        "/test-mcp-tools-list": {
          post: {
            description: "Test MCP server tools listing",
            operationId: "testMcpToolsList",
            responses: {
              "200": {
                description: "Successful tools list test",
                content: {
                  "application/json": {
                    schema: {
                      type: "object",
                      properties: {
                        success: { type: "boolean" },
                        result: { type: "object" },
                        error: { type: "string" }
                      }
                    }
                  }
                }
              }
            }
          }
        },
        "/test-mcp-tools-call": {
          post: {
            description: "Test MCP server tool execution",
            operationId: "testMcpToolsCall",
            requestBody: {
              required: true,
              content: {
                "application/json": {
                  schema: {
                    type: "object",
                    properties: {
                      toolName: { 
                        type: "string",
                        description: "Name of the tool to call"
                      },
                      arguments: {
                        type: "string",
                        description: "JSON string of arguments to pass to the tool"
                      }
                    },
                    required: ["toolName", "arguments"]
                  }
                }
              }
            },
            responses: {
              "200": {
                description: "Successful tool call test",
                content: {
                  "application/json": {
                    schema: {
                      type: "object",
                      properties: {
                        success: { type: "boolean" },
                        result: { type: "object" },
                        error: { type: "string" }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    };

    // Create Bedrock Agent using L1 constructs (simplified version)
    const mcpTestAgent = new bedrock.CfnAgent(this, 'McpTestAgent', {
      agentName: 'mcp-test-agent',
      agentResourceRoleArn: agentRole.roleArn,
      foundationModel: 'anthropic.claude-3-5-sonnet-20240620-v1:0',
      instruction: `You are an MCP (Model Context Protocol) server testing assistant. 
Your primary goal is to test and validate MCP server functionality by:

1. Testing the initialization handshake to ensure proper MCP protocol compliance
2. Listing available tools from the MCP server 
3. Executing tool calls with various parameters to verify functionality
4. Reporting on the server's responses, including any errors or unexpected behavior

When testing:
- Always start with initialization to establish the connection
- List available tools before attempting to call them
- Test tools with valid parameters first, then test edge cases
- Provide detailed analysis of responses including protocol compliance
- Report any deviations from expected MCP protocol behavior

Use the available action group functions to interact with the MCP server and provide comprehensive test reports.`,
      actionGroups: [{
        actionGroupName: 'mcp-testing-actions',
        description: 'Action group for testing MCP server functionality',
        actionGroupExecutor: {
          lambda: mcpTestLambda.functionArn
        },
        apiSchema: {
          payload: JSON.stringify(actionGroupSchema)
        }
      }]
    });

    // Create agent alias
    const agentAlias = new bedrock.CfnAgentAlias(this, 'McpTestAgentAlias', {
      agentId: mcpTestAgent.attrAgentId,
      agentAliasName: 'mcp-test-agent-alias',
      description: 'Alias for MCP testing agent'
    });

    // Grant Lambda permission to be invoked by Bedrock
    mcpTestLambda.addPermission('BedrockInvoke', {
      principal: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      action: 'lambda:InvokeFunction',
      sourceAccount: this.account
    });

    // Outputs
    new cdk.CfnOutput(this, 'BedrockAgentId', {
      value: mcpTestAgent.attrAgentId,
      description: 'Bedrock Agent ID for MCP testing',
      exportName: 'McpTestAgentId'
    });

    new cdk.CfnOutput(this, 'BedrockAgentAliasId', {
      value: agentAlias.attrAgentAliasId,
      description: 'Bedrock Agent Alias ID',
      exportName: 'McpTestAgentAliasId'
    });

    new cdk.CfnOutput(this, 'TestLambdaArn', {
      value: mcpTestLambda.functionArn,
      description: 'MCP Test Lambda Function ARN',
      exportName: 'McpTestLambdaArn'
    });
  }
}