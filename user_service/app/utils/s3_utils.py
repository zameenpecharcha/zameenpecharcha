import os
import boto3
from app.utils.log_utils import log_msg
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError


def get_bucket_name() -> str:
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME', '')
    log_msg("info", f"[S3] Using bucket name: '{bucket_name}'")
    return bucket_name


def get_region() -> str:
    return os.getenv('AWS_DEFAULT_REGION', 'us-east-1')


def get_s3_client():
    region = get_region()
    log_msg("info", f"[S3] Creating client. Region={region}")
    session = boto3.session.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=region,
    )
    client = session.client('s3', config=Config(s3={'addressing_style': 'virtual'}))
    return client


def verify_s3_connection(bucket: str) -> bool:
    """Ping S3 by calling head_bucket. Returns True on success, False otherwise, with logs."""
    try:
        s3 = get_s3_client()
        log_msg("info", f"[S3] Verifying connection to bucket='{bucket}'")
        s3.head_bucket(Bucket=bucket)
        log_msg("info", f"[S3] Verified access to bucket '{bucket}'")
        return True
    except ClientError as e:
        code = e.response.get('Error', {}).get('Code')
        log_msg("error", f"[S3] head_bucket failed for bucket='{bucket}'. Code={code}, Error={e}")
        return False
    except BotoCoreError as e:
        log_msg("error", f"[S3] BotoCoreError while verifying bucket='{bucket}': {e}")
        return False
    except Exception as e:
        log_msg("error", f"[S3] Unexpected error verifying bucket='{bucket}': {e}")
        return False


def upload_bytes_and_get_url(bucket: str, key: str, content_bytes: bytes, content_type: str) -> str:
    s3 = get_s3_client()
    size = len(content_bytes) if content_bytes else 0
    log_msg("info", f"[S3] Upload start. Bucket='{bucket}', Key='{key}', SizeBytes={size}, ContentType='{content_type}'")
    try:
        s3.put_object(Bucket=bucket, Key=key, Body=content_bytes, ContentType=content_type)
        region = get_region()
        if region == 'us-east-1':
            url = f"https://{bucket}.s3.amazonaws.com/{key}"
        else:
            url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
        log_msg("info", f"[S3] Upload success. URL='{url}'")
        return url
    except (ClientError, BotoCoreError) as e:
        log_msg("error", f"[S3] Upload failed. Bucket='{bucket}', Key='{key}'. Error={e}")
        raise
    except Exception as e:
        log_msg("error", f"[S3] Unexpected error during upload. Bucket='{bucket}', Key='{key}'. Error={e}")
        raise


def build_user_media_key(user_id: int, is_profile: bool, file_name: str) -> str:
    folder = 'profile photo' if is_profile else 'cover photo'
    return f"user/{user_id}/{folder}/{file_name}"

