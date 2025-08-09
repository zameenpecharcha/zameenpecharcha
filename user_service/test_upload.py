from app.utils.s3_utils import upload_bytes_and_get_url, build_user_media_key, get_bucket_name, verify_s3_connection
from app.utils.log_utils import log_msg
from PIL import Image, ImageDraw
import io
import base64

def create_test_image():
    # Create a new image with a white background
    width = 100
    height = 100
    image = Image.new('RGB', (width, height), 'white')

    # Get a drawing context
    draw = ImageDraw.Draw(image)

    # Draw a simple blue rectangle
    draw.rectangle([20, 20, 80, 80], fill='blue')

    # Save to a bytes buffer
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()

def test_s3_upload():
    try:
        # Create test image
        log_msg("info", "Creating test image...")
        image_bytes = create_test_image()
        
        # Get bucket name
        bucket = get_bucket_name()
        log_msg("info", f"Using bucket: {bucket}")
        
        # Verify S3 connection
        log_msg("info", "Verifying S3 connection...")
        if not verify_s3_connection(bucket):
            log_msg("error", "Failed to connect to S3 bucket")
            return False
            
        # Build S3 key
        user_id = 2  # Test user ID
        key = build_user_media_key(user_id, is_profile=True, file_name="test_profile.jpg")
        log_msg("info", f"Using S3 key: {key}")
        
        # Upload to S3
        log_msg("info", "Uploading to S3...")
        media_url = upload_bytes_and_get_url(
            bucket=bucket,
            key=key,
            content_bytes=image_bytes,
            content_type='image/jpeg'
        )
        
        log_msg("info", f"Successfully uploaded. URL: {media_url}")
        return True
        
    except Exception as e:
        log_msg("error", f"Error in test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_s3_upload()
    print(f"\nTest {'succeeded' if success else 'failed'}")