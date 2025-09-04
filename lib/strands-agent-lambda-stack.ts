import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';
import * as path from 'path';

export class StrandsAgentLambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const packagingDirectory = path.join(__dirname, "../packaging");
    const zipDependencies = path.join(packagingDirectory, "dependencies.zip");
    const zipApp = path.join(packagingDirectory, "app.zip");

    // Create a lambda layer with dependencies
    const dependenciesLayer = new lambda.LayerVersion(this, "DependenciesLayer", {
      code: lambda.Code.fromAsset(zipDependencies),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
      description: "Dependencies needed for Strands agent-based lambda",
    });

    // Define the Lambda function
    const strandsAgentFunction = new lambda.Function(this, "StrandsAgentLambda", {
      runtime: lambda.Runtime.PYTHON_3_12,
      functionName: "StrandsAgentFunction",
      handler: "agent_handler.handler",
      code: lambda.Code.fromAsset(zipApp),
      timeout: cdk.Duration.seconds(60), // Increased timeout for agent processing
      memorySize: 512, // Increased memory for better performance
      layers: [dependenciesLayer],
      architecture: lambda.Architecture.ARM_64,
      environment: {
        // Add any environment variables needed for the agent
        PYTHONPATH: '/opt/python:/var/runtime:/var/task'
      }
    });

    // Add permissions for Bedrock APIs (if using Bedrock models)
    strandsAgentFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [
          "bedrock:InvokeModel", 
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:GetFoundationModel",
          "bedrock:ListFoundationModels"
        ],
        resources: ["*"],
      }),
    );

    // Add permissions for other AWS services that might be needed
    strandsAgentFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream", 
          "logs:PutLogEvents"
        ],
        resources: ["arn:aws:logs:*:*:*"],
      }),
    );

    // Create API Gateway to expose the Lambda function
    const api = new apigateway.RestApi(this, 'StrandsAgentApi', {
      restApiName: 'Strands Agent Service',
      description: 'API Gateway for Strands Agent Lambda function',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key'],
      },
    });

    // Create Lambda integration
    const lambdaIntegration = new apigateway.LambdaIntegration(strandsAgentFunction, {
      requestTemplates: { "application/json": '{ "statusCode": "200" }' },
    });

    // Add resource and method
    const agentResource = api.root.addResource('agent');
    agentResource.addMethod('POST', lambdaIntegration);

    // Create a Lambda function URL for direct invocation (alternative to API Gateway)
    const functionUrl = strandsAgentFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowCredentials: true,
        allowedHeaders: ['*'],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedOrigins: ['*'],
        maxAge: cdk.Duration.days(1),
      },
    });

    // Output the Lambda function name
    new cdk.CfnOutput(this, 'StrandsAgentFunctionName', {
      value: strandsAgentFunction.functionName,
      description: 'The name of the Strands Agent Lambda function'
    });

    // Output the Lambda function ARN
    new cdk.CfnOutput(this, 'StrandsAgentFunctionArn', {
      value: strandsAgentFunction.functionArn,
      description: 'The ARN of the Strands Agent Lambda function'
    });

    // Output the API Gateway URL
    new cdk.CfnOutput(this, 'StrandsAgentApiUrl', {
      value: api.url,
      description: 'The URL of the API Gateway for the Strands Agent'
    });

    // Output the Function URL
    new cdk.CfnOutput(this, 'StrandsAgentFunctionUrl', {
      value: functionUrl.url,
      description: 'The direct URL of the Strands Agent Lambda function'
    });

    // Output the dependencies layer ARN for reference
    new cdk.CfnOutput(this, 'DependenciesLayerArn', {
      value: dependenciesLayer.layerVersionArn,
      description: 'The ARN of the dependencies layer'
    });
  }
}
