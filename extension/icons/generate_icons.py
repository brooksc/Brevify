from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size):
    # Create a new image with a white background
    image = Image.new('RGBA', (size, size), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw a blue circle
    margin = size // 8
    draw.ellipse([margin, margin, size - margin, size - margin], fill='#0066cc')
    
    # Add a "B" in white
    try:
        # Try to get a system font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=size//2)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw the text
    text = "B"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    draw.text((x, y), text, fill='white', font=font)
    
    # Save the image
    filename = f'icon{size}.png'
    image.save(filename)
    return filename

# Create icons in different sizes
sizes = [16, 32, 48, 128]
for size in sizes:
    create_icon(size)
