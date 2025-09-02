import os
import boto3
from typing import Optional, Tuple


def _s3_client(region: Optional[str] = None):
    region_name = region or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
    client_kwargs = {"region_name": region_name}
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    if aws_access_key_id and aws_secret_access_key:
        client_kwargs.update({
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
        })
        if aws_session_token:
            client_kwargs["aws_session_token"] = aws_session_token
    return boto3.client("s3", **client_kwargs)


def build_post_object_key(file_name: str) -> str:
    # Flat uploads path; posts service will move under post/{id}/{media_id}/ when uploaded again if needed
    # Here we upload directly as final asset, so we keep uploads/post/<uuid or name>
    # Keep simple: uploads/post/<file_name>
    return f"uploads/post/{file_name}"


def generate_presigned_put_url(file_name: str, content_type: Optional[str] = None, expires_in: int = 3600) -> Tuple[str, str, str]:
    bucket = os.getenv("S3_BUCKET_NAME") or os.getenv("AWS_S3_BUCKET") or "zpc-app"
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
    key = build_post_object_key(file_name)
    s3 = _s3_client(region)
    params = {"Bucket": bucket, "Key": key}
    if content_type:
        params["ContentType"] = content_type
    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params=params,
        ExpiresIn=expires_in,
    )
    public_url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    return url, key, public_url


