from app.utils.s3_utils import upload_bytes_and_get_url, get_bucket_name, get_region, verify_s3_connection
from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw
import io

# Load environment variables
load_dotenv()

def create_dummy_image_bytes(size=(100, 100), color="blue"):
    img = Image.new('RGB', size, color='white')
    d = ImageDraw.Draw(img)
    d.rectangle([20, 20, 80, 80], fill=color)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def run_aws_s3_upload_test():
    print("Starting AWS S3 Upload Test")
    print("==================================================")

    # 1. Check AWS Credentials
    print("\n1. Checking AWS Credentials...")
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    bucket_name = get_bucket_name()
    aws_region = get_region()

    print(f"AWS Access Key present: {bool(aws_access_key)}")
    print(f"AWS Secret Key present: {bool(aws_secret_key)}")
    print(f"AWS Bucket Name: {bucket_name}")
    print(f"AWS Region: {aws_region}")

    if not all([aws_access_key, aws_secret_key, bucket_name, aws_region]):
        print("❌ Missing one or more AWS environment variables. Please set them in .env file.")
        return False

    # 2. Create test image
    print("\n2. Creating test image...")
    test_image_bytes = create_dummy_image_bytes()
    print(f"Created test image: {len(test_image_bytes)} bytes")
    print("✅ Test image created successfully")

    # 3. Test S3 connection
    print("\n3. Testing S3 connection...")
    if not verify_s3_connection(bucket_name):
        print("❌ S3 connection failed. Check logs for details.")
        return False
    print("✅ S3 connection successful")

    # 4. Attempt S3 upload
    print("\n4. Attempting S3 upload...")
    test_key = "test/test_profile.jpg"
    try:
        uploaded_url = upload_bytes_and_get_url(
            bucket=bucket_name,
            key=test_key,
            content_bytes=test_image_bytes,
            content_type="image/jpeg"
        )
        print(f"Successfully uploaded to: {uploaded_url}")
        print("✅ Upload successful")
        print(f"\nFinal URL: {uploaded_url}")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

if __name__ == "__main__":
    if run_aws_s3_upload_test():
        print("\nTest passed!")
    else:
        print("\nTest failed")