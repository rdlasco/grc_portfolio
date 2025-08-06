#!/bin/bash

# Deploy Secure S3 Bucket CloudFormation Template
# Usage: ./deploy-secure-bucket.sh [bucket-name] [environment]

set -e

# Default values
BUCKET_NAME=${1:-"my-secure-bucket"}
ENVIRONMENT=${2:-"development"}
STACK_NAME="grc-lab-secure-bucket-${ENVIRONMENT}"
TEMPLATE_FILE="templates/secure-s3-bucket.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Deploying Secure S3 Bucket Stack${NC}"
echo "Stack Name: ${STACK_NAME}"
echo "Bucket Name: ${BUCKET_NAME}"
echo "Environment: ${ENVIRONMENT}"
echo "Template: ${TEMPLATE_FILE}"
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS CLI not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

# Validate template
echo -e "${YELLOW}📋 Validating CloudFormation template...${NC}"
if aws cloudformation validate-template --template-body file://${TEMPLATE_FILE} > /dev/null; then
    echo -e "${GREEN}✅ Template validation successful${NC}"
else
    echo -e "${RED}❌ Template validation failed${NC}"
    exit 1
fi

# Deploy stack
echo -e "${YELLOW}🔧 Deploying CloudFormation stack...${NC}"
aws cloudformation deploy \
    --template-file ${TEMPLATE_FILE} \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        BucketName=${BUCKET_NAME} \
        Environment=${ENVIRONMENT} \
    --capabilities CAPABILITY_NAMED_IAM \
    --tags \
        Project=GRC-Lab \
        Lab=Infrastructure-as-Code \
        Owner=$(aws sts get-caller-identity --query 'Arn' --output text | cut -d'/' -f2) \
        Environment=${ENVIRONMENT}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Stack deployment successful!${NC}"
    
    # Get stack outputs
    echo -e "${YELLOW}📊 Stack Outputs:${NC}"
    aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
    
    # Verify bucket security settings
    BUCKET_NAME_FULL=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' \
        --output text)
    
    echo -e "${YELLOW}🔒 Verifying security settings for bucket: ${BUCKET_NAME_FULL}${NC}"
    
    # Check encryption
    echo "Encryption Status:"
    aws s3api get-bucket-encryption --bucket ${BUCKET_NAME_FULL} --query 'ServerSideEncryptionConfiguration.Rules[0].ApplyServerSideEncryptionByDefault.SSEAlgorithm' --output text
    
    # Check public access block
    echo "Public Access Block:"
    aws s3api get-public-access-block --bucket ${BUCKET_NAME_FULL} --query 'PublicAccessBlockConfiguration' --output table
    
    # Check versioning
    echo "Versioning Status:"
    aws s3api get-bucket-versioning --bucket ${BUCKET_NAME_FULL} --query 'Status' --output text
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
else
    echo -e "${RED}❌ Stack deployment failed${NC}"
    exit 1
fi
