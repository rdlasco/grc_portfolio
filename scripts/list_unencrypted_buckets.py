#!/usr/bin/env python3
"""
list_unencrypted_buckets.py
--------------------------
This script enumerates **all** S3 buckets in the currently-configured AWS account
and prints out the buckets that do **not** have a default server-side encryption
configuration.

Requirements:
  • Python 3.8+
  • boto3: ``pip install boto3``

Usage examples:
  $ python list_unencrypted_buckets.py               # Uses default profile & region
  $ AWS_PROFILE=myprofile python list_unencrypted_buckets.py

Security notice:
  The script makes **read-only** API calls (ListBuckets and
  GetBucketEncryption). No resources are modified.
"""

# Standard Library Imports
import sys
from typing import List

# Third-party Imports
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound, EndpointConnectionError

def is_bucket_encrypted(bucket_name: str, s3_client) -> bool:
    """Return ``True`` if the bucket **has** a default encryption configuration.

    A bucket is considered encrypted if the GetBucketEncryption call succeeds
    without raising ``ServerSideEncryptionConfigurationNotFoundError``.

    Parameters
    ----------
    bucket_name : str
        Name of the S3 bucket to test.
    s3_client : botocore.client.S3
        Boto3 S3 client.

    Returns
    -------
    bool
        ``True``  – bucket **is** encrypted.
        ``False`` – bucket is **not** encrypted (or encryption config missing).
    """
    try:
        s3_client.get_bucket_encryption(Bucket=bucket_name)
        # If the above call does NOT raise an exception, encryption is enabled.
        return True
    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code", "")
        # This specific error means the bucket lacks a default encryption config.
        if error_code == "ServerSideEncryptionConfigurationNotFoundError":
            return False
        # Any other error (e.g., AccessDenied) is re-raised so the user sees it.
        raise


def list_unencrypted_buckets(s3_client) -> List[str]:
    """Return a list of buckets that do NOT have default encryption."""
    try:
        response = s3_client.list_buckets()
    except (ClientError, EndpointConnectionError) as err:
        # Fatal: we cannot enumerate buckets – report and bail out gracefully.
        print(f"[ERROR] Unable to list buckets: {err}")
        return []
    unencrypted: List[str] = []

    for bucket in response.get("Buckets", []):
        name = bucket["Name"]
        try:
            if not is_bucket_encrypted(name, s3_client):
                unencrypted.append(name)
        except ClientError as err:
            # The user may lack permissions for some buckets. Log and continue.
            print(f"[WARN] Skipping bucket '{name}' – {err.response['Error']['Code']}")
            continue

    return unencrypted


def main() -> None:
    """Entry point. Creates a client and prints unencrypted buckets."""
    try:
        s3 = boto3.client("s3")
    except (NoCredentialsError, ProfileNotFound) as cred_err:
        print("[ERROR] AWS credentials not found. Configure them and retry.")
        sys.exit(1)

    try:
        unencrypted_buckets = list_unencrypted_buckets(s3)
    except EndpointConnectionError as net_err:
        print(f"[ERROR] Network error while contacting AWS: {net_err}")
        sys.exit(1)

    if unencrypted_buckets:
        print("\nUnencrypted buckets detected (default encryption missing):")
        for bucket in unencrypted_buckets:
            print(f"  • {bucket}")
    else:
        print("All buckets have default server-side encryption enabled. ✅")


if __name__ == "__main__":
    main()
