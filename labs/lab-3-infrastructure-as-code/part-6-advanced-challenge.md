# Part 6: Advanced Challenge - Secure Web Application Infrastructure

## Challenge Overview

Put your CloudFormation skills to the test by building a complete, secure web application infrastructure that meets enterprise compliance requirements. This challenge combines all the concepts you've learned into a real-world scenario.

## The Scenario

**Company**: SecureCorpTech  
**Requirement**: Deploy a secure, compliant web application infrastructure for their new customer portal

**Compliance Requirements**:
- All data must be encrypted in transit and at rest
- Network traffic must be segmented and monitored
- Access must follow least privilege principles
- All resources must be properly tagged for audit purposes
- Infrastructure must support high availability
- Logs must be centralized and retained for compliance

## Challenge Architecture

You'll build a 3-tier web application with the following components:

```
Internet Gateway
        ↓
Application Load Balancer (HTTPS only)
        ↓
Auto Scaling Group (Private Subnets)
        ↓
RDS Database (Private Subnets)
        ↓
S3 Bucket (Application Data)
```

### Additional Security Components:
- VPC with public and private subnets
- NAT Gateway for outbound internet access
- Security groups with least privilege rules
- CloudWatch logging and monitoring
- Secrets Manager for database credentials
- KMS keys for encryption

## Challenge Requirements

### 1. Network Security
- **VPC** with proper CIDR segmentation
- **Public subnets** for load balancer only
- **Private subnets** for application servers and database
- **Security groups** with minimal required access
- **NACLs** for additional network-level protection

### 2. Application Security
- **HTTPS-only** communication (redirect HTTP to HTTPS)
- **Auto Scaling Group** with encrypted EBS volumes
- **Application Load Balancer** with SSL certificate
- **WAF** (Web Application Firewall) protection
- **Systems Manager** for secure instance management

### 3. Data Security
- **RDS database** with encryption at rest
- **Automated backups** with encryption
- **S3 bucket** with server-side encryption
- **Secrets Manager** for database passwords
- **KMS keys** for encryption key management

### 4. Monitoring & Compliance
- **CloudWatch** logs for all components
- **CloudTrail** for API logging
- **VPC Flow Logs** for network monitoring
- **Comprehensive tagging** for all resources
- **SNS alerts** for security events

## Challenge Template Structure

Create the following CloudFormation templates:

### Master Template (`master-stack.yml`)
Orchestrates all other stacks and manages dependencies.

### Network Template (`network-stack.yml`)
```yaml
# Your template should create:
# - VPC with DNS resolution enabled
# - 2 public subnets (different AZs)
# - 2 private subnets (different AZs)
# - Internet Gateway
# - NAT Gateway (for private subnet internet access)
# - Route tables with proper routing
# - VPC Flow Logs
```

### Security Template (`security-stack.yml`)
```yaml
# Your template should create:
# - KMS key for encryption
# - Security groups for ALB, EC2, and RDS
# - IAM roles for EC2 instances
# - WAF Web ACL
# - CloudWatch Log Groups
```

### Database Template (`database-stack.yml`)
```yaml
# Your template should create:
# - RDS subnet group
# - RDS parameter group (if needed)
# - RDS instance with encryption
# - Database password in Secrets Manager
# - Database security group
```

### Application Template (`application-stack.yml`)
```yaml
# Your template should create:
# - Application Load Balancer
# - Target Group
# - Launch Template with encrypted storage
# - Auto Scaling Group
# - S3 bucket for application data
# - CloudWatch alarms
```

## Starter Code

Here's a skeleton to get you started:

### Master Stack Template
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Secure Web Application Infrastructure - Master Stack'

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
    Default: dev
  
  ProjectName:
    Type: String
    Default: secure-webapp
    Description: Name of the project for resource naming

  # Add more parameters as needed

Resources:
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub 'https://s3.amazonaws.com/${TemplateBucket}/network-stack.yml'
      Parameters:
        Environment: !Ref Environment
        ProjectName: !Ref ProjectName
        # Add other parameters

  SecurityStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: NetworkStack
    Properties:
      TemplateURL: !Sub 'https://s3.amazonaws.com/${TemplateBucket}/security-stack.yml'
      Parameters:
        Environment: !Ref Environment
        ProjectName: !Ref ProjectName
        VPCId: !GetAtt NetworkStack.Outputs.VPCId
        # Add other parameters

  # Add DatabaseStack and ApplicationStack

Outputs:
  ApplicationURL:
    Description: Application Load Balancer URL
    Value: !GetAtt ApplicationStack.Outputs.LoadBalancerURL
    Export:
      Name: !Sub '${AWS::StackName}-ApplicationURL'
```

## Challenge Specifications

### Network Requirements
- **VPC CIDR**: 10.0.0.0/16
- **Public Subnets**: 10.0.1.0/24, 10.0.2.0/24
- **Private Subnets**: 10.0.10.0/24, 10.0.11.0/24
- **Multi-AZ deployment** for high availability

### Security Group Rules
```yaml
# ALB Security Group
- Port 80: 0.0.0.0/0 (redirect to 443)
- Port 443: 0.0.0.0/0

# EC2 Security Group  
- Port 80: ALB Security Group only
- Port 443: ALB Security Group only

# RDS Security Group
- Port 3306: EC2 Security Group only
```

### Required Tags
All resources must include:
```yaml
Tags:
  - Key: Project
    Value: !Ref ProjectName
  - Key: Environment
    Value: !Ref Environment
  - Key: Owner
    Value: 'GRC-Team'
  - Key: CostCenter
    Value: 'IT-Security'
  - Key: Compliance
    Value: 'Required'
  - Key: DataClassification
    Value: 'Confidential'
```

## Challenge Validation Criteria

Your solution will be evaluated on:

### ✅ Security Implementation (40 points)
- All traffic encrypted in transit
- All data encrypted at rest
- Proper network segmentation
- Least privilege access controls
- No hardcoded secrets

### ✅ Compliance Features (30 points)
- Comprehensive logging enabled
- Proper resource tagging
- Audit trail configuration
- Backup and retention policies

### ✅ High Availability (20 points)
- Multi-AZ deployment
- Auto Scaling configuration
- Load balancer health checks
- Database backup strategy

### ✅ Code Quality (10 points)
- Clean, readable YAML
- Proper parameter validation
- Good use of CloudFormation functions
- Comprehensive documentation

## Bonus Challenges

If you complete the basic requirements, try these advanced features:

### 🏆 Bonus 1: Blue/Green Deployment
Add support for blue/green deployments using CodeDeploy.

### 🏆 Bonus 2: Container Support
Modify the application tier to use ECS Fargate instead of EC2.

### 🏆 Bonus 3: Multi-Region
Extend the template to support deployment across multiple AWS regions.

### 🏆 Bonus 4: Custom Metrics
Create custom CloudWatch metrics and alarms for application monitoring.

## Solution Template

Here's a complete example of one component to guide your implementation:

### Network Stack Example
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Secure Web Application - Network Infrastructure'

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
  
  ProjectName:
    Type: String
    MinLength: 1
    MaxLength: 20

Mappings:
  EnvironmentMap:
    dev:
      VPCCidr: '10.0.0.0/16'
    staging:
      VPCCidr: '10.1.0.0/16'  
    prod:
      VPCCidr: '10.2.0.0/16'

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !FindInMap [EnvironmentMap, !Ref Environment, VPCCidr]
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-vpc'
        - Key: Project
          Value: !Ref ProjectName
        - Key: Environment
          Value: !Ref Environment

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-igw'

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      InternetGatewayId: !Ref InternetGateway
      VpcId: !Ref VPC

  # Public Subnets
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: !Select [0, !Cidr [!GetAtt VPC.CidrBlock, 4, 8]]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-public-subnet-1'

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: !Select [1, !Cidr [!GetAtt VPC.CidrBlock, 4, 8]]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-public-subnet-2'

  # Private Subnets
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: !Select [2, !Cidr [!GetAtt VPC.CidrBlock, 4, 8]]
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-private-subnet-1'

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: !Select [3, !Cidr [!GetAtt VPC.CidrBlock, 4, 8]]
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-private-subnet-2'

  # NAT Gateway
  NatGateway1EIP:
    Type: AWS::EC2::EIP
    DependsOn: InternetGatewayAttachment
    Properties:
      Domain: vpc
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-nat-eip-1'

  NatGateway1:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatGateway1EIP.AllocationId
      SubnetId: !Ref PublicSubnet1
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-nat-1'

  # Route Tables
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-public-routes'

  DefaultPublicRoute:
    Type: AWS::EC2::Route
    DependsOn: InternetGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PublicRouteTable
      SubnetId: !Ref PublicSubnet1

  PublicSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PublicRouteTable
      SubnetId: !Ref PublicSubnet2

  PrivateRouteTable1:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-private-routes-1'

  DefaultPrivateRoute1:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway1

  PrivateSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      SubnetId: !Ref PrivateSubnet1

  PrivateSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      SubnetId: !Ref PrivateSubnet2

  # VPC Flow Logs
  VPCFlowLogRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: vpc-flow-logs.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: flowlogsDeliveryRolePolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                  - logs:DescribeLogGroups
                  - logs:DescribeLogStreams
                Resource: '*'

  VPCFlowLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/aws/vpc/flowlogs/${ProjectName}-${Environment}'
      RetentionInDays: 30

  VPCFlowLog:
    Type: AWS::EC2::FlowLog
    Properties:
      ResourceType: VPC
      ResourceId: !Ref VPC
      TrafficType: ALL
      LogDestinationType: cloud-watch-logs
      LogGroupName: !Ref VPCFlowLogGroup
      DeliverLogsPermissionArn: !GetAtt VPCFlowLogRole.Arn
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-vpc-flowlog'

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VPC-ID'

  PublicSubnets:
    Description: List of public subnets
    Value: !Join [',', [!Ref PublicSubnet1, !Ref PublicSubnet2]]
    Export:
      Name: !Sub '${AWS::StackName}-PublicSubnets'

  PrivateSubnets:
    Description: List of private subnets  
    Value: !Join [',', [!Ref PrivateSubnet1, !Ref PrivateSubnet2]]
    Export:
      Name: !Sub '${AWS::StackName}-PrivateSubnets'
```

## Getting Started

1. **Plan your architecture** - Sketch out the components and their relationships
2. **Start with the network stack** - This is the foundation for everything else
3. **Build incrementally** - Test each stack individually before combining
4. **Use the validation script** - Run `python scripts/validate-templates.py` frequently
5. **Deploy to a test environment** - Don't deploy to production first!

## Submission Guidelines

When you complete the challenge:

1. **Create a `challenge-solution/` directory**
2. **Include all CloudFormation templates**
3. **Add a `README.md` explaining your architecture decisions**
4. **Include deployment instructions**
5. **Document any assumptions or trade-offs made**

## Success Criteria

You'll know you've succeeded when:

✅ All stacks deploy without errors  
✅ The web application is accessible via HTTPS  
✅ All security requirements are met  
✅ Comprehensive logging is enabled  
✅ Resources are properly tagged  
✅ High availability is configured  

## Time Estimate

- **Planning**: 30 minutes
- **Network Stack**: 1 hour
- **Security Stack**: 1 hour  
- **Database Stack**: 45 minutes
- **Application Stack**: 1.5 hours
- **Testing & Debugging**: 1 hour
- **Documentation**: 30 minutes

**Total**: ~6 hours (can be done over multiple sessions)

## Need Help?

If you get stuck:

1. **Review the earlier lab parts** - The patterns are all there
2. **Check AWS documentation** - CloudFormation resource reference
3. **Use the validation script** - It catches many common errors
4. **Start simple** - Get basic functionality working first, then add security features
5. **Test incrementally** - Deploy and test each stack individually

## Conclusion

This challenge brings together everything you've learned about CloudFormation and Infrastructure as Code. By completing it, you'll have built a production-ready, secure web application infrastructure that demonstrates enterprise-level GRC practices.

The skills you develop here - secure architecture design, CloudFormation mastery, and compliance automation - are directly applicable to real-world GRC engineering roles.

Good luck, and remember: the goal isn't just to make it work, but to make it secure, compliant, and maintainable!

---

**Ready to take on the challenge?** Start with the network stack and build your way up to a complete, secure application infrastructure!
