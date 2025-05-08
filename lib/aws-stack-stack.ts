import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sso from 'aws-cdk-lib/aws-sso';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as cr from 'aws-cdk-lib/custom-resources';

export class AwsStackStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // example resource
    // const queue = new sqs.Queue(this, 'AwsStackQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });

    // Create an S3 bucket with versioning and encryption
    const bucket = new s3.Bucket(this, 'MyFirstBucket', {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // NOT recommended for production
      autoDeleteObjects: true, // NOT recommended for production
    });

    // Create an IAM Identity Center instance
    const identityCenterInstance = new sso.CfnInstance(this, 'MyIdentityCenterInstance', {
      name: 'My-Identity-Center',
      tags: [
        {
          key: 'Environment',
          value: 'Development'
        },
        {
          key: 'Purpose',
          value: 'Identity-Management'
        }
      ]
    });

    // Create a QuickSight Admin Group in IAM Identity Center
    // This uses a Custom Resource since CfnGroup requires the IdentityStoreId which is only available after the instance is created
    const quickSightAdminGroup = new cr.AwsCustomResource(this, 'QuickSightAdminGroup', {
      onUpdate: {
        service: 'IdentityStore',
        action: 'createGroup',
        parameters: {
          IdentityStoreId: identityCenterInstance.attrIdentityStoreId,
          DisplayName: 'QuickSight-Admins',
          Description: 'Administrators for Amazon QuickSight'
        },
        physicalResourceId: cr.PhysicalResourceId.fromResponse('GroupId')
      },
      policy: cr.AwsCustomResourcePolicy.fromSdkCalls({
        resources: cr.AwsCustomResourcePolicy.ANY_RESOURCE
      })
    });

    // Ensure the group creation depends on the identity center instance
    quickSightAdminGroup.node.addDependency(identityCenterInstance);

    // Create a QuickSight Admin User
    const quickSightAdminUser = new cr.AwsCustomResource(this, 'QuickSightAdminUser', {
      onUpdate: {
        service: 'IdentityStore',
        action: 'createUser',
        parameters: {
          IdentityStoreId: identityCenterInstance.attrIdentityStoreId,
          UserName: 'xkevinj',
          Name: {
            GivenName: 'Kevin',
            FamilyName: 'Xu'
          },
          DisplayName: 'Kevin Xu',
          Emails: [
            {
              Value: 'xkevinj@gmail.com',
              Type: 'Work',
              Primary: true
            }
          ]
        },
        physicalResourceId: cr.PhysicalResourceId.fromResponse('UserId')
      },
      policy: cr.AwsCustomResourcePolicy.fromSdkCalls({
        resources: cr.AwsCustomResourcePolicy.ANY_RESOURCE
      })
    });

    // Ensure the user creation depends on the identity center instance
    quickSightAdminUser.node.addDependency(identityCenterInstance);

    // Add the user to the QuickSight Admin Group
    const userGroupMembership = new cr.AwsCustomResource(this, 'UserGroupMembership', {
      onUpdate: {
        service: 'IdentityStore',
        action: 'createGroupMembership',
        parameters: {
          IdentityStoreId: identityCenterInstance.attrIdentityStoreId,
          GroupId: quickSightAdminGroup.getResponseField('GroupId'),
          MemberId: {
            UserId: quickSightAdminUser.getResponseField('UserId')
          }
        },
        physicalResourceId: cr.PhysicalResourceId.fromResponse('MembershipId')
      },
      policy: cr.AwsCustomResourcePolicy.fromSdkCalls({
        resources: cr.AwsCustomResourcePolicy.ANY_RESOURCE
      })
    });

    // Ensure proper dependencies
    userGroupMembership.node.addDependency(quickSightAdminGroup);
    userGroupMembership.node.addDependency(quickSightAdminUser);

    // Add S3 bucket for QuickSight data source
    const quicksightBucket = new s3.Bucket(this, 'QuickSightDataBucket', {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      removalPolicy: cdk.RemovalPolicy.DESTROY, 
      autoDeleteObjects: true
    });

    // IAM role for QuickSight to access S3
    const quickSightS3AccessRole = new iam.Role(this, 'QuickSightS3AccessRole', {
      assumedBy: new iam.ServicePrincipal('quicksight.amazonaws.com'),
      description: 'Role for QuickSight to access S3 data sources'
    });

    // Grant read permissions to S3 bucket
    quicksightBucket.grantRead(quickSightS3AccessRole);

    // Output the QuickSight data bucket name for the upload script
    new cdk.CfnOutput(this, 'QuickSightDataBucketName', {
      value: quicksightBucket.bucketName,
      description: 'The name of the S3 bucket for QuickSight data'
    });

    // Output the Identity Center instance ARN for future reference
    new cdk.CfnOutput(this, 'IdentityCenterInstanceArn', {
      value: identityCenterInstance.attrInstanceArn,
      description: 'The ARN of the IAM Identity Center instance'
    });

    // Output the Identity Store ID for future reference
    new cdk.CfnOutput(this, 'IdentityStoreId', {
      value: identityCenterInstance.attrIdentityStoreId,
      description: 'The ID of the IAM Identity Store'
    });

    // Output the QuickSight Admin Group ID
    new cdk.CfnOutput(this, 'QuickSightAdminGroupId', {
      value: quickSightAdminGroup.getResponseField('GroupId'),
      description: 'The ID of the QuickSight Admin Group in IAM Identity Center'
    });

    // Output the QuickSight Admin User ID
    new cdk.CfnOutput(this, 'QuickSightAdminUserId', {
      value: quickSightAdminUser.getResponseField('UserId'),
      description: 'The ID of the QuickSight Admin User in IAM Identity Center'
    });

    // Output the QuickSight Admin User Group Membership ID
    new cdk.CfnOutput(this, 'UserGroupMembershipId', {
      value: userGroupMembership.getResponseField('MembershipId'),
      description: 'The ID of the membership between the user and the admin group'
    });
  }
}
