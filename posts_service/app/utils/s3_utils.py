import base64
import os
import re
from typing import Optional, Tuple
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError


_DATA_URL_RE = re.compile(r"^data:(?P<content_type>[^;]+);base64,(?P<data>.+)$")


def _split_data_url(base64_string: str) -> Tuple[Optional[str], str]:
    match = _DATA_URL_RE.match(base64_string)
    if match:
        return match.group("content_type"), match.group("data")
    return None, base64_string


def _infer_extension_from_content_type(content_type: Optional[str]) -> str:
    mapping = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
        "image/tiff": ".tiff",
    }
    return mapping.get((content_type or "").lower(), "")


def _choose_file_name(file_name: Optional[str], content_type: Optional[str], fallback_prefix: str) -> str:
    if file_name and "." in file_name:
        return file_name
    extension = _infer_extension_from_content_type(content_type)
    if not extension and file_name:
        extension = ".jpg"
    if not file_name:
        file_name = f"{fallback_prefix}_{uuid4().hex}"
    return f"{file_name}{extension if not file_name.endswith(extension) else ''}"


def upload_base64_to_s3(*, base64_string: str, key: str, content_type: Optional[str] = None, acl: str = "public-read") -> Tuple[str, int]:
    bucket = os.getenv("S3_BUCKET_NAME") or os.getenv("AWS_S3_BUCKET") or "zpc-app"
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"

    detected_content_type, raw_b64 = _split_data_url(base64_string)
    effective_content_type = content_type or detected_content_type or "application/octet-stream"

    binary_data = base64.b64decode(raw_b64)

    client_kwargs = {"region_name": region}
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

    s3 = boto3.client("s3", **client_kwargs)

    put_kwargs = {
        "Bucket": bucket,
        "Key": key,
        "Body": binary_data,
        "ContentType": effective_content_type,
    }
    try:
        if acl:
            s3.put_object(**put_kwargs, ACL=acl)
        else:
            s3.put_object(**put_kwargs)
    except ClientError as e:
        error_code = getattr(e, "response", {}).get("Error", {}).get("Code")
        if error_code == "AccessControlListNotSupported":
            s3.put_object(**put_kwargs)
        else:
            raise

    public_url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    return public_url, len(binary_data)


def build_post_key(post_id: int, media_id: int, file_name: Optional[str], content_type: Optional[str]) -> str:
    safe_name = _choose_file_name(file_name, content_type, fallback_prefix="image")
    return f"post/{post_id}/{media_id}/{safe_name}"


