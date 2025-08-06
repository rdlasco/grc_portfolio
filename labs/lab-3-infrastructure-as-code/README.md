# Lab 3: Infrastructure as Code with CloudFormation

## Overview

This lab introduces Infrastructure as Code (IaC) using AWS CloudFormation specifically for GRC engineers. You'll learn to write YAML templates that deploy secure, compliant infrastructure automatically, ensuring security controls are built-in from the start.

## Learning Objectives

By the end of this lab, you will be able to:

1. **Understand Infrastructure as Code principles** and how they improve compliance
2. **Write CloudFormation templates** using YAML to deploy secure AWS resources
3. **Deploy infrastructure** using both AWS Console and AWS CLI
4. **Implement security best practices** directly in CloudFormation templates
5. **Create reusable, compliant infrastructure patterns** for your organization

## Prerequisites

- AWS account with appropriate permissions
- Basic understanding of AWS services (S3, IAM, CloudTrail)
- AWS CLI installed and configured (for CLI deployment section)

## Lab Structure

This lab is divided into several hands-on exercises:

1. **Foundation Concepts** - Understanding Infrastructure as Code principles
2. **YAML Basics** - Learning the syntax for CloudFormation templates
3. **Your First CloudFormation Template** - Creating a secure S3 bucket
4. **Deployment Methods** - Using AWS Console and CLI
5. **Advanced CloudFormation Patterns** - Building comprehensive compliance templates

## Time Estimate

- **Total Duration**: 2-3 hours
- **Hands-on Activities**: 60% of time
- **Conceptual Learning**: 40% of time

## Lab Files

- `templates/` - CloudFormation YAML templates
- `policies/` - Service Control Policy JSON files
- `scripts/` - Deployment and validation scripts
- `docs/` - Additional documentation and references

## Getting Started

Begin with [Part 1: Foundation Concepts](./part-1-foundation.md) to understand the core principles before diving into hands-on exercises.

## Support

If you encounter issues during this lab:
1. Check the troubleshooting section in each part
2. Review the AWS documentation links provided
3. Verify your AWS permissions and CLI configuration

## Next Steps

After completing this lab, consider exploring:
- Lab 4: Advanced CloudFormation Patterns
- Lab 5: Multi-Account CloudFormation Deployment
- Lab 6: CloudFormation Custom Resources for Compliance
