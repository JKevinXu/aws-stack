#!/bin/bash

# Strands Agent Lambda Deployment Script
# This script follows the deployment pattern from the Strands documentation

set -e  # Exit on any error

echo "🚀 Strands Agent Lambda Deployment Script"
echo "========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js and npm are available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    exit 1
fi

# Check if CDK is available
if ! command -v npx &> /dev/null; then
    echo "❌ npx is required but not installed."
    exit 1
fi

echo "📋 Prerequisites check passed!"

# Step 1: Install Python dependencies and package for Lambda
echo "📦 Step 1: Packaging Lambda function and dependencies..."
python3 ./bin/package_for_lambda.py

if [ $? -ne 0 ]; then
    echo "❌ Packaging failed!"
    exit 1
fi

echo "✅ Packaging completed successfully!"

# Step 2: Build TypeScript CDK code
echo "🔨 Step 2: Building CDK TypeScript code..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ TypeScript build failed!"
    exit 1
fi

echo "✅ TypeScript build completed!"

# Step 3: Bootstrap CDK (if not already done)
echo "🌱 Step 3: Bootstrapping CDK environment (if needed)..."
npx cdk bootstrap --require-approval never || {
    echo "⚠️  CDK bootstrap may have already been done or failed - continuing..."
}

# Step 4: Deploy the Strands Agent Lambda stack
echo "🚀 Step 4: Deploying Strands Agent Lambda Stack..."
npx cdk deploy StrandsAgentLambdaStack --require-approval never

if [ $? -ne 0 ]; then
    echo "❌ CDK deployment failed!"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Test your Lambda function using the AWS CLI:"
echo "   aws lambda invoke --function-name StrandsAgentFunction \\"
echo "     --region us-east-1 \\"
echo "     --cli-binary-format raw-in-base64-out \\"
echo "     --payload '{\"prompt\": \"What is the weather in Seattle?\"}' \\"
echo "     output.json"
echo ""
echo "2. View the response:"
echo "   cat output.json"
echo ""
echo "3. Or use the Function URL or API Gateway endpoint from the CDK outputs"
echo ""
echo "🔗 Check the CDK output above for the specific URLs and ARNs."
