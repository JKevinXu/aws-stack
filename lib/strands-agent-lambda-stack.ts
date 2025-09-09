import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
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
      timeout: cdk.Duration.seconds(90), // Extended timeout for complex agent operations
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


    // Create a Lambda function URL for direct invocation
    // For production: use AWS_IAM auth, for testing: use NONE
    const functionUrl = strandsAgentFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE, // Change to AWS_IAM for production
      cors: {
        allowCredentials: true,
        allowedHeaders: [
          'Content-Type',
          'Authorization', 
          'X-Amz-Date',
          'X-Amz-Security-Token',
          'mcp-authorization-token'
        ],
        allowedMethods: [lambda.HttpMethod.POST],
        allowedOrigins: ['*'], // Restrict to specific domains in production
        maxAge: cdk.Duration.hours(1),
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
