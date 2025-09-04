#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { AwsStackStack } from '../lib/aws-stack-stack';
import { ApiGatewayMcpStack } from '../lib/api-gateway-mcp-stack';
import { BedrockAgentStack } from '../lib/bedrock-agent-stack';
import { StrandsAgentLambdaStack } from '../lib/strands-agent-lambda-stack';

const app = new cdk.App();
new AwsStackStack(app, 'AwsStackStack', {
  /* If you don't specify 'env', this stack will be environment-agnostic.
   * Account/Region-dependent features and context lookups will not work,
   * but a single synthesized template can be deployed anywhere. */

  /* Uncomment the next line to specialize this stack for the AWS Account
   * and Region that are implied by the current CLI configuration. */
  // env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },

  /* Uncomment the next line if you know exactly what Account and Region you
   * want to deploy the stack to. */
  // env: { account: '123456789012', region: 'us-east-1' },

  /* For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html */
});

// Create API Gateway MCP Stack
new ApiGatewayMcpStack(app, 'ApiGatewayMcpStack', {
  /* Use the same environment configuration as the main stack */
  // env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
});

// Create Bedrock Agent Stack for MCP testing
new BedrockAgentStack(app, 'BedrockAgentStack', {
  /* Use the same environment configuration as the main stack */
  // env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
});

// Create Strands Agent Lambda Stack
new StrandsAgentLambdaStack(app, 'StrandsAgentLambdaStack', {
  /* Use the same environment configuration as the main stack */
  // env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
});