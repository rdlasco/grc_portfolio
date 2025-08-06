# Part 5: Advanced CloudFormation Patterns

## Building Comprehensive Compliance Templates

Now that you understand the basics of CloudFormation, let's explore advanced patterns that make your templates more powerful, reusable, and compliant.

## Pattern 1: Conditional Security Controls

Sometimes you need different security levels based on the environment or specific requirements.

### Environment-Based Security
```yaml
Parameters:
  Environment:
    Type: String
    AllowedValues: [development, staging, production]
    Default: development
  
  EnableAdvancedSecurity:
    Type: String
    Default: 'false'
    AllowedValues: ['true', 'false']

Conditions:
  IsProduction: !Equals [!Ref Environment, production]
  EnableKMSEncryption: !Or
    - !Condition IsProduction
    - !Equals [!Ref EnableAdvancedSecurity, 'true']

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'secure-bucket-${Environment}-${AWS::AccountId}'
      
      # Conditional encryption: KMS for production, AES256 for others
      BucketEncryption: !If
        - EnableKMSEncryption
        - ServerSideEncryptionConfiguration:
            - ServerSideEncryptionByDefault:
                SSEAlgorithm: aws:kms
                KMSMasterKeyID: !Ref MyKMSKey
        - ServerSideEncryptionConfiguration:
            - ServerSideEncryptionByDefault:
                SSEAlgorithm: AES256
      
      # Always block public access
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  # KMS key only created when needed
  MyKMSKey:
    Type: AWS::KMS::Key
    Condition: EnableKMSEncryption
    Properties:
      Description: !Sub 'KMS key for ${Environment} S3 encryption'
      KeyPolicy:
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'
```

### Benefits of Conditional Controls
- **Cost optimization**: Only deploy expensive resources when needed
- **Environment-appropriate security**: Different controls for dev vs prod
- **Flexibility**: Single template works across multiple scenarios

## Pattern 2: Cross-Stack References

Build modular templates that work together while maintaining security boundaries.

### Network Stack (foundation)
```yaml
# network-stack.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Secure network foundation'

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-VPC'

  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      Tags:
        - Key: Name
          Value: Private Subnet

  # Security group with restrictive defaults
  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Database access security group
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref ApplicationSecurityGroup
      Tags:
        - Key: Name
          Value: Database Security Group

  ApplicationSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Application security group
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: Application Security Group

Outputs:
  VPCId:
    Description: VPC ID for other stacks
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VPC-ID'
  
  PrivateSubnetId:
    Description: Private subnet for databases
    Value: !Ref PrivateSubnet
    Export:
      Name: !Sub '${AWS::StackName}-PrivateSubnet-ID'
  
  DatabaseSecurityGroupId:
    Description: Security group for databases
    Value: !Ref DatabaseSecurityGroup
    Export:
      Name: !Sub '${AWS::StackName}-DatabaseSG-ID'
```

### Application Stack (uses network foundation)
```yaml
# application-stack.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Secure application resources'

Parameters:
  NetworkStackName:
    Type: String
    Description: Name of the network stack to import values from
    Default: network-stack

Resources:
  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub '${AWS::StackName}-database'
      DBInstanceClass: db.t3.micro
      Engine: mysql
      MasterUsername: admin
      MasterUserPassword: !Ref DatabasePassword
      
      # Use imported network resources
      DBSubnetGroupName: !Ref DatabaseSubnetGroup
      VPCSecurityGroups:
        - !ImportValue 
            Fn::Sub: '${NetworkStackName}-DatabaseSG-ID'
      
      # Security settings
      StorageEncrypted: true
      BackupRetentionPeriod: 7
      DeletionProtection: true
      
  DatabaseSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for RDS database
      SubnetIds:
        - !ImportValue 
            Fn::Sub: '${NetworkStackName}-PrivateSubnet-ID'
        # Add more subnets for production
      Tags:
        - Key: Name
          Value: Database Subnet Group

  DatabasePassword:
    Type: AWS::SecretsManager::Secret
    Properties:
      Description: Database master password
      GenerateSecretString:
        SecretStringTemplate: '{"username": "admin"}'
        GenerateStringKey: 'password'
        PasswordLength: 16
        ExcludeCharacters: '"@/\'
```

## Pattern 3: Nested Stacks for Reusability

Create reusable components that can be shared across teams.

### Master Stack
```yaml
# master-stack.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Complete application infrastructure'

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
    Default: dev

Resources:
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/my-templates/network.yml
      Parameters:
        Environment: !Ref Environment
        
  SecurityStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/my-templates/security.yml
      Parameters:
        Environment: !Ref Environment
        VPCId: !GetAtt NetworkStack.Outputs.VPCId
        
  ApplicationStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: [NetworkStack, SecurityStack]
    Properties:
      TemplateURL: https://s3.amazonaws.com/my-templates/application.yml
      Parameters:
        Environment: !Ref Environment
        VPCId: !GetAtt NetworkStack.Outputs.VPCId
        SecurityGroupId: !GetAtt SecurityStack.Outputs.SecurityGroupId

Outputs:
  ApplicationURL:
    Description: Application endpoint
    Value: !GetAtt ApplicationStack.Outputs.ApplicationURL
```

## Pattern 4: Parameter Validation and Constraints

Ensure users provide valid, secure configurations.

```yaml
Parameters:
  DatabasePassword:
    Type: String
    NoEcho: true
    Description: Database password (minimum 8 characters, must include uppercase, lowercase, and numbers)
    MinLength: 8
    MaxLength: 64
    AllowedPattern: '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$'
    ConstraintDescription: 'Password must be 8-64 characters with uppercase, lowercase, and numbers'

  AllowedCIDR:
    Type: String
    Description: CIDR block allowed to access the application
    Default: 10.0.0.0/8
    AllowedPattern: '^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    ConstraintDescription: 'Must be a valid CIDR block (e.g., 10.0.0.0/8)'

  Environment:
    Type: String
    Description: Environment name
    AllowedValues: [development, staging, production]
    ConstraintDescription: 'Must be development, staging, or production'

  InstanceType:
    Type: String
    Description: EC2 instance type
    Default: t3.micro
    AllowedValues: [t3.micro, t3.small, t3.medium, t3.large]
    ConstraintDescription: 'Must be a valid EC2 instance type'

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: ami-0abcdef1234567890  # Use latest Amazon Linux 2
      SecurityGroupIds:
        - !Ref MySecurityGroup
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          # Install security updates automatically

  MySecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Secure application access
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: !Ref AllowedCIDR
          Description: HTTPS access from allowed network
```

## Pattern 5: Comprehensive Tagging Strategy

Implement consistent tagging for compliance and cost management.

```yaml
Parameters:
  Project:
    Type: String
    Description: Project name
    MinLength: 1
    MaxLength: 50

  Owner:
    Type: String
    Description: Resource owner email
    AllowedPattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

  CostCenter:
    Type: String
    Description: Cost center code
    AllowedPattern: '^[A-Z0-9]{4,8}$'

  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]

Mappings:
  EnvironmentMap:
    dev:
      DataClassification: internal
      BackupRequired: 'false'
    staging:
      DataClassification: internal
      BackupRequired: 'true'
    prod:
      DataClassification: confidential
      BackupRequired: 'true'

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${Project}-${Environment}-${AWS::AccountId}'
      Tags:
        - Key: Project
          Value: !Ref Project
        - Key: Owner
          Value: !Ref Owner
        - Key: CostCenter
          Value: !Ref CostCenter
        - Key: Environment
          Value: !Ref Environment
        - Key: DataClassification
          Value: !FindInMap [EnvironmentMap, !Ref Environment, DataClassification]
        - Key: BackupRequired
          Value: !FindInMap [EnvironmentMap, !Ref Environment, BackupRequired]
        - Key: CreatedBy
          Value: CloudFormation
        - Key: CreatedDate
          Value: !Sub '${AWS::StackName}-${AWS::Region}'
```

## Pattern 6: Security-First Resource Policies

Embed security policies directly in your resources.

```yaml
Resources:
  SecureBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'secure-data-${AWS::AccountId}-${AWS::Region}'
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      VersioningConfiguration:
        Status: Enabled
      NotificationConfiguration:
        CloudWatchConfigurations:
          - Event: 's3:ObjectCreated:*'
            CloudWatchConfiguration:
              LogGroupName: !Ref S3AccessLogGroup

  # Restrictive bucket policy
  SecureBucketPolicy:
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
          
          - Sid: RestrictToSpecificRoles
            Effect: Allow
            Principal:
              AWS: 
                - !Sub 'arn:aws:iam::${AWS::AccountId}:role/DataProcessingRole'
                - !Sub 'arn:aws:iam::${AWS::AccountId}:role/BackupRole'
            Action:
              - 's3:GetObject'
              - 's3:PutObject'
            Resource: !Sub '${SecureBucket}/*'

  S3AccessLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/aws/s3/${AWS::StackName}'
      RetentionInDays: 90
```

## Hands-On Exercise: Build a Complete Secure Application

### Exercise: Multi-Tier Secure Application
Create a CloudFormation template that deploys:

1. **VPC with private subnets**
2. **Application Load Balancer with SSL**
3. **Auto Scaling Group with secure instances**
4. **RDS database with encryption**
5. **S3 bucket for application data**
6. **CloudWatch logging and monitoring**

### Requirements:
- All resources must have comprehensive tags
- Use parameters for environment-specific settings
- Implement conditional logic for dev vs prod
- Include security groups with least privilege
- Enable encryption everywhere possible
- Create cross-stack references where appropriate

### Solution Structure:
```
secure-application/
├── master-template.yml          # Main orchestration
├── network-template.yml         # VPC and networking
├── security-template.yml        # Security groups and roles
├── application-template.yml     # ALB and Auto Scaling
├── database-template.yml        # RDS with encryption
└── monitoring-template.yml      # CloudWatch and logging
```

## Best Practices Summary

### Template Organization
- **Use nested stacks** for complex applications
- **Separate concerns** - network, security, application layers
- **Create reusable components** that teams can share
- **Version control everything** including parameter files

### Security Implementation
- **Default to secure** - make insecure configurations hard
- **Use least privilege** in all IAM policies and security groups
- **Enable encryption** for all data at rest and in transit
- **Implement defense in depth** with multiple security layers

### Operational Excellence
- **Comprehensive tagging** for cost allocation and governance
- **Parameter validation** to prevent misconfigurations
- **Clear documentation** in descriptions and comments
- **Automated testing** of templates before deployment

### Compliance Considerations
- **Audit trail** - all changes tracked in version control
- **Consistent implementation** - same template = same security
- **Evidence generation** - templates serve as compliance documentation
- **Scalable governance** - patterns can be enforced organization-wide

## Next Steps

You now have the knowledge to build sophisticated, secure CloudFormation templates! Key skills you've developed:

✅ **YAML syntax mastery** - Write clean, readable templates
✅ **Security-first design** - Build compliance into your infrastructure
✅ **Advanced patterns** - Conditional logic, cross-stack references, nested stacks
✅ **Deployment expertise** - Console and CLI deployment methods
✅ **Best practices** - Tagging, validation, and operational excellence

### Recommended Next Steps:
1. **Practice with real projects** - Apply these patterns to your actual infrastructure needs
2. **Explore AWS CDK** - Higher-level abstraction for complex applications
3. **Learn CloudFormation Macros** - Extend CloudFormation with custom functionality
4. **Study AWS Well-Architected** - Understand broader architectural principles
5. **Build a template library** - Create reusable patterns for your organization

You're now equipped to transform manual, error-prone infrastructure deployment into automated, compliant, and scalable Infrastructure as Code!
