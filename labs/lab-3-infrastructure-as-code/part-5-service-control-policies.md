# Part 5: Service Control Policies (SCPs)

## What are Service Control Policies?

Service Control Policies (SCPs) are organizational-level guardrails that set boundaries on what actions can be performed across all AWS accounts in your organization. Think of them as the ultimate override mechanism that can prevent actions even for users with full administrative privileges.

## How SCPs Work

SCPs operate on a "deny by default" principle with an important hierarchy:

```
User Request → IAM Permissions Check → SCP Permissions Check → Action Allowed/Denied
```

**Key Points:**
- SCPs can only **restrict** permissions, never **grant** them
- Even if IAM says "yes," SCP can still say "no"
- SCPs apply to all users and roles in the account (including root)
- They work at the organizational unit (OU) and account level

### Real-World Analogy
Think of IAM as your office building access card that gives you permission to enter certain floors and rooms. SCPs are like building-wide fire codes that override your individual permissions. Even if your card gives you access to a floor, you can't enter if there's a fire alarm requiring evacuation.

## Understanding JSON for SCPs

While CloudFormation uses YAML, SCPs are written in JSON (JavaScript Object Notation). If you understood YAML, JSON will make sense quickly.

### YAML vs JSON Comparison

**YAML:**
```yaml
name: my-bucket
properties:
  encrypted: true
  public: false
  tags:
    - environment
    - compliance
```

**JSON:**
```json
{
  "name": "my-bucket",
  "properties": {
    "encrypted": true,
    "public": false,
    "tags": ["environment", "compliance"]
  }
}
```

### Key JSON Rules
- Use curly braces `{}` to group related items
- Use square brackets `[]` for lists
- Put quotes around all text values
- Use commas to separate items
- No trailing commas allowed

## Basic SCP Structure

Every SCP follows this pattern:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "service:action",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "key": "value"
        }
      }
    }
  ]
}
```

### Component Breakdown

#### Version
```json
"Version": "2012-10-17"
```
- Always use `"2012-10-17"` (current policy language version)
- Must be in quotes because it looks like a date

#### Statement
```json
"Statement": [
  {
    // Individual policy rules go here
  }
]
```
- Contains an array of policy rules
- Each rule defines what actions are allowed or denied

#### Effect
```json
"Effect": "Deny"
```
- `"Allow"`: Permits the action (rare in SCPs)
- `"Deny"`: Blocks the action (most common in SCPs)

#### Action
```json
"Action": "ec2:RunInstances"
```
- Specifies which AWS API actions this rule applies to
- Format: `service:action`
- Use `*` as wildcard (e.g., `"ec2:*"` for all EC2 actions)

#### Resource
```json
"Resource": "*"
```
- Specifies which AWS resources this rule affects
- `"*"` means all resources
- Can be specific ARNs for targeted policies

#### Condition (Optional)
```json
"Condition": {
  "StringEquals": {
    "aws:Region": "us-east-1"
  }
}
```
- Adds specific circumstances when the rule applies
- Many condition types available (StringEquals, IpAddress, DateGreaterThan, etc.)

## Simple SCP Examples

### Example 1: Deny All EC2 Actions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyAllEC2",
      "Effect": "Deny",
      "Action": "ec2:*",
      "Resource": "*"
    }
  ]
}
```

**What it does:** Prevents anyone in the organization from performing any EC2 actions (launching instances, creating security groups, etc.).

**Use case:** Accounts that should only use serverless services.

### Example 2: Deny Root User Actions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyRootUser",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalType": "Root"
        }
      }
    }
  ]
}
```

**What it does:** Prevents the root user from performing any actions.

**Use case:** Enforce use of IAM users/roles instead of root account.

### Example 3: Deny Actions Outside Approved Regions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnapprovedRegions",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": [
            "us-east-1",
            "us-west-2"
          ]
        },
        "ForAllValues:StringNotEquals": {
          "aws:PrincipalServiceName": [
            "cloudformation.amazonaws.com",
            "config.amazonaws.com"
          ]
        }
      }
    }
  ]
}
```

**What it does:** Only allows actions in us-east-1 and us-west-2, with exceptions for CloudFormation and Config services.

**Use case:** Data residency compliance requirements.

## Advanced SCP Examples for GRC

### Example 4: Prevent Audit Log Deletion
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ProtectAuditLogs",
      "Effect": "Deny",
      "Action": [
        "cloudtrail:DeleteTrail",
        "cloudtrail:StopLogging",
        "cloudtrail:UpdateTrail",
        "s3:DeleteBucket",
        "s3:DeleteObject",
        "s3:DeleteObjectVersion"
      ],
      "Resource": [
        "arn:aws:cloudtrail:*:*:trail/audit-*",
        "arn:aws:s3:::audit-logs-*",
        "arn:aws:s3:::audit-logs-*/*"
      ]
    }
  ]
}
```

**What it does:** Protects audit trails and log buckets from deletion or modification.

**Compliance benefit:** Ensures audit log integrity for SOC 2, PCI DSS, and other frameworks.

### Example 5: Enforce Encryption for S3 Buckets
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnencryptedS3Buckets",
      "Effect": "Deny",
      "Action": "s3:CreateBucket",
      "Resource": "*",
      "Condition": {
        "Bool": {
          "s3:x-amz-server-side-encryption": "false"
        }
      }
    },
    {
      "Sid": "DenyUnencryptedObjectUploads",
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

**What it does:** Prevents creation of unencrypted S3 buckets and uploading unencrypted objects.

**Compliance benefit:** Enforces data encryption requirements across all accounts.

### Example 6: Prevent Insecure Security Group Rules
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PreventOpenSSH",
      "Effect": "Deny",
      "Action": [
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:ModifySecurityGroupRules"
      ],
      "Resource": "*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "0.0.0.0/0"
        },
        "NumericEquals": {
          "ec2:FromPort": "22"
        }
      }
    },
    {
      "Sid": "PreventOpenRDP",
      "Effect": "Deny",
      "Action": [
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:ModifySecurityGroupRules"
      ],
      "Resource": "*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "0.0.0.0/0"
        },
        "NumericEquals": {
          "ec2:FromPort": "3389"
        }
      }
    }
  ]
}
```

**What it does:** Prevents opening SSH (port 22) and RDP (port 3389) to the entire internet.

**Compliance benefit:** Prevents common security misconfigurations.

### Example 7: Require MFA for Sensitive Actions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RequireMFAForSensitiveActions",
      "Effect": "Deny",
      "Action": [
        "iam:DeleteUser",
        "iam:DeleteRole",
        "iam:DeletePolicy",
        "iam:AttachUserPolicy",
        "iam:AttachRolePolicy",
        "s3:DeleteBucket",
        "rds:DeleteDBInstance"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

**What it does:** Requires MFA for high-risk actions like deleting users, roles, or databases.

**Compliance benefit:** Adds additional authentication for privileged operations.

## SCP Condition Types Reference

### String Conditions
```json
"Condition": {
  "StringEquals": {"key": "exact-value"},
  "StringNotEquals": {"key": "not-this-value"},
  "StringLike": {"key": "pattern*"},
  "StringNotLike": {"key": "not-pattern*"}
}
```

### Numeric Conditions
```json
"Condition": {
  "NumericEquals": {"key": 123},
  "NumericNotEquals": {"key": 456},
  "NumericLessThan": {"key": 100},
  "NumericGreaterThan": {"key": 50}
}
```

### Date/Time Conditions
```json
"Condition": {
  "DateEquals": {"key": "2023-12-31T23:59:59Z"},
  "DateNotEquals": {"key": "2023-01-01T00:00:00Z"},
  "DateLessThan": {"key": "2024-01-01T00:00:00Z"},
  "DateGreaterThan": {"key": "2023-01-01T00:00:00Z"}
}
```

### Boolean Conditions
```json
"Condition": {
  "Bool": {"key": "true"},
  "BoolIfExists": {"key": "false"}
}
```

### IP Address Conditions
```json
"Condition": {
  "IpAddress": {"aws:SourceIp": "203.0.113.0/24"},
  "NotIpAddress": {"aws:SourceIp": "203.0.113.0/24"}
}
```

## Hands-On Exercise: Create Your First SCP

### Exercise 1: Basic Region Restriction
Create an SCP that only allows actions in `us-east-1` and `us-west-2`:

<details>
<summary>Click to see the solution</summary>

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RestrictToApprovedRegions",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": [
            "us-east-1",
            "us-west-2"
          ]
        }
      }
    }
  ]
}
```
</details>

### Exercise 2: Protect CloudTrail
Create an SCP that prevents anyone from stopping or deleting CloudTrail:

<details>
<summary>Click to see the solution</summary>

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ProtectCloudTrail",
      "Effect": "Deny",
      "Action": [
        "cloudtrail:DeleteTrail",
        "cloudtrail:StopLogging",
        "cloudtrail:UpdateTrail"
      ],
      "Resource": "*"
    }
  ]
}
```
</details>

### Exercise 3: Business Hours Only
Create an SCP that only allows EC2 actions during business hours (9 AM - 5 PM UTC):

<details>
<summary>Click to see the solution</summary>

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BusinessHoursOnly",
      "Effect": "Deny",
      "Action": "ec2:*",
      "Resource": "*",
      "Condition": {
        "DateLessThan": {
          "aws:CurrentTime": "09:00Z"
        }
      }
    },
    {
      "Sid": "AfterBusinessHours",
      "Effect": "Deny",
      "Action": "ec2:*",
      "Resource": "*",
      "Condition": {
        "DateGreaterThan": {
          "aws:CurrentTime": "17:00Z"
        }
      }
    }
  ]
}
```
</details>

## SCP Best Practices

### 1. Start Small and Test
- Begin with permissive policies
- Test in development accounts first
- Gradually add restrictions
- Monitor for unintended impacts

### 2. Use Descriptive Sids
```json
{
  "Sid": "PreventPublicS3Access",  // Good: Clear purpose
  "Sid": "Statement1",             // Bad: Generic name
}
```

### 3. Document Your Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnforceEncryption",
      "Effect": "Deny",
      "Action": "s3:PutObject",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}
```

Add comments in your documentation:
- **Purpose**: Ensure all S3 objects are encrypted
- **Compliance**: Required for PCI DSS Level 1
- **Impact**: Prevents unencrypted uploads
- **Exceptions**: None

### 4. Use Conditions Wisely
- Be specific to avoid blocking legitimate actions
- Test conditions thoroughly
- Consider time-based restrictions for sensitive operations

### 5. Plan for Exceptions
Some services need broader permissions:
```json
"Condition": {
  "StringNotEquals": {
    "aws:PrincipalServiceName": [
      "cloudformation.amazonaws.com",
      "config.amazonaws.com"
    ]
  }
}
```

## Common SCP Pitfalls

### ❌ Too Restrictive Initially
```json
{
  "Effect": "Deny",
  "Action": "*",
  "Resource": "*"
}
```
This blocks everything, including AWS service operations.

### ❌ Forgetting Service Exceptions
Not allowing AWS services to perform necessary actions on your behalf.

### ❌ No Testing Strategy
Deploying SCPs directly to production without testing.

### ❌ Poor Documentation
Not documenting the purpose and impact of each policy.

## Testing SCPs Safely

### 1. Use AWS Organizations Simulator
- Test policies before applying
- Understand the impact on different actions
- Available in the AWS Console

### 2. Start with Development Accounts
- Apply SCPs to non-production accounts first
- Monitor for unexpected denials
- Adjust policies based on findings

### 3. Monitor CloudTrail for Denials
Look for events with:
- `errorCode`: `AccessDenied`
- `errorMessage`: Contains "explicit deny"

### 4. Use AWS Config Rules
Create Config rules to monitor SCP effectiveness:
- Check if resources comply with SCP restrictions
- Alert on policy violations
- Generate compliance reports

## Deploying SCPs

SCPs are managed through AWS Organizations, not CloudFormation. Here's how to deploy them:

### Via AWS Console
1. Go to AWS Organizations
2. Navigate to Policies → Service control policies
3. Create policy
4. Attach to organizational units or accounts

### Via AWS CLI
```bash
# Create the policy
aws organizations create-policy \
  --name "RestrictRegions" \
  --description "Only allow us-east-1 and us-west-2" \
  --type SERVICE_CONTROL_POLICY \
  --content file://region-restriction.json

# Attach to an OU
aws organizations attach-policy \
  --policy-id p-xxxxxxxxxx \
  --target-id ou-xxxxxxxxxx
```

## Next Steps

Now you understand how to create organizational guardrails with SCPs. Let's explore the future of compliance enforcement with Resource Control Policies!

👉 **Continue to [Part 6: Advanced Compliance Patterns](./part-6-advanced-patterns.md)**
