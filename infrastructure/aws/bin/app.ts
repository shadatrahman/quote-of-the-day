#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { DatabaseStack } from '../lib/database-stack';
import { ApiStack } from '../lib/api-stack';
import { LambdaStack } from '../lib/lambda-stack';
import { MonitoringStack } from '../lib/monitoring-stack';

const app = new cdk.App();

// Get environment context
const environment = app.node.tryGetContext('environment') || 'development';
const account = process.env.CDK_DEFAULT_ACCOUNT || process.env.AWS_ACCOUNT_ID;
const region = process.env.CDK_DEFAULT_REGION || process.env.AWS_REGION || 'us-east-1';

const env = { account, region };

// Environment-specific configuration
const config = {
  development: {
    stackPrefix: 'QuoteDev',
    domainName: undefined,
    certificateArn: undefined,
    enableDeletionProtection: false,
    enableBackup: false,
    multiAz: false,
    instanceClass: 'db.t4g.micro',
    allocatedStorage: 20,
    maxAllocatedStorage: 100,
  },
  staging: {
    stackPrefix: 'QuoteStaging',
    domainName: 'staging-api.quotestage.com',
    certificateArn: process.env.STAGING_CERTIFICATE_ARN,
    enableDeletionProtection: false,
    enableBackup: true,
    multiAz: false,
    instanceClass: 'db.t4g.small',
    allocatedStorage: 50,
    maxAllocatedStorage: 200,
  },
  production: {
    stackPrefix: 'QuoteProd',
    domainName: 'api.quoteapp.com',
    certificateArn: process.env.PRODUCTION_CERTIFICATE_ARN,
    enableDeletionProtection: true,
    enableBackup: true,
    multiAz: true,
    instanceClass: 'db.r6g.large',
    allocatedStorage: 100,
    maxAllocatedStorage: 1000,
  },
};

const envConfig = config[environment as keyof typeof config];

if (!envConfig) {
  throw new Error(`Unknown environment: ${environment}. Must be development, staging, or production.`);
}

console.log(`Deploying to environment: ${environment}`);
console.log(`Using account: ${account}, region: ${region}`);

// Create stacks
const databaseStack = new DatabaseStack(app, `${envConfig.stackPrefix}-Database`, {
  env,
  environment,
  ...envConfig,
});

const apiStack = new ApiStack(app, `${envConfig.stackPrefix}-Api`, {
  env,
  environment,
  database: databaseStack.database,
  redisCluster: databaseStack.redisCluster,
  vpc: databaseStack.vpc,
  ...envConfig,
});

const lambdaStack = new LambdaStack(app, `${envConfig.stackPrefix}-Lambda`, {
  env,
  environment,
  database: databaseStack.database,
  redisCluster: databaseStack.redisCluster,
  vpc: databaseStack.vpc,
  ...envConfig,
});

const monitoringStack = new MonitoringStack(app, `${envConfig.stackPrefix}-Monitoring`, {
  env,
  environment,
  apiCluster: apiStack.cluster,
  apiService: apiStack.service,
  database: databaseStack.database,
  redisCluster: databaseStack.redisCluster,
  lambdaFunctions: lambdaStack.functions,
  ...envConfig,
});

// Add dependencies
apiStack.addDependency(databaseStack);
lambdaStack.addDependency(databaseStack);
monitoringStack.addDependency(apiStack);
monitoringStack.addDependency(lambdaStack);

// Add tags to all stacks
const tags = {
  Project: 'QuoteOfTheDay',
  Environment: environment,
  ManagedBy: 'CDK',
};

Object.entries(tags).forEach(([key, value]) => {
  cdk.Tags.of(app).add(key, value);
});