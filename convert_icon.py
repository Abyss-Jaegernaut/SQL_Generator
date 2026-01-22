from PIL import Image
import os

png_path = r"C:/Users/couli/.gemini/antigravity/brain/b7f085d1-67e0-4416-a437-01e3c2194db9/sql_generator_icon_1769020557895.png"
ico_path = r"d:/SQL_GENERATOR/icon.ico"

if os.path.exists(png_path):
    img = Image.open(png_path)
    # Resize to standard icon sizes
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, sizes=icon_sizes)
    print(f"Icon saved to {ico_path}")
else:
    print(f"File not found: {png_path}")
