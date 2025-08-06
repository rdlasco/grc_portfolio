# Part 3: Your First CloudFormation Template

## Building a Secure S3 Bucket

In this section, you'll create a CloudFormation template that deploys a secure S3 bucket with all the compliance controls that GRC engineers care about.

## The Complete Template

Let's start with the full template, then break it down section by section:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Secure S3 Bucket with GRC compliance controls'

Parameters:
  BucketName:
    Type: String
    Description: 'Name for the S3 bucket (must be globally unique)'
    Default: 'my-secure-bucket'
    MinLength: 3
    MaxLength: 63
    AllowedPattern: '^[a-z0-9][a-z0-9-]*[a-z0-9]$'
    ConstraintDescription: 'Bucket name must be 3-63 characters, lowercase, and contain only letters, numbers, and hyphens'

  Environment:
    Type: String
    Description: 'Environment tag for the bucket'
    Default: 'development'
    AllowedValues:
      - development
      - staging
      - production

Resources:
  SecureBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${BucketName}-${AWS::AccountId}-${AWS::Region}'
      
      # Block all public access
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      
      # Enable encryption
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
            BucketKeyEnabled: true
      
      # Enable versioning
      VersioningConfiguration:
        Status: Enabled
      
      # Configure lifecycle management
      LifecycleConfiguration:
        Rules:
          - Id: DeleteIncompleteMultipartUploads
            Status: Enabled
            AbortIncompleteMultipartUpload:
              DaysAfterInitiation: 7
          - Id: TransitionToIA
            Status: Enabled
            Transition:
              StorageClass: STANDARD_IA
              TransitionInDays: 30
          - Id: TransitionToGlacier
            Status: Enabled
            Transition:
              StorageClass: GLACIER
              TransitionInDays: 90
      
      # Enable access logging
      LoggingConfiguration:
        DestinationBucketName: !Ref AccessLogsBucket
        LogFilePrefix: 'access-logs/'
      
      # Enable notifications
      NotificationConfiguration:
        CloudWatchConfigurations:
          - Event: 's3:ObjectCreated:*'
            CloudWatchConfiguration:
              LogGroupName: !Ref S3LogGroup
      
      # Add compliance tags
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Compliance
          Value: 'Required'
        - Key: DataClassification
          Value: 'Confidential'
        - Key: BackupRequired
          Value: 'Yes'
        - Key: CreatedBy
          Value: 'CloudFormation'

  # Separate bucket for access logs
  AccessLogsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${BucketName}-access-logs-${AWS::AccountId}-${AWS::Region}'
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      LifecycleConfiguration:
        Rules:
          - Id: DeleteOldLogs
            Status: Enabled
            ExpirationInDays: 90

  # CloudWatch Log Group for S3 events
  S3LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/aws/s3/${BucketName}'
      RetentionInDays: 30

  # Bucket policy for additional security
  BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref SecureBucket
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Sid: DenyInsecureConnections
            Effect: Deny
            Principal: '*'
            Action: 's3:*'
            Resource:
              - !Sub '${SecureBucket}/*'
              - !Ref SecureBucket
            Condition:
              Bool:
                'aws:SecureTransport': 'false'
          - Sid: DenyUnencryptedObjectUploads
            Effect: Deny
            Principal: '*'
            Action: 's3:PutObject'
            Resource: !Sub '${SecureBucket}/*'
            Condition:
              StringNotEquals:
                's3:x-amz-server-side-encryption': 'AES256'

Outputs:
  BucketName:
    Description: 'Name of the created S3 bucket'
    Value: !Ref SecureBucket
    Export:
      Name: !Sub '${AWS::StackName}-BucketName'
  
  BucketArn:
    Description: 'ARN of the created S3 bucket'
    Value: !GetAtt SecureBucket.Arn
    Export:
      Name: !Sub '${AWS::StackName}-BucketArn'
  
  AccessLogsBucket:
    Description: 'Name of the access logs bucket'
    Value: !Ref AccessLogsBucket
    Export:
      Name: !Sub '${AWS::StackName}-AccessLogsBucket'
```

## Breaking Down the Template

### Template Header
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Secure S3 Bucket with GRC compliance controls'
```

- **AWSTemplateFormatVersion**: Always use `'2010-09-09'` (current standard)
- **Description**: Explains what this template does (appears in AWS Console)

### Parameters Section
```yaml
Parameters:
  BucketName:
    Type: String
    Description: 'Name for the S3 bucket (must be globally unique)'
    Default: 'my-secure-bucket'
    MinLength: 3
    MaxLength: 63
    AllowedPattern: '^[a-z0-9][a-z0-9-]*[a-z0-9]$'
    ConstraintDescription: 'Bucket name must be 3-63 characters, lowercase, and contain only letters, numbers, and hyphens'
```

**Parameters make templates reusable:**
- `Type`: Data type (String, Number, List, etc.)
- `Description`: Help text for users
- `Default`: Value used if none provided
- `MinLength/MaxLength`: Validation constraints
- `AllowedPattern`: Regex validation
- `AllowedValues`: Dropdown list of valid options

### Core Security Controls

#### 1. Block Public Access
```yaml
PublicAccessBlockConfiguration:
  BlockPublicAcls: true
  BlockPublicPolicy: true
  IgnorePublicAcls: true
  RestrictPublicBuckets: true
```

**Why this matters:**
- Prevents accidental public exposure of data
- Required by most compliance frameworks
- Overrides any bucket policies or ACLs that would allow public access

#### 2. Encryption at Rest
```yaml
BucketEncryption:
  ServerSideEncryptionConfiguration:
    - ServerSideEncryptionByDefault:
        SSEAlgorithm: AES256
      BucketKeyEnabled: true
```

**Why this matters:**
- Protects data if physical storage is compromised
- Required by PCI DSS, HIPAA, SOC 2
- `BucketKeyEnabled` reduces encryption costs

#### 3. Versioning
```yaml
VersioningConfiguration:
  Status: Enabled
```

**Why this matters:**
- Protects against accidental deletion or modification
- Enables point-in-time recovery
- Required for compliance with data retention policies

#### 4. Lifecycle Management
```yaml
LifecycleConfiguration:
  Rules:
    - Id: TransitionToIA
      Status: Enabled
      Transition:
        StorageClass: STANDARD_IA
        TransitionInDays: 30
```

**Why this matters:**
- Reduces storage costs automatically
- Ensures data retention compliance
- Cleans up incomplete uploads (security best practice)

#### 5. Access Logging
```yaml
LoggingConfiguration:
  DestinationBucketName: !Ref AccessLogsBucket
  LogFilePrefix: 'access-logs/'
```

**Why this matters:**
- Provides audit trail of all bucket access
- Required for forensic investigations
- Helps detect unauthorized access patterns

### Bucket Policy for Additional Security
```yaml
PolicyDocument:
  Version: '2012-10-17'
  Statement:
    - Sid: DenyInsecureConnections
      Effect: Deny
      Principal: '*'
      Action: 's3:*'
      Resource:
        - !Sub '${SecureBucket}/*'
        - !Ref SecureBucket
      Condition:
        Bool:
          'aws:SecureTransport': 'false'
```

**This policy:**
- Denies all HTTP connections (forces HTTPS)
- Denies unencrypted uploads
- Applies to all users and roles

### Compliance Tags
```yaml
Tags:
  - Key: Environment
    Value: !Ref Environment
  - Key: Compliance
    Value: 'Required'
  - Key: DataClassification
    Value: 'Confidential'
```

**Why tags matter:**
- Enable automated compliance reporting
- Support cost allocation and governance
- Required by many organizational policies

## CloudFormation Functions Used

### !Ref
```yaml
BucketName: !Ref BucketName
```
References a parameter or resource. Returns the resource's primary identifier.

### !Sub
```yaml
BucketName: !Sub '${BucketName}-${AWS::AccountId}-${AWS::Region}'
```
Substitutes variables in strings. Creates unique names across accounts/regions.

### !GetAtt
```yaml
Value: !GetAtt SecureBucket.Arn
```
Gets specific attributes from resources (like ARN, DNS name, etc.).

## Hands-On Exercise

### Exercise 1: Create the Template
1. Copy the complete template above
2. Save it as `secure-s3-bucket.yml`
3. Modify the default bucket name to include your initials

### Exercise 2: Validate the Template
Before deploying, validate your YAML syntax:

```bash
# Check YAML syntax
python -c "import yaml; print('Valid YAML!' if yaml.safe_load(open('secure-s3-bucket.yml')) else 'Invalid YAML')"

# Validate CloudFormation template
aws cloudformation validate-template --template-body file://secure-s3-bucket.yml
```

### Exercise 3: Customize for Your Environment
Modify the template to:
1. Change the default environment to "staging"
2. Add a new tag for "Owner" with your name
3. Change the lifecycle transition to Glacier after 60 days instead of 90

<details>
<summary>Click to see the solution</summary>

```yaml
# In Parameters section:
Environment:
  Type: String
  Description: 'Environment tag for the bucket'
  Default: 'staging'  # Changed from 'development'
  AllowedValues:
    - development
    - staging
    - production

# In Tags section, add:
- Key: Owner
  Value: 'Your Name Here'

# In LifecycleConfiguration:
- Id: TransitionToGlacier
  Status: Enabled
  Transition:
    StorageClass: GLACIER
    TransitionInDays: 60  # Changed from 90
```
</details>

## Common Issues and Troubleshooting

### Issue: "Bucket name already exists"
**Solution:** S3 bucket names must be globally unique. Use the `!Sub` function to add account ID and region:
```yaml
BucketName: !Sub '${BucketName}-${AWS::AccountId}-${AWS::Region}'
```

### Issue: "Invalid bucket name"
**Solution:** Bucket names must follow DNS naming conventions:
- 3-63 characters long
- Lowercase letters, numbers, and hyphens only
- Cannot start or end with a hyphen
- Cannot contain consecutive periods

### Issue: "Access denied when creating bucket policy"
**Solution:** Ensure your IAM user/role has `s3:PutBucketPolicy` permission.

## Security Best Practices Implemented

✅ **Encryption at rest** - All data encrypted with AES-256
✅ **Encryption in transit** - HTTPS required for all connections
✅ **Access logging** - All bucket access logged for audit
✅ **Versioning** - Protection against accidental deletion
✅ **Public access blocked** - No public read/write access possible
✅ **Lifecycle management** - Automatic cost optimization and cleanup
✅ **Compliance tagging** - Proper resource categorization
✅ **Monitoring** - CloudWatch integration for alerts

## Next Steps

Now that you have a secure CloudFormation template, you're ready to learn how to deploy it!

👉 **Continue to [Part 4: Deployment Methods](./part-4-deployment.md)**
