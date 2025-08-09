from app.proto_files import user_pb2
import base64
from PIL import Image, ImageDraw
import io

def create_test_image():
    # Create a new image with a white background
    width = 100
    height = 100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    draw.rectangle([20, 20, 80, 80], fill='blue')
    
    # Save to bytes
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()

def create_test_request():
    # Create the image bytes
    image_bytes = create_test_image()
    
    # Create the media request
    media = user_pb2.MediaRequest(
        context_id=2,
        context_type='user_profile',
        media_type='image',
        file_name='test_profile.jpg',
        content_type='image/jpeg',
        file_content=image_bytes,
        caption='Profile photo',
        media_order=1,
        media_size=len(image_bytes)
    )
    
    # Create the update photo request
    request = user_pb2.UpdateUserPhotoRequest(
        user_id=2,
        media=media
    )
    
    return request

if __name__ == "__main__":
    # Create and print the request
    request = create_test_request()
    print("\nRequest fields:")
    print(f"user_id: {request.user_id}")
    print("\nMedia fields:")
    print(f"context_id: {request.media.context_id}")
    print(f"context_type: {request.media.context_type!r}")
    print(f"media_type: {request.media.media_type!r}")
    print(f"file_name: {request.media.file_name!r}")
    print(f"content_type: {request.media.content_type!r}")
    print(f"file_content length: {len(request.media.file_content)}")
    print(f"caption: {request.media.caption!r}")
    print(f"media_order: {request.media.media_order}")
    print(f"media_size: {request.media.media_size}")
