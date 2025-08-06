#!/usr/bin/env python3
"""
CloudFormation Template Validation Script
Validates YAML syntax and CloudFormation template structure
"""

import os
import sys
import yaml
import boto3
import json
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError

def validate_yaml_syntax(file_path):
    """Validate YAML syntax"""
    try:
        with open(file_path, 'r') as file:
            yaml.safe_load(file)
        return True, "Valid YAML syntax"
    except yaml.YAMLError as e:
        return False, f"YAML syntax error: {str(e)}"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def validate_cloudformation_template(file_path):
    """Validate CloudFormation template using AWS API"""
    try:
        cf_client = boto3.client('cloudformation')
        
        with open(file_path, 'r') as file:
            template_body = file.read()
        
        response = cf_client.validate_template(TemplateBody=template_body)
        return True, "Valid CloudFormation template"
    
    except NoCredentialsError:
        return False, "AWS credentials not configured"
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return False, f"CloudFormation validation error ({error_code}): {error_message}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def check_security_best_practices(file_path):
    """Check for security best practices in CloudFormation templates"""
    issues = []
    
    try:
        with open(file_path, 'r') as file:
            template = yaml.safe_load(file)
        
        resources = template.get('Resources', {})
        
        for resource_name, resource_config in resources.items():
            resource_type = resource_config.get('Type', '')
            properties = resource_config.get('Properties', {})
            
            # Check S3 bucket security
            if resource_type == 'AWS::S3::Bucket':
                # Check for public access block
                if 'PublicAccessBlockConfiguration' not in properties:
                    issues.append(f"{resource_name}: Missing PublicAccessBlockConfiguration")
                
                # Check for encryption
                if 'BucketEncryption' not in properties:
                    issues.append(f"{resource_name}: Missing BucketEncryption")
                
                # Check for versioning
                if 'VersioningConfiguration' not in properties:
                    issues.append(f"{resource_name}: Missing VersioningConfiguration")
            
            # Check security groups
            elif resource_type == 'AWS::EC2::SecurityGroup':
                ingress_rules = properties.get('SecurityGroupIngress', [])
                for rule in ingress_rules:
                    cidr_ip = rule.get('CidrIp', '')
                    if cidr_ip == '0.0.0.0/0':
                        from_port = rule.get('FromPort', 0)
                        if from_port in [22, 3389]:  # SSH or RDP
                            issues.append(f"{resource_name}: Allows {from_port} from 0.0.0.0/0")
        
        return issues
    
    except Exception as e:
        return [f"Error checking security practices: {str(e)}"]

def main():
    """Main validation function"""
    if len(sys.argv) < 2:
        print("Usage: python validate-templates.py <template-file-or-directory>")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    
    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = list(target.glob('**/*.yml')) + list(target.glob('**/*.yaml'))
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)
    
    print("🔍 CloudFormation Template Validation")
    print("=" * 50)
    
    total_files = len(files)
    passed_files = 0
    
    for file_path in files:
        print(f"\n📄 Validating: {file_path}")
        print("-" * 30)
        
        # Check YAML syntax
        yaml_valid, yaml_message = validate_yaml_syntax(file_path)
        if yaml_valid:
            print(f"✅ YAML Syntax: {yaml_message}")
        else:
            print(f"❌ YAML Syntax: {yaml_message}")
            continue
        
        # Check CloudFormation template
        cf_valid, cf_message = validate_cloudformation_template(file_path)
        if cf_valid:
            print(f"✅ CloudFormation: {cf_message}")
        else:
            print(f"❌ CloudFormation: {cf_message}")
            continue
        
        # Check security best practices
        security_issues = check_security_best_practices(file_path)
        if not security_issues:
            print("✅ Security: No issues found")
        else:
            print("⚠️  Security Issues:")
            for issue in security_issues:
                print(f"   - {issue}")
        
        if yaml_valid and cf_valid:
            passed_files += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Summary: {passed_files}/{total_files} files passed validation")
    
    if passed_files == total_files:
        print("🎉 All templates are valid!")
        sys.exit(0)
    else:
        print("❌ Some templates have issues")
        sys.exit(1)

if __name__ == "__main__":
    main()
