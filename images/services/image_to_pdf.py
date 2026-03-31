import os
import uuid
from PIL import Image
from django.conf import settings

OUTPUT_DIR = os.path.join(settings.BASE_DIR, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def image_to_pdf(input_path):
    try:
        img = Image.open(input_path)

        # Convert to RGB (PDF doesn't support RGBA)
        if img.mode in ('RGBA', 'LA'):
            img = img.convert('RGB')

        output_path = os.path.join(
            OUTPUT_DIR,
            str(uuid.uuid4()) + ".pdf"
        )

        img.save(output_path, "PDF", resolution=100.0)

        return output_path

    except Exception as e:
        raise Exception(f"Image to PDF failed: {str(e)}")