import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sso from 'aws-cdk-lib/aws-sso';

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
  }
}
