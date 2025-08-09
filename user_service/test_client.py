import grpc
from app.proto_files import user_pb2, user_pb2_grpc
from PIL import Image, ImageDraw
import io
import base64

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
    image_bytes = buffer.getvalue()
    
    # Convert to base64 for debugging
    base64_str = base64.b64encode(image_bytes).decode('utf-8')
    print(f"\nBase64 image (first 100 chars):")
    print(base64_str[:100])
    print(f"Total base64 length: {len(base64_str)}")
    
    return image_bytes

def update_profile_photo():
    # Create channel and client
    channel = grpc.insecure_channel('localhost:50051')
    stub = user_pb2_grpc.UserServiceStub(channel)
    
    # Create a test token using HS256
    import jwt
    token = jwt.encode(
        {
            "sub": "2",
            "email": "test@example.com",
            "role": "user"
        },
        "your-256-bit-secret",
        algorithm="HS256"
    )
    
    # Add authentication metadata
    metadata = [
        ('authorization', f'Bearer {token}')
    ]
    
    # Create image bytes
    image_bytes = create_test_image()
    
    # Create media request
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
    
    # Create update photo request
    request = user_pb2.UpdateUserPhotoRequest(
        user_id=2,
        media=media
    )
    
    print("\nSending request with:")
    print(f"user_id: {request.user_id}")
    print("Media fields:")
    print(f"  context_id: {request.media.context_id}")
    print(f"  context_type: {request.media.context_type!r}")
    print(f"  media_type: {request.media.media_type!r}")
    print(f"  file_name: {request.media.file_name!r}")
    print(f"  content_type: {request.media.content_type!r}")
    print(f"  file_content length: {len(request.media.file_content)}")
    print(f"  caption: {request.media.caption!r}")
    print(f"  media_order: {request.media.media_order}")
    print(f"  media_size: {request.media.media_size}")
    
    try:
        # Make the call with metadata
        response = stub.UpdateProfilePhoto(request, metadata=metadata)
        print("\nResponse received:")
        print(f"User ID: {response.id}")
        print(f"Profile photo ID: {response.profile_photo_id}")
        return True
    except grpc.RpcError as e:
        print(f"\nRPC failed: {e.code()}")
        print(f"Details: {e.details()}")
        return False

if __name__ == "__main__":
    if update_profile_photo():
        print("\nProfile photo update successful!")
    else:
        print("\nProfile photo update failed!")