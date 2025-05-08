# AWS CDK S3 Bucket Stack

This project contains an AWS CDK stack that deploys an S3 bucket with the following features:
- Versioning enabled
- Server-side encryption using S3-managed keys (SSE-S3)
- Automatic cleanup on destroy (for development purposes)

# AWS CDK S3 Bucket & QuickSight Integration Stack

This project contains an AWS CDK stack that deploys:

1. S3 buckets with the following features:
   - Versioning enabled
   - Server-side encryption using S3-managed keys (SSE-S3)
   - Automatic cleanup on destroy (for development purposes)

2. IAM Identity Center integration:
   - Identity Center instance for centralized user management
   - Automated QuickSight Admin group creation
   - Pre-configured IAM role for QuickSight to access S3 data

3. QuickSight preparation:
   - Dedicated S3 bucket for QuickSight data
   - All necessary permissions and roles
   - Ready-to-use admin group for QuickSight management

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

Note: The stack uses AWS CDK custom resources to create the QuickSight admin group. The required `aws-cdk-lib/custom-resources` module is part of the standard CDK library and does not require additional installation.

## Configuring QuickSight with IAM Identity Center

Once the stack is deployed, you can configure Amazon QuickSight to work with the IAM Identity Center:

1. Note the outputs from the CDK deployment, which include:
   - `IdentityCenterInstanceArn` - The ARN of the IAM Identity Center instance
   - `IdentityStoreId` - The ID of the IAM Identity Store
   - `QuickSightDataBucketName` - The S3 bucket that can be used for QuickSight data

2. Sign in to the AWS Management Console and navigate to the QuickSight service.

3. If you haven't subscribed to QuickSight yet:
   - Click "Sign up for QuickSight"
   - Choose "Enterprise" edition
   - Select "IAM Identity Center" as your identity type
   - In the "Authentication" section, select the Identity Center instance that was created by the CDK stack

4. If you already have QuickSight:
   - Go to QuickSight admin settings
   - Navigate to "Security & permissions"
   - Under "Authentication", select "Manage IAM Identity Center" 
   - Connect to the Identity Center instance created by the CDK stack

5. Configure permissions for the S3 bucket:
   - In QuickSight, go to "Manage QuickSight" > "Security & permissions"
   - Under "QuickSight access to AWS services", select "Add or remove"
   - Enable access to the S3 bucket created by the stack (`QuickSightDataBucketName`)

6. Configure users and groups:
   - In the AWS Console, navigate to IAM Identity Center
   - Create users and groups as needed
   - Assign QuickSight access to those users and groups

7. To connect to the S3 data source in QuickSight:
   - In QuickSight, choose "Datasets" > "New dataset"
   - Select "S3" as the data source
   - Enter the bucket name from the CDK output (`QuickSightDataBucketName`)
   - Follow the prompts to complete the connection

### QuickSight Admin Group Management

The CDK stack automatically creates a QuickSight Admin group in IAM Identity Center, eliminating the need for manual group creation. After deployment:

1. Note the output `QuickSightAdminGroupId` from the CDK deployment, which contains the ID of the created admin group.

2. To add users to this admin group:
   - Go to the AWS IAM Identity Center console
   - Navigate to "Groups" and select the "QuickSight-Admins" group
   - Click "Add users"
   - Select users to add and complete the process

3. To configure this group in QuickSight:
   - Navigate to the QuickSight console
   - Go to "Manage QuickSight" > "Manage users"
   - Click "Add users" and select the Identity Center option
   - Search for the "QuickSight-Admins" group and add it
   - Set the access level to "Admin"
   - Complete the process by following the prompts

This group has been pre-created with the name "QuickSight-Admins" and is ready to be used for QuickSight administration purposes.

### Default QuickSight Admin User

The CDK stack also automatically creates a default QuickSight admin user and adds them to the QuickSight Admins group:

1. The user is created with the following attributes:
   - Username: `xkevinj`
   - Display name: `Kevin X`
   - Email: `xkevinj@gmail.com`

2. The user is automatically added to the "QuickSight-Admins" group

3. Important deployment outputs include:
   - `QuickSightAdminUserId`: The ID of the created admin user
   - `UserGroupMembershipId`: The ID of the group membership link

4. To set a password for this user:
   - Go to the AWS IAM Identity Center console
   - Navigate to "Users" and find the "Kevin X" user
   - Select the user and choose "Reset password"
   - Follow the prompts to set a password and complete the process

5. The user can then log in to QuickSight using their Identity Center credentials

**Important:** For production environments, you should modify the user email address in the CDK code to use a valid email before deploying.

## Useful CDK Commands

* `npm run build`