from PIL import Image, ImageDraw, ImageFont
import os

def create_sign_image(text, output_path):
    # Create a new image with a white background
    width = 400
    height = 400
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw a black border
    border_width = 10
    draw.rectangle([0, 0, width-1, height-1], outline='black', width=border_width)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Center the text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # Draw the text
    draw.text((text_x, text_y), text, fill='black', font=font)
    
    # Save the image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)

# Create the missing sign images
signs = [
    ('LEFT\nTURN\nONLY', 'media/question_images/left_turn_only.jpg'),
    ('SCHOOL\nZONE', 'media/question_images/school_zone.jpg')
]

for text, path in signs:
    create_sign_image(text, path)
