import os
from typing import Dict
import boto3
from botocore.exceptions import ClientError

# Simple in-memory cache per Lambda execution environment
_SECRET_CACHE: Dict[str, str] = {}


def get_secret_value(secret_id: str) -> str:
    """
    Fetch secret value from AWS Secrets Manager.
    secret_id can be secret name or ARN.
    Never log the returned secret.
    """
    if secret_id in _SECRET_CACHE:
        return _SECRET_CACHE[secret_id]

    client = boto3.client("secretsmanager", region_name=os.environ.get("AWS_REGION"))
    try:
        resp = client.get_secret_value(SecretId=secret_id)
    except ClientError as e:
        # Don't leak secret_id in logs here; caller will wrap with safe message.
        raise e

    secret_string = resp.get("SecretString")
    if not secret_string:
        raise ValueError("SecretString is empty")

    _SECRET_CACHE[secret_id] = secret_string
    return secret_string