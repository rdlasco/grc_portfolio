# Part 2: YAML Basics for CloudFormation

## What is YAML?

YAML ("YAML Ain't Markup Language") is a human-readable data format used for configuration files. It's the language you'll use to write CloudFormation templates.

YAML is designed to be easy to read and write, making it perfect for Infrastructure as Code.

## Basic YAML Syntax

### Key-Value Pairs
```yaml
name: my-first-stack
description: A secure S3 bucket template
version: 1.0
```

**Rules:**
- Keys and values are separated by a colon and space (`: `)
- No quotes needed for simple values
- Use quotes for values with special characters

### Lists
```yaml
resources:
  - AWS::S3::Bucket
  - AWS::IAM::Role
  - AWS::CloudTrail::Trail

# Alternative list syntax
resources: [AWS::S3::Bucket, AWS::IAM::Role, AWS::CloudTrail::Trail]
```

**Rules:**
- Lists start with a dash and space (`- `)
- Each item on a new line with same indentation
- Alternative: square brackets with comma separation

### Nested Structures
```yaml
bucket:
  name: my-secure-bucket
  properties:
    encryption: enabled
    versioning: true
    access:
      public: false
      logging: enabled
```

**Rules:**
- Indentation defines hierarchy (usually 2 spaces)
- All items at the same level must have the same indentation
- Tabs are not allowed - use spaces only

### Comments
```yaml
# This is a comment
name: my-stack  # This is also a comment
description: |
  This is a multi-line description
  that spans several lines
  and preserves line breaks
```

**Rules:**
- Comments start with `#`
- Use `|` for multi-line text that preserves line breaks
- Use `>` for multi-line text that folds into a single line

## YAML for CloudFormation

CloudFormation templates have a specific structure. Here's the basic template format:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Template description'

Parameters:
  # Input parameters

Mappings:
  # Static lookup tables

Conditions:
  # Conditional logic

Resources:
  # AWS resources to create

Outputs:
  # Values to return
```

### Template Sections Explained

#### AWSTemplateFormatVersion (Required)
```yaml
AWSTemplateFormatVersion: '2010-09-09'
```
- Always use `'2010-09-09'` (current standard)
- Quotes are required because it looks like a date

#### Description (Optional but Recommended)
```yaml
Description: 'Creates a secure S3 bucket with encryption and access logging'
```
- Human-readable explanation of the template
- Appears in the AWS Console
- Helps with documentation and maintenance

#### Resources (Required)
```yaml
Resources:
  MySecureBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-secure-bucket-12345
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
```

**Structure:**
- `MySecureBucket`: Logical name (you choose this)
- `Type`: AWS resource type (AWS::Service::Resource)
- `Properties`: Configuration specific to the resource type

## Common YAML Mistakes to Avoid

### ❌ Incorrect Indentation
```yaml
Resources:
MyBucket:  # Wrong - not indented
  Type: AWS::S3::Bucket
    Properties:  # Wrong - too much indentation
      BucketName: test
```

### ✅ Correct Indentation
```yaml
Resources:
  MyBucket:  # Correct - 2 spaces
    Type: AWS::S3::Bucket
    Properties:  # Correct - same level as Type
      BucketName: test
```

### ❌ Missing Spaces After Colons
```yaml
Resources:
  MyBucket:
    Type:AWS::S3::Bucket  # Wrong - no space after colon
```

### ✅ Correct Spacing
```yaml
Resources:
  MyBucket:
    Type: AWS::S3::Bucket  # Correct - space after colon
```

### ❌ Mixing Tabs and Spaces
```yaml
Resources:
	MyBucket:  # Tab used here
  Type: AWS::S3::Bucket  # Spaces used here
```

### ✅ Consistent Spacing
```yaml
Resources:
  MyBucket:  # 2 spaces
    Type: AWS::S3::Bucket  # 4 spaces (2 + 2)
```

## Hands-On Exercise: Your First YAML

Let's practice by creating a simple YAML structure:

### Exercise 1: Basic Structure
Create a YAML file that represents this information:
- Stack name: "my-first-template"
- Description: "Learning YAML for CloudFormation"
- Author: "GRC Engineer"
- Services used: S3, IAM, CloudTrail

<details>
<summary>Click to see the solution</summary>

```yaml
stack_name: my-first-template
description: Learning YAML for CloudFormation
author: GRC Engineer
services:
  - S3
  - IAM
  - CloudTrail
```
</details>

### Exercise 2: CloudFormation Structure
Create a basic CloudFormation template structure (don't worry about the actual resources yet):

<details>
<summary>Click to see the solution</summary>

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'My first CloudFormation template for GRC'

Resources:
  # Resources will go here

Outputs:
  # Outputs will go here
```
</details>

## YAML Validation Tools

Before deploying CloudFormation templates, validate your YAML syntax:

### Online Validators
- [YAML Lint](http://www.yamllint.com/)
- [Online YAML Parser](https://yaml-online-parser.appspot.com/)

### Command Line Tools
```bash
# Using Python (if installed)
python -c "import yaml; yaml.safe_load(open('template.yml'))"

# Using AWS CLI (validates CloudFormation syntax)
aws cloudformation validate-template --template-body file://template.yml
```

### VS Code Extensions
- **YAML** by Red Hat
- **CloudFormation** by AWS

## Key Takeaways

- **Indentation matters**: Use 2 spaces consistently
- **Colons need spaces**: Always `key: value`, never `key:value`
- **No tabs**: Only use spaces for indentation
- **Comments help**: Use `#` to document your templates
- **Validate early**: Check syntax before deploying

## Common CloudFormation YAML Patterns

### Boolean Values
```yaml
Properties:
  Enabled: true        # Boolean true
  PublicRead: false    # Boolean false
  Versioning: !Ref EnableVersioning  # Reference to parameter
```

### Numbers
```yaml
Properties:
  Port: 443           # Integer
  Timeout: 30.5       # Float
  MaxSize: !Ref MaxInstances  # Reference
```

### Lists of Objects
```yaml
SecurityGroupRules:
  - IpProtocol: tcp
    FromPort: 80
    ToPort: 80
    CidrIp: 0.0.0.0/0
  - IpProtocol: tcp
    FromPort: 443
    ToPort: 443
    CidrIp: 0.0.0.0/0
```

## Next Steps

Now that you understand YAML syntax, you're ready to create your first CloudFormation template!

👉 **Continue to [Part 3: Your First CloudFormation Template](./part-3-first-template.md)**
