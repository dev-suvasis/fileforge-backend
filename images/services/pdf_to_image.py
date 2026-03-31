import os
import uuid
from pdf2image import convert_from_path
from django.conf import settings

OUTPUT_DIR = os.path.join(settings.BASE_DIR, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def pdf_to_image(input_path, target_format='png'):
    try:
        images = convert_from_path(input_path)

        output_files = []

        for i, img in enumerate(images):
            output_path = os.path.join(
                OUTPUT_DIR,
                f"{uuid.uuid4()}_{i}.{target_format}"
            )
            img.save(output_path, target_format.upper())
            output_files.append(output_path)

        return output_files

    except Exception as e:
        raise Exception(f"PDF to Image failed: {str(e)}")