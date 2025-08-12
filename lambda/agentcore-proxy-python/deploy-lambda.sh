#!/bin/bash

# AgentCore Proxy Python Lambda Deployment Script
# This script handles the complete deployment process for the Lambda function

set -e

# Configuration
LAMBDA_FUNCTION_NAME="agentcore-proxy-python"
RUNTIME="python3.11"
TIMEOUT=300
MEMORY_SIZE=1024
MCP_SERVER_URL="https://sybw5cuj41.execute-api.us-west-2.amazonaws.com/prod/mcp"
DEPLOYMENT_DIR="/Users/kevinxu/ws4/aws-stack/lambda/agentcore-proxy-python"
INLINE_AGENT_SOURCE="/Users/kevinxu/ws4/amazon-bedrock-agent-samples/src/InlineAgent/src/InlineAgent"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions for colored output
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Function to check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi
    
    # Check Python 3.11
    if ! command -v python3.11 &> /dev/null; then
        log_error "Python 3.11 is not installed"
        exit 1
    fi
    
    # Check if source directories exist
    if [[ ! -d "$DEPLOYMENT_DIR" ]]; then
        log_error "Deployment directory not found: $DEPLOYMENT_DIR"
        exit 1
    fi
    
    if [[ ! -d "$INLINE_AGENT_SOURCE" ]]; then
        log_error "InlineAgent source not found: $INLINE_AGENT_SOURCE"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

# Function to clean up previous builds
cleanup_previous() {
    log_step "Cleaning up previous deployment artifacts..."
    cd "$DEPLOYMENT_DIR"
    
    rm -rf venv package lambda-deployment.zip *.json 2>/dev/null || true
    log_info "Cleanup completed"
}

# Function to prepare InlineAgent source
prepare_inline_agent() {
    log_step "Preparing InlineAgent source code..."
    cd "$DEPLOYMENT_DIR"
    
    # Remove existing InlineAgent if present
    rm -rf InlineAgent
    
    # Copy InlineAgent source
    cp -r "$INLINE_AGENT_SOURCE" ./InlineAgent
    
    log_info "InlineAgent source prepared"
}

# Function to create virtual environment and install dependencies
install_dependencies() {
    log_step "Creating virtual environment and installing dependencies..."
    cd "$DEPLOYMENT_DIR"
    
    # Create virtual environment
    python3.11 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip --quiet
    
    # Create package directory
    mkdir -p package
    
    # Install dependencies with Linux-compatible binaries
    log_info "Installing dependencies (this may take a few minutes)..."
    pip install -r requirements.txt -t ./package \
        --platform manylinux2014_x86_64 \
        --python-version 3.11 \
        --only-binary :all: \
        --quiet
    
    log_info "Dependencies installed successfully"
}

# Function to create deployment package
create_package() {
    log_step "Creating deployment package..."
    cd "$DEPLOYMENT_DIR"
    
    # Copy application code
    cp -r InlineAgent ./package/
    cp lambda_function_new.py ./package/
    
    # Create ZIP package
    cd package
    zip -r ../lambda-deployment.zip . \
        -x "*.pyc" -x "*__pycache__*" -x "*.DS_Store" \
        > /dev/null 2>&1
    cd ..
    
    # Check package size
    PACKAGE_SIZE=$(ls -lh lambda-deployment.zip | awk '{print $5}')
    log_info "Deployment package created: lambda-deployment.zip ($PACKAGE_SIZE)"
    
    # Warn if package is too large
    PACKAGE_BYTES=$(wc -c < lambda-deployment.zip)
    if (( PACKAGE_BYTES > 50000000 )); then
        log_warn "Package size is close to Lambda limit (50MB)"
    fi
}

# Function to check if Lambda function exists
function_exists() {
    aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" &>/dev/null
}

# Function to create Lambda function
create_function() {
    log_step "Creating new Lambda function..."
    
    # Get default execution role
    ROLE_ARN=$(aws iam list-roles --query "Roles[?RoleName=='lambda-execution-role'].Arn" --output text)
    
    if [[ -z "$ROLE_ARN" ]]; then
        log_error "Lambda execution role not found. Please ensure 'lambda-execution-role' exists."
        exit 1
    fi
    
    aws lambda create-function \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --runtime "$RUNTIME" \
        --role "$ROLE_ARN" \
        --handler lambda_function_new.lambda_handler \
        --zip-file fileb://lambda-deployment.zip \
        --timeout "$TIMEOUT" \
        --memory-size "$MEMORY_SIZE" \
        --environment Variables="{MCP_SERVER_URL=$MCP_SERVER_URL}" \
        --description "AgentCore Proxy Python Lambda with InlineAgent support" \
        > /dev/null 2>&1
    
    log_info "Lambda function created successfully"
}

# Function to update existing Lambda function
update_function() {
    log_step "Updating existing Lambda function..."
    
    # Update function code
    aws lambda update-function-code \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --zip-file fileb://lambda-deployment.zip \
        > /dev/null 2>&1
    
    # Update function configuration
    aws lambda update-function-configuration \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --timeout "$TIMEOUT" \
        --memory-size "$MEMORY_SIZE" \
        --environment Variables="{MCP_SERVER_URL=$MCP_SERVER_URL}" \
        > /dev/null 2>&1
    
    log_info "Lambda function updated successfully"
}

# Function to test Lambda function
test_function() {
    log_step "Testing Lambda function..."
    
    # Test basic functionality
    aws lambda invoke \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --payload '{"input":"Test deployment"}' \
        --cli-binary-format raw-in-base64-out \
        test-response.json \
        > /dev/null 2>&1
    
    if jq -e '.success == true' test-response.json > /dev/null; then
        log_info "Basic test passed"
    else
        log_error "Basic test failed"
        cat test-response.json
        exit 1
    fi
    
    # Test mathematical calculation
    aws lambda invoke \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --payload '{"input":"What is 7 * 8?"}' \
        --cli-binary-format raw-in-base64-out \
        math-test.json \
        > /dev/null 2>&1
    
    if jq -e '.success == true' math-test.json > /dev/null; then
        MATH_RESULT=$(jq -r '.response' math-test.json)
        log_info "Math test passed: $MATH_RESULT"
    else
        log_error "Math test failed"
        cat math-test.json
        exit 1
    fi
    
    # Cleanup test files
    rm -f test-response.json math-test.json
}

# Function to get function details
get_function_info() {
    log_step "Retrieving function information..."
    
    FUNCTION_ARN=$(aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" --query 'Configuration.FunctionArn' --output text)
    LAST_MODIFIED=$(aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" --query 'Configuration.LastModified' --output text)
    CODE_SIZE=$(aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" --query 'Configuration.CodeSize' --output text)
    
    echo ""
    log_info "Deployment Summary:"
    echo "  Function Name: $LAMBDA_FUNCTION_NAME"
    echo "  Function ARN: $FUNCTION_ARN"
    echo "  Runtime: $RUNTIME"
    echo "  Memory: ${MEMORY_SIZE}MB"
    echo "  Timeout: ${TIMEOUT}s"
    echo "  Code Size: $CODE_SIZE bytes"
    echo "  Last Modified: $LAST_MODIFIED"
    echo ""
}

# Function to cleanup deployment artifacts
cleanup_artifacts() {
    log_step "Cleaning up deployment artifacts..."
    cd "$DEPLOYMENT_DIR"
    
    deactivate 2>/dev/null || true
    rm -rf venv package
    
    if [[ "$1" == "--keep-zip" ]]; then
        log_info "Keeping lambda-deployment.zip as backup"
    else
        rm -f lambda-deployment.zip
    fi
    
    log_info "Cleanup completed"
}

# Main deployment function
main() {
    echo ""
    log_info "Starting Lambda deployment process..."
    echo "Function: $LAMBDA_FUNCTION_NAME"
    echo "Runtime: $RUNTIME"
    echo ""
    
    # Run deployment steps
    check_prerequisites
    cleanup_previous
    prepare_inline_agent
    install_dependencies
    create_package
    
    # Deploy or update function
    if function_exists; then
        update_function
    else
        create_function
    fi
    
    # Test and show results
    test_function
    get_function_info
    
    # Cleanup (keep zip as backup)
    cleanup_artifacts --keep-zip
    
    log_info "Lambda deployment completed successfully!"
    echo ""
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --clean        Clean up all artifacts including zip file"
        echo ""
        echo "This script will:"
        echo "1. Check prerequisites"
        echo "2. Prepare InlineAgent source code"
        echo "3. Install dependencies"
        echo "4. Create deployment package"
        echo "5. Deploy/update Lambda function"
        echo "6. Test the function"
        echo "7. Show deployment summary"
        exit 0
        ;;
    --clean)
        log_info "Cleaning up all deployment artifacts..."
        cd "$DEPLOYMENT_DIR"
        rm -rf venv package lambda-deployment.zip *.json
        log_info "Cleanup completed"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac