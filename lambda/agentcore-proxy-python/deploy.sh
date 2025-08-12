#!/bin/bash

# Lambda Deployment Script for AgentCore Proxy Python
# Usage: ./deploy.sh [create|update] [function-name] [role-arn]

set -e

# Configuration
FUNCTION_NAME=${2:-agentcore-proxy-python}
ROLE_ARN=$3
RUNTIME="python3.11"
TIMEOUT=3000
MEMORY_SIZE=1024
MCP_SERVER_URL="https://bwzo9wnhy3.execute-api.us-west-2.amazonaws.com/beta/mcp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check deployment mode
if [ "$1" != "create" ] && [ "$1" != "update" ]; then
    print_error "Usage: $0 [create|update] [function-name] [role-arn]"
    echo "  create: Create new Lambda function (requires role-arn)"
    echo "  update: Update existing Lambda function"
    exit 1
fi

# For create mode, check if role ARN is provided
if [ "$1" == "create" ] && [ -z "$ROLE_ARN" ]; then
    print_error "Role ARN is required for creating new function"
    echo "Usage: $0 create function-name arn:aws:iam::ACCOUNT:role/ROLE_NAME"
    exit 1
fi

print_status "Starting Lambda deployment process..."

# Get current directory (deployment script directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Clean up any previous build artifacts
print_status "Cleaning up previous build artifacts..."
rm -rf lambda-deployment.zip

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Build deployment package using Docker with faster build options
print_status "Building deployment package using Docker (linux/amd64)..."
DOCKER_BUILDKIT=1 docker build --platform linux/amd64 -f Dockerfile.build -t lambda-builder . --progress=plain

# Extract the deployment package from the container
print_status "Extracting deployment package..."
docker run --platform linux/amd64 --rm --entrypoint="" -v "${SCRIPT_DIR}:/output" lambda-builder cp /tmp/lambda-deployment.zip /output/

# Get package size
PACKAGE_SIZE=$(ls -lh lambda-deployment.zip | awk '{print $5}')
print_status "Deployment package created: lambda-deployment.zip (${PACKAGE_SIZE})"

# Deploy to AWS Lambda
if [ "$1" == "create" ]; then
    print_status "Creating new Lambda function: ${FUNCTION_NAME}..."
    aws lambda create-function \
        --function-name ${FUNCTION_NAME} \
        --runtime ${RUNTIME} \
        --role ${ROLE_ARN} \
        --handler lambda_function_new.lambda_handler \
        --zip-file fileb://lambda-deployment.zip \
        --timeout ${TIMEOUT} \
        --memory-size ${MEMORY_SIZE} \
        --environment Variables={MCP_SERVER_URL=${MCP_SERVER_URL}} \
        --description "AgentCore Proxy Python Lambda with InlineAgent" \
        > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        print_status "Lambda function created successfully!"
    else
        print_error "Failed to create Lambda function"
        exit 1
    fi
else
    print_status "Updating existing Lambda function: ${FUNCTION_NAME}..."
    aws lambda update-function-code \
        --function-name ${FUNCTION_NAME} \
        --zip-file fileb://lambda-deployment.zip \
        > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        print_status "Lambda function code updated successfully!"
        
        # Update configuration
        print_status "Updating function configuration..."
        aws lambda update-function-configuration \
            --function-name ${FUNCTION_NAME} \
            --timeout ${TIMEOUT} \
            --memory-size ${MEMORY_SIZE} \
            --environment Variables={MCP_SERVER_URL=${MCP_SERVER_URL}} \
            > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            print_status "Lambda function configuration updated successfully!"
        else
            print_warning "Failed to update function configuration"
        fi
    else
        print_error "Failed to update Lambda function"
        exit 1
    fi
fi

# Get function details
print_status "Retrieving function details..."
FUNCTION_ARN=$(aws lambda get-function --function-name ${FUNCTION_NAME} --query 'Configuration.FunctionArn' --output text 2>/dev/null)
LAST_MODIFIED=$(aws lambda get-function --function-name ${FUNCTION_NAME} --query 'Configuration.LastModified' --output text 2>/dev/null)

echo ""
print_status "Deployment Summary:"
echo "  Function Name: ${FUNCTION_NAME}"
echo "  Function ARN: ${FUNCTION_ARN}"
echo "  Last Modified: ${LAST_MODIFIED}"
echo "  Package Size: ${PACKAGE_SIZE}"
echo ""

# Cleanup
print_status "Cleaning up build artifacts..."
docker rmi lambda-builder > /dev/null 2>&1 || true

# Keep the deployment package for backup
print_status "Deployment package saved as: lambda-deployment.zip"
print_status "Deployment completed successfully!"

# Optional: Test the function
read -p "Would you like to test the function? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Testing Lambda function..."
    TEST_PAYLOAD='{"input":"Please add 5 and 3 together using your available tools"}'
    aws lambda invoke \
        --function-name ${FUNCTION_NAME} \
        --payload "${TEST_PAYLOAD}" \
        --cli-binary-format raw-in-base64-out \
        response.json \
        > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        print_status "Test invocation successful! Response saved to response.json"
        cat response.json | python3 -m json.tool
    else
        print_error "Test invocation failed"
    fi
fi