from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a new image with a white background
    size = (256, 256)
    image = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a circle
    circle_color = (0, 136, 204)  # Telegram blue
    draw.ellipse([20, 20, 236, 236], fill=circle_color)
    
    # Draw the letter T
    try:
        font = ImageFont.truetype("arial.ttf", 160)
    except:
        font = ImageFont.load_default()
    
    text_color = (255, 255, 255)  # White
    text = "T"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2 - 10  # Slight adjustment for visual balance
    
    draw.text((x, y), text, font=font, fill=text_color)
    
    # Save as ICO
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    image.save(icon_path, format='ICO', sizes=[(256, 256)])
    
    return icon_path

if __name__ == "__main__":
    create_icon() 