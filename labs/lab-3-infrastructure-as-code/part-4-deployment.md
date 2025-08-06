# Part 4: Deployment Methods

## Two Ways to Deploy CloudFormation Templates

You can deploy CloudFormation templates using either the AWS Console (point-and-click) or the AWS CLI (command-line). Both methods achieve the same result, but each has advantages for different situations.

## Method 1: AWS Console Deployment

The AWS Console is great for learning, testing, and one-off deployments.

### Step-by-Step Console Deployment

#### Step 1: Access CloudFormation
1. Log into the AWS Management Console
2. Navigate to **CloudFormation** service
3. Click **Create stack** → **With new resources (standard)**

#### Step 2: Upload Your Template
1. Select **Template is ready**
2. Choose **Upload a template file**
3. Click **Choose file** and select your `secure-s3-bucket.yml`
4. Click **Next**

#### Step 3: Configure Stack Details
1. **Stack name**: Enter `my-secure-bucket-stack`
2. **Parameters**:
   - **BucketName**: Enter a unique name (e.g., `my-secure-bucket-yourname`)
   - **Environment**: Select `development`, `staging`, or `production`
3. Click **Next**

#### Step 4: Configure Stack Options
1. **Tags** (optional but recommended):
   - Key: `Project`, Value: `GRC-Lab`
   - Key: `Owner`, Value: `Your Name`
2. **Permissions**: Leave default (uses your current role)
3. **Stack failure options**: Select **Roll back all stack resources**
4. Click **Next**

#### Step 5: Review and Deploy
1. Review all settings
2. Check **I acknowledge that AWS CloudFormation might create IAM resources**
3. Click **Create stack**

#### Step 6: Monitor Deployment
1. Watch the **Events** tab for real-time progress
2. Check the **Resources** tab to see what's being created
3. Deployment typically takes 2-3 minutes

### Console Deployment Advantages
- ✅ Visual interface with guided steps
- ✅ Real-time progress monitoring
- ✅ Easy parameter validation
- ✅ Built-in template validation
- ✅ Great for learning and testing

### Console Deployment Disadvantages
- ❌ Manual process (not automatable)
- ❌ Slower for repeated deployments
- ❌ No version control integration
- ❌ Difficult to replicate exactly

## Method 2: AWS CLI Deployment

The AWS CLI is perfect for automation, scripting, and production deployments.

### Prerequisites for CLI Deployment

#### Install AWS CLI
Visit [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and follow instructions for your operating system.

**Quick installation:**
```bash
# macOS (using Homebrew)
brew install awscli

# Windows (using Chocolatey)
choco install awscli

# Linux (using pip)
pip install awscli
```

#### Configure AWS CLI
```bash
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: Your unique identifier
- **AWS Secret Access Key**: Your secret key
- **Default region**: e.g., `us-east-1`
- **Default output format**: `json` (recommended)

**Get your credentials:**
1. Go to AWS Console → IAM → Users → [Your Username]
2. Click **Security credentials** tab
3. Click **Create access key**
4. Choose **Command Line Interface (CLI)**
5. Copy the Access Key ID and Secret Access Key

#### Test Your Setup
```bash
aws sts get-caller-identity
```

This should return your AWS account information.

### CLI Deployment Commands

#### Basic Deployment
```bash
aws cloudformation deploy \
  --template-file secure-s3-bucket.yml \
  --stack-name my-secure-bucket-stack \
  --parameter-overrides BucketName=my-unique-bucket-name Environment=development \
  --capabilities CAPABILITY_NAMED_IAM \
  --tags Project=GRC-Lab Owner=YourName
```

#### Command Breakdown
- `aws cloudformation deploy`: Deploy a CloudFormation template
- `--template-file`: Path to your YAML template
- `--stack-name`: Name for your stack in AWS
- `--parameter-overrides`: Override default parameter values
- `--capabilities`: Permission to create IAM resources
- `--tags`: Add tags to all resources in the stack

#### Advanced Deployment with Validation
```bash
# Step 1: Validate template syntax
aws cloudformation validate-template --template-body file://secure-s3-bucket.yml

# Step 2: Deploy with change set (preview changes)
aws cloudformation deploy \
  --template-file secure-s3-bucket.yml \
  --stack-name my-secure-bucket-stack \
  --parameter-overrides BucketName=my-unique-bucket Environment=development \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-execute-changeset

# Step 3: Review changes, then execute
aws cloudformation execute-change-set \
  --change-set-name awscli-cloudformation-package-deploy-1234567890 \
  --stack-name my-secure-bucket-stack
```

#### Monitor Deployment Progress
```bash
# Watch stack events in real-time
aws cloudformation describe-stack-events --stack-name my-secure-bucket-stack

# Get stack status
aws cloudformation describe-stacks --stack-name my-secure-bucket-stack --query 'Stacks[0].StackStatus'

# List all resources in the stack
aws cloudformation list-stack-resources --stack-name my-secure-bucket-stack
```

### CLI Deployment Advantages
- ✅ Fully automatable and scriptable
- ✅ Fast repeated deployments
- ✅ Version control integration
- ✅ Consistent across environments
- ✅ Can be integrated into CI/CD pipelines

### CLI Deployment Disadvantages
- ❌ Steeper learning curve
- ❌ Less visual feedback
- ❌ Requires command-line comfort
- ❌ More setup required initially

## Hands-On Exercise: Deploy Your Template

### Exercise 1: Console Deployment
1. Use the AWS Console method to deploy your secure S3 bucket template
2. Use these parameters:
   - Stack name: `grc-lab-console-deployment`
   - Bucket name: `grc-lab-console-[your-initials]`
   - Environment: `development`
3. Monitor the deployment and note how long it takes
4. Verify the bucket was created with all security settings

### Exercise 2: CLI Deployment
1. Install and configure AWS CLI if you haven't already
2. Deploy the same template using CLI:
```bash
aws cloudformation deploy \
  --template-file secure-s3-bucket.yml \
  --stack-name grc-lab-cli-deployment \
  --parameter-overrides BucketName=grc-lab-cli-[your-initials] Environment=staging \
  --capabilities CAPABILITY_NAMED_IAM
```
3. Compare the deployment speed with the console method

### Exercise 3: Verify Deployments
Check that both deployments created secure buckets:

```bash
# List your stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE

# Get bucket details
aws s3api get-bucket-encryption --bucket [your-bucket-name]
aws s3api get-public-access-block --bucket [your-bucket-name]
aws s3api get-bucket-versioning --bucket [your-bucket-name]
```

## Deployment Best Practices

### 1. Always Validate First
```bash
# Validate template syntax
aws cloudformation validate-template --template-body file://template.yml

# Use change sets to preview changes
aws cloudformation deploy --no-execute-changeset
```

### 2. Use Consistent Naming
```bash
# Good: Descriptive and consistent
--stack-name company-environment-service-purpose

# Examples:
--stack-name acme-prod-s3-audit-logs
--stack-name acme-dev-vpc-networking
```

### 3. Tag Everything
```bash
aws cloudformation deploy \
  --tags \
    Environment=production \
    Project=compliance-automation \
    Owner=grc-team \
    CostCenter=security \
    Compliance=required
```

### 4. Use Parameter Files for Complex Deployments
Create `parameters.json`:
```json
[
  {
    "ParameterKey": "BucketName",
    "ParameterValue": "my-secure-bucket"
  },
  {
    "ParameterKey": "Environment",
    "ParameterValue": "production"
  }
]
```

Deploy with parameter file:
```bash
aws cloudformation deploy \
  --template-file template.yml \
  --stack-name my-stack \
  --parameter-overrides file://parameters.json
```

### 5. Handle Failures Gracefully
```bash
# Set rollback behavior
aws cloudformation deploy \
  --on-failure ROLLBACK \
  --disable-rollback false
```

## Troubleshooting Common Issues

### Issue: "Bucket name already exists"
**Error**: `BucketAlreadyExists`
**Solution**: Use a more unique bucket name or add randomization:
```yaml
BucketName: !Sub '${BucketName}-${AWS::AccountId}-${AWS::Region}'
```

### Issue: "Access denied"
**Error**: `AccessDenied`
**Solution**: Ensure your IAM user/role has these permissions:
- `cloudformation:*`
- `s3:*`
- `logs:*`
- `iam:PassRole` (if creating IAM resources)

### Issue: "Template validation failed"
**Error**: `ValidationError`
**Solution**: Check YAML syntax and CloudFormation resource properties:
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('template.yml'))"

# Validate CloudFormation
aws cloudformation validate-template --template-body file://template.yml
```

### Issue: "Stack rollback failed"
**Error**: `UPDATE_ROLLBACK_FAILED`
**Solution**: Some resources can't be rolled back automatically. Options:
1. Continue rollback and skip problematic resources
2. Delete the stack and redeploy
3. Fix the issue manually and continue

## Stack Management Commands

### Update a Stack
```bash
# Deploy updates to existing stack
aws cloudformation deploy \
  --template-file updated-template.yml \
  --stack-name existing-stack-name
```

### Delete a Stack
```bash
# Delete stack and all resources
aws cloudformation delete-stack --stack-name my-stack

# Monitor deletion
aws cloudformation wait stack-delete-complete --stack-name my-stack
```

### Get Stack Outputs
```bash
# Get all outputs
aws cloudformation describe-stacks \
  --stack-name my-stack \
  --query 'Stacks[0].Outputs'

# Get specific output
aws cloudformation describe-stacks \
  --stack-name my-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' \
  --output text
```

## Next Steps

Now that you can deploy secure infrastructure with CloudFormation, let's learn how to enforce organizational guardrails with Service Control Policies!

👉 **Continue to [Part 5: Service Control Policies](./part-5-service-control-policies.md)**
