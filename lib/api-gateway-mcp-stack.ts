import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as path from 'path';

export class ApiGatewayMcpStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create Lambda function for MCP server
    const mcpLambda = new lambda.Function(this, 'McpServerLambda', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda/mcp-server')),
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
      environment: {
        LOG_LEVEL: 'INFO'
      }
    });

    // Create API Gateway REST API
    const api = new apigateway.RestApi(this, 'McpServerApi', {
      restApiName: 'MCP Server API',
      description: 'API Gateway for MCP Server Lambda',
      deployOptions: {
        stageName: 'prod'
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key']
      }
    });

    // Add /mcp resource
    const mcpResource = api.root.addResource('mcp');

    // Add POST method with Lambda integration
    const lambdaIntegration = new apigateway.LambdaIntegration(mcpLambda, {
      requestTemplates: { 'application/json': '{ "statusCode": "200" }' }
    });

    mcpResource.addMethod('POST', lambdaIntegration, {
      apiKeyRequired: false
    });

    // Output the API endpoint
    new cdk.CfnOutput(this, 'McpApiEndpoint', {
      value: api.url,
      description: 'MCP Server API Endpoint',
      exportName: 'McpServerApiEndpoint'
    });

    new cdk.CfnOutput(this, 'McpApiUrl', {
      value: `${api.url}mcp`,
      description: 'MCP Server API Full URL',
      exportName: 'McpServerApiUrl'
    });
  }
}