import os
import uuid

from PIL import Image
from django.conf import settings

UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'uploads')
OUTPUT_DIR = os.path.join(settings.BASE_DIR, 'outputs')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff', 'gif']


def convert_image(input_path, target_format):
    try:
        target_format = target_format.lower()

        if target_format not in SUPPORTED_FORMATS:
            raise Exception(f"Unsupported target format: {target_format}")

        img = Image.open(input_path)

        if target_format in ('jpg', 'jpeg'):
            # JPEG cannot store transparency or palette — normalise every mode
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # last channel = alpha
                img = background
            elif img.mode == 'P':
                # Palette mode: convert via RGBA to preserve any transparency
                img = img.convert('RGBA')
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert('RGB')

        # Normalise PIL format name (jpg → JPEG)
        pil_format = 'JPEG' if target_format in ('jpg', 'jpeg') else target_format.upper()

        output_path = os.path.join(OUTPUT_DIR, str(uuid.uuid4()) + f'.{target_format}')
        img.save(output_path, pil_format)

        return output_path

    except Exception as e:
        raise Exception(f"Image conversion failed: {str(e)}")
