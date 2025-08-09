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
    img_bytes = buffer.getvalue()

    # Convert to base64
    base64_string = base64.b64encode(img_bytes).decode('utf-8')
    
    print("Image created successfully!")
    print("\nBase64 string (first 100 chars):")
    print(base64_string[:100])
    print("\nTotal base64 length:", len(base64_string))
    
    return base64_string

if __name__ == "__main__":
    base64_image = create_test_image()
    
    # Create a sample request JSON
    request_json = {
        "user_id": 2,
        "media": {
            "media_type": "image",
            "file_name": "test_profile.jpg",
            "content_type": "image/jpeg",
            "file_content": base64_image,
            "caption": "Test profile photo"
        }
    }
    
    print("\nSample request JSON (truncated):")
    print(str(request_json).replace(base64_image, base64_image[:50] + "..."))