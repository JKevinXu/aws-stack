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

## Notes

- Users will sign in to QuickSight through their IAM Identity Center portal
- Access management is handled through IAM Identity Center groups, simplifying administration
- QuickSight roles determine what actions users can perform within QuickSight

## Troubleshooting

- If users cannot sign in, verify they are added to the correct IAM Identity Center groups
- If users cannot see specific dashboards, ensure the dashboards are shared with their groups
- For data access issues, verify that QuickSight service role has appropriate permissions to the data sources 