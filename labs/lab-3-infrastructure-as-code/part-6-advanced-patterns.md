# Part 6: Advanced Compliance Patterns

## The Layered Compliance Approach

Now that you understand CloudFormation templates and Service Control Policies individually, let's explore how they work together to create a comprehensive, self-enforcing compliance system.

## The Four-Layer Defense Strategy

### Layer 1: Infrastructure as Code (Prevention)
**Purpose**: Deploy resources with correct security configurations from the start
**Mechanism**: CloudFormation templates with built-in compliance controls
**Benefit**: Prevents non-compliant resources from being created

### Layer 2: Service Control Policies (Enforcement)
**Purpose**: Create organizational guardrails that cannot be bypassed
**Mechanism**: JSON policies that deny non-compliant actions
**Benefit**: Prevents modification of compliant configurations

### Layer 3: Continuous Monitoring (Detection)
**Purpose**: Continuously monitor for configuration drift and violations
**Mechanism**: AWS Config rules and Security Hub findings
**Benefit**: Detects any issues that slip through prevention layers

### Layer 4: Automated Remediation (Response)
**Purpose**: Automatically fix violations when detected
**Mechanism**: Lambda functions triggered by Config rule violations
**Benefit**: Self-healing infrastructure that maintains compliance

## Real-World Integration Example

Let's see how all layers work together for S3 bucket security:

### Layer 1: Secure CloudFormation Template
```yaml
# secure-s3-template.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Multi-layer compliant S3 bucket'

Resources:
  ComplianceBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'compliant-bucket-${AWS::AccountId}-${AWS::Region}'
      
      # Layer 1: Built-in security controls
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
      
      # Compliance tags for monitoring
      Tags:
        - Key: ComplianceRequired
          Value: 'true'
        - Key: DataClassification
          Value: 'confidential'
        - Key: MonitoringEnabled
          Value: 'true'

  # Config rule to monitor compliance
  S3EncryptionRule:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: s3-bucket-server-side-encryption-enabled
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED
      Scope:
        ComplianceResourceTypes:
          - AWS::S3::Bucket
```

### Layer 2: Organizational SCP
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PreventS3PublicAccess",
      "Effect": "Deny",
      "Action": [
        "s3:PutBucketPublicAccessBlock",
        "s3:DeleteBucketPublicAccessBlock"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "s3:ExistingBucketPublicAccessBlock": "false"
        }
      }
    },
    {
      "Sid": "RequireS3Encryption",
      "Effect": "Deny",
      "Action": "s3:PutObject",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": [
            "AES256",
            "aws:kms"
          ]
        }
      }
    }
  ]
}
```

### Layer 3: Monitoring Configuration
```yaml
# monitoring-stack.yml
Resources:
  # Security Hub for centralized findings
  SecurityHub:
    Type: AWS::SecurityHub::Hub
    Properties:
      Tags:
        - Key: Purpose
          Value: ComplianceMonitoring

  # Config configuration recorder
  ConfigRecorder:
    Type: AWS::Config::ConfigurationRecorder
    Properties:
      Name: ComplianceRecorder
      RoleARN: !GetAtt ConfigRole.Arn
      RecordingGroup:
        AllSupported: true
        IncludeGlobalResourceTypes: true

  # Config delivery channel
  ConfigDeliveryChannel:
    Type: AWS::Config::DeliveryChannel
    Properties:
      Name: ComplianceDeliveryChannel
      S3BucketName: !Ref ConfigBucket
```

### Layer 4: Automated Remediation
```python
# remediation-lambda.py
import boto3
import json

def lambda_handler(event, context):
    """
    Automatically remediate S3 bucket compliance violations
    """
    s3_client = boto3.client('s3')
    
    # Parse Config rule evaluation
    config_item = event['configurationItem']
    bucket_name = config_item['resourceName']
    
    # Check if bucket lacks encryption
    if config_item['complianceType'] == 'NON_COMPLIANT':
        try:
            # Enable default encryption
            s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            )
            
            # Log remediation action
            print(f"Enabled encryption for bucket: {bucket_name}")
            
            return {
                'statusCode': 200,
                'body': json.dumps(f'Remediated bucket: {bucket_name}')
            }
            
        except Exception as e:
            print(f"Failed to remediate bucket {bucket_name}: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps(f'Remediation failed: {str(e)}')
            }
```

## Resource Control Policies: The Next Evolution

Resource Control Policies (RCPs) represent the future of granular compliance enforcement. While SCPs work at the account level, RCPs enforce compliance at the individual resource level during creation.

### How RCPs Differ from SCPs

| Aspect | SCPs | RCPs |
|--------|------|------|
| **Scope** | Account/OU level | Individual resource level |
| **Timing** | During API calls | During resource creation/modification |
| **Granularity** | Service actions | Resource properties |
| **Evaluation** | User permissions | Resource configuration |

### RCP Example: Enforce S3 Bucket Naming
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnforceS3NamingConvention",
      "Effect": "Deny",
      "Action": "s3:CreateBucket",
      "Resource": "*",
      "Condition": {
        "StringNotLike": {
          "s3:BucketName": [
            "company-*-prod-*",
            "company-*-dev-*",
            "company-*-staging-*"
          ]
        }
      }
    }
  ]
}
```

### RCP Example: Require Specific Tags
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RequireComplianceTags",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "s3:CreateBucket",
        "rds:CreateDBInstance"
      ],
      "Resource": "*",
      "Condition": {
        "ForAllValues:StringNotEquals": {
          "aws:TagKeys": [
            "Environment",
            "Owner",
            "CostCenter",
            "DataClassification"
          ]
        }
      }
    }
  ]
}
```

## Advanced CloudFormation Patterns

### Pattern 1: Conditional Compliance Controls
```yaml
Parameters:
  Environment:
    Type: String
    AllowedValues: [development, staging, production]
  
  EnableAdvancedSecurity:
    Type: String
    Default: 'false'
    AllowedValues: ['true', 'false']

Conditions:
  IsProduction: !Equals [!Ref Environment, production]
  EnableSecurity: !Or
    - !Condition IsProduction
    - !Equals [!Ref EnableAdvancedSecurity, 'true']

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketEncryption: !If
        - EnableSecurity
        - ServerSideEncryptionConfiguration:
            - ServerSideEncryptionByDefault:
                SSEAlgorithm: aws:kms
                KMSMasterKeyID: !Ref MyKMSKey
        - ServerSideEncryptionConfiguration:
            - ServerSideEncryptionByDefault:
                SSEAlgorithm: AES256
```

### Pattern 2: Cross-Stack References
```yaml
# network-stack.yml
Outputs:
  VPCId:
    Description: VPC ID for other stacks
    Value: !Ref MyVPC
    Export:
      Name: !Sub '${AWS::StackName}-VPC-ID'

# application-stack.yml
Resources:
  MySecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      VpcId: !ImportValue 'network-stack-VPC-ID'
      GroupDescription: Application security group
```

### Pattern 3: Nested Stacks for Reusability
```yaml
# master-stack.yml
Resources:
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/templates/network.yml
      Parameters:
        Environment: !Ref Environment
        
  SecurityStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/templates/security.yml
      Parameters:
        VPCId: !GetAtt NetworkStack.Outputs.VPCId
```

## Compliance Automation Workflows

### Workflow 1: New Account Setup
```yaml
# account-baseline.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Baseline compliance setup for new AWS accounts'

Resources:
  # Enable CloudTrail
  ComplianceTrail:
    Type: AWS::CloudTrail::Trail
    Properties:
      TrailName: compliance-audit-trail
      S3BucketName: !Ref AuditLogsBucket
      IncludeGlobalServiceEvents: true
      IsMultiRegionTrail: true
      EnableLogFileValidation: true

  # Enable Config
  ConfigRecorder:
    Type: AWS::Config::ConfigurationRecorder
    Properties:
      Name: compliance-recorder
      RoleARN: !GetAtt ConfigRole.Arn
      RecordingGroup:
        AllSupported: true

  # Enable Security Hub
  SecurityHub:
    Type: AWS::SecurityHub::Hub

  # Enable GuardDuty
  GuardDuty:
    Type: AWS::GuardDuty::Detector
    Properties:
      Enable: true
      FindingPublishingFrequency: FIFTEEN_MINUTES
```

### Workflow 2: Compliance Drift Detection
```python
# compliance-checker.py
import boto3
from datetime import datetime, timedelta

def check_compliance_drift():
    """
    Check for compliance drift across all resources
    """
    config_client = boto3.client('config')
    
    # Get compliance summary
    response = config_client.get_compliance_summary_by_config_rule()
    
    non_compliant_rules = []
    for rule in response['ComplianceSummary']:
        if rule['NonCompliantResourceCount']['CappedCount'] > 0:
            non_compliant_rules.append({
                'rule_name': rule['ConfigRuleName'],
                'non_compliant_count': rule['NonCompliantResourceCount']['CappedCount']
            })
    
    # Send alerts for non-compliance
    if non_compliant_rules:
        send_compliance_alert(non_compliant_rules)
    
    return non_compliant_rules

def send_compliance_alert(violations):
    """
    Send alert to compliance team
    """
    sns_client = boto3.client('sns')
    
    message = "Compliance Violations Detected:\n\n"
    for violation in violations:
        message += f"Rule: {violation['rule_name']}\n"
        message += f"Non-compliant resources: {violation['non_compliant_count']}\n\n"
    
    sns_client.publish(
        TopicArn='arn:aws:sns:us-east-1:123456789012:compliance-alerts',
        Subject='Compliance Drift Detected',
        Message=message
    )
```

## Integration with CI/CD Pipelines

### GitHub Actions Example
```yaml
# .github/workflows/compliance-check.yml
name: Compliance Check
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate-templates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Validate CloudFormation templates
        run: |
          for template in templates/*.yml; do
            aws cloudformation validate-template --template-body file://$template
          done
      
      - name: Run compliance checks
        run: |
          # Check for required security controls
          python scripts/compliance-validator.py
      
      - name: Deploy to staging
        if: github.ref == 'refs/heads/main'
        run: |
          aws cloudformation deploy \
            --template-file templates/main.yml \
            --stack-name compliance-staging \
            --parameter-overrides Environment=staging
```

## Hands-On Exercise: Complete Integration

### Exercise: Build a Self-Enforcing Compliance System

Create a complete system that demonstrates all four layers:

1. **Create the Infrastructure Template**
   - S3 bucket with all security controls
   - Config rule to monitor compliance
   - CloudWatch alarms for violations

2. **Write the Service Control Policy**
   - Prevent disabling bucket encryption
   - Require specific tags on all resources
   - Block public access modifications

3. **Set Up Monitoring**
   - Security Hub integration
   - Config rules for continuous monitoring
   - CloudWatch dashboards for visibility

4. **Implement Automated Remediation**
   - Lambda function to fix violations
   - EventBridge rules to trigger remediation
   - SNS notifications for compliance team

### Solution Structure
```
compliance-system/
├── templates/
│   ├── infrastructure.yml
│   ├── monitoring.yml
│   └── remediation.yml
├── policies/
│   ├── scp-s3-security.json
│   └── scp-tagging.json
├── scripts/
│   ├── remediation-lambda.py
│   └── compliance-checker.py
└── docs/
    ├── deployment-guide.md
    └── troubleshooting.md
```

## Key Takeaways

### The Power of Layered Defense
- **No single tool is perfect** - Combine multiple approaches
- **Prevention is better than detection** - Use IaC to deploy correctly
- **Enforcement prevents drift** - SCPs maintain compliance
- **Monitoring catches edge cases** - Config rules provide visibility
- **Automation scales compliance** - Remediation reduces manual work

### Best Practices Summary
1. **Start with templates** - Define secure defaults in CloudFormation
2. **Add guardrails** - Use SCPs to prevent policy violations
3. **Monitor continuously** - Enable Config and Security Hub
4. **Automate responses** - Build remediation into your system
5. **Document everything** - Make your system maintainable

### Compliance Benefits
- **Audit readiness** - Evidence is collected automatically
- **Reduced risk** - Violations are prevented or quickly fixed
- **Cost efficiency** - Automation reduces manual effort
- **Consistency** - Same controls across all environments
- **Scalability** - System grows with your organization

## Next Steps

Congratulations! You now understand how to build a comprehensive Infrastructure as Code system for GRC compliance. You've learned:

- ✅ AWS Shared Responsibility Model
- ✅ YAML syntax for CloudFormation
- ✅ Secure infrastructure templates
- ✅ Deployment methods (Console and CLI)
- ✅ Service Control Policies for enforcement
- ✅ Advanced compliance patterns and integration

### Recommended Follow-up Labs
1. **Event-Driven Compliance Automation** - Build real-time response systems
2. **Advanced AWS Config Rules** - Create custom compliance checks
3. **Security Hub Custom Insights** - Build compliance dashboards
4. **Multi-Account Governance** - Scale compliance across organizations

### Additional Resources
- [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/)
- [CloudFormation Best Practices](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html)
- [Service Control Policies User Guide](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html)
- [AWS Config Developer Guide](https://docs.aws.amazon.com/config/latest/developerguide/)

You're now equipped to build self-enforcing compliance systems that work 24/7 to keep your AWS infrastructure secure and compliant!
