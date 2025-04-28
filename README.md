# AWS CDK S3 Bucket Stack

This project contains an AWS CDK stack that deploys an S3 bucket with the following features:
- Versioning enabled
- Server-side encryption using S3-managed keys (SSE-S3)
- Automatic cleanup on destroy (for development purposes)

## Prerequisites

Before you begin, ensure you have the following installed:
- Node.js & npm
- AWS CLI
- AWS CDK CLI (`npm install -g aws-cdk`)

## AWS Credentials Setup

Configure your AWS credentials using one of these methods:

1. Using AWS CLI (recommended):
```bash
aws configure
```
You'll be prompted to enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

2. Using environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=your_preferred_region
```

## Deployment Steps

1. Install dependencies:
```bash
npm install
```

2. Build the TypeScript project:
```bash
npm run build
```

3. Bootstrap the CDK environment (one-time setup per account/region):
```bash
cdk bootstrap
```

4. Deploy the stack:
```bash
cdk deploy
```

## Useful CDK Commands

* `npm run build` - Compile TypeScript to JavaScript
* `npm run watch` - Watch for changes and compile
* `npm run test` - Perform the jest unit tests
* `cdk deploy` - Deploy this stack to your default AWS account/region
* `cdk diff` - Compare deployed stack with current state
* `cdk synth` - Emits the synthesized CloudFormation template

## Security Note

The current configuration includes `removalPolicy: DESTROY` and `autoDeleteObjects: true`. These settings are suitable for development but should be removed for production deployments to prevent accidental deletion of the bucket and its contents.

## Cleanup

To destroy the stack and clean up all resources:
```bash
cdk destroy
```

Note: This will delete the S3 bucket and all its contents due to the `autoDeleteObjects` setting.
