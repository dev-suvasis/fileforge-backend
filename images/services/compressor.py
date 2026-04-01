import os
import uuid
import random

from PIL import Image
from django.conf import settings

OUTPUT_DIR = os.path.join(settings.BASE_DIR, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mild: good quality, moderate size reduction
MILD_QUALITY_MIN = 70
MILD_QUALITY_MAX = 85

# Heavy: aggressive size reduction, noticeable quality loss
HEAVY_QUALITY_MIN = 30
HEAVY_QUALITY_MAX = 50

# Formats that support quality-based compression
COMPRESSIBLE_FORMATS = ['jpg', 'jpeg', 'webp', 'png']


def compress_image(input_path, level):
    """
    Compress an image by the given level.

    Parameters
    ----------
    input_path : str
        Path to the source image file.
    level : str
        'mild'  → quality randomly chosen from 70–85
        'heavy' → quality randomly chosen from 30–50

    Returns
    -------
    str
        Path to the compressed output file.
    """
    level = level.lower()

    if level == 'mild':
        quality = random.randint(MILD_QUALITY_MIN, MILD_QUALITY_MAX)
    elif level == 'heavy':
        quality = random.randint(HEAVY_QUALITY_MIN, HEAVY_QUALITY_MAX)
    else:
        raise Exception("Invalid compression level. Use 'mild' or 'heavy'.")

    try:
        img = Image.open(input_path)

        # Determine output extension from source file
        ext = os.path.splitext(input_path)[1].lower().lstrip('.')
        if ext not in COMPRESSIBLE_FORMATS:
            raise Exception(
                f"Compression not supported for format: {ext}. "
                f"Supported formats: {', '.join(COMPRESSIBLE_FORMATS)}"
            )

        output_path = os.path.join(OUTPUT_DIR, str(uuid.uuid4()) + f'.{ext}')

        if ext in ('jpg', 'jpeg'):
            # JPEG needs RGB mode — flatten transparency if present
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=quality, optimize=True)

        elif ext == 'webp':
            img.save(output_path, 'WEBP', quality=quality, method=6)

        elif ext == 'png':
            # PNG is lossless — use optimize + max compression level instead
            # compress_level: 0 (none) → 9 (max); map quality range to this
            compress_level = 9 if level == 'heavy' else 6
            img.save(output_path, 'PNG', optimize=True, compress_level=compress_level)

        return output_path

    except Exception as e:
        raise Exception(f"Image compression failed: {str(e)}")
