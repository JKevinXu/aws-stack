# Setting Up Amazon QuickSight with IAM Identity Center

This document provides step-by-step instructions for setting up Amazon QuickSight to use IAM Identity Center as the identity provider.

## Prerequisites

- AWS Account with administrator access
- IAM Identity Center instance deployed (via our CDK stack)
- Amazon QuickSight Enterprise Edition subscription

## Step 1: Subscribe to Amazon QuickSight Enterprise Edition

1. Navigate to the [Amazon QuickSight console](https://quicksight.aws.amazon.com/)
2. Click on "Sign up for QuickSight"
3. Select "Enterprise Edition"
4. Choose "Use IAM Identity Center enabled application"
5. Select the IAM Identity Center instance created by our CDK stack
6. Complete the subscription process

## Step 2: Configure IAM Identity Center Groups for QuickSight

1. In the IAM Identity Center console, create or use existing user groups:
   - quicksight-admins
   - quicksight-authors
   - quicksight-readers

2. Add users to appropriate groups based on their QuickSight access needs

## Step 3: Configure QuickSight Access

1. In the QuickSight console, go to "Manage QuickSight"
2. Select "Manage Users"
3. Click on "Manage IAM Identity Center configuration"
4. Map IAM Identity Center groups to QuickSight roles:
   - Map "quicksight-admins" to "Admin" role
   - Map "quicksight-authors" to "Author" role
   - Map "quicksight-readers" to "Reader" role

## Step 4: Create a QuickSight Data Source (Manual Process)

1. Sign in to QuickSight as an Admin
2. Navigate to "Datasets" in the left navigation
3. Click "New dataset"
4. Select "S3" as the data source
5. Choose "Upload a manifest file"
6. Upload the manifest.json file that was uploaded to the S3 bucket
7. Click "Connect" and then "Visualize"

## Step 5: Create and Share QuickSight Dashboards

1. Create visualizations and dashboards in QuickSight
2. To share dashboards:
   - Open the dashboard
   - Click "Share" in the top-right
   - Select "Share dashboard"
   - Add IAM Identity Center groups to provide access

## Step 6: QuickSight Subscription Costs with Amazon Q

When setting up Amazon QuickSight with Amazon Q integration, consider the following pricing structure:

### User License Costs
- **Author**: $24/user/month (or $18/user/month with annual commitment)
- **Author Pro** (with full Amazon Q capabilities): $50/user/month
- **Reader**: $3/user/month
- **Reader Pro** (with Amazon Q capabilities): $20/user/month

### Amazon Q Enablement Fee
- $250/month per QuickSight account when any of the following apply:
  - At least one Pro user exists
  - At least one Amazon Q Topic is created

### Pro License Features
#### Author Pro includes:
- Building dashboards using natural language
- Creating Amazon Q Topics
- Viewing executive dashboard summaries
- Building and sharing generative data stories
- Advanced analysis with scenario capabilities
- Entitlement to Amazon Q Business Pro

#### Reader Pro includes:
- Viewing executive dashboard summaries
- Building and sharing generative data stories
- Advanced analysis with scenario capabilities
- Entitlement to Amazon Q Business Pro

### Considerations when Enabling Amazon Q for QuickSight
1. **Cost Management**: Start with a small number of Pro licenses for key personnel
2. **User Assignment**: Regular users can start with standard Reader licenses ($3/month)
3. **Consolidated Billing**: When provisioned in AWS IAM Identity Center, Pro licenses offer consolidated billing across multiple AWS accounts
4. **Free Trial**: Amazon Q in QuickSight offers a 30-day free trial for up to 4 users per QuickSight account

For the most up-to-date pricing information, always refer to the [official AWS QuickSight pricing page](https://aws.amazon.com/quicksight/pricing/).

## Notes

- Users will sign in to QuickSight through their IAM Identity Center portal
- Access management is handled through IAM Identity Center groups, simplifying administration
- QuickSight roles determine what actions users can perform within QuickSight

## Troubleshooting

- If users cannot sign in, verify they are added to the correct IAM Identity Center groups
- If users cannot see specific dashboards, ensure the dashboards are shared with their groups
- For data access issues, verify that QuickSight service role has appropriate permissions to the data sources 