from PIL import Image, ImageDraw
import base64
import io

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

# Print the base64 string
print(base64_string)