#!/bin/bash

# Get the bucket name from CloudFormation outputs
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name AwsStackStack --query "Stacks[0].Outputs[?OutputKey=='QuickSightDataBucketName'].OutputValue" --output text)

if [ -z "$BUCKET_NAME" ]; then
  echo "Error: Could not retrieve QuickSight data bucket name from CloudFormation outputs."
  exit 1
fi

# Create sample data directory
mkdir -p sample-data

# Replace the placeholder in manifest.json with the actual bucket name
sed -i '' "s/BUCKET_NAME/$BUCKET_NAME/g" manifest.json

# Upload the manifest file to the bucket
aws s3 cp manifest.json s3://$BUCKET_NAME/

echo "Manifest file uploaded to s3://$BUCKET_NAME/manifest.json"

# Optional: Create and upload a sample CSV file
echo "id,name,value
1,Item1,100
2,Item2,200
3,Item3,300" > sample-data/sample.csv

aws s3 cp sample-data/sample.csv s3://$BUCKET_NAME/sample-data/

echo "Sample data uploaded to s3://$BUCKET_NAME/sample-data/sample.csv" 