import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sso from 'aws-cdk-lib/aws-sso';
import * as iam from 'aws-cdk-lib/aws-iam';

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
  }
}
