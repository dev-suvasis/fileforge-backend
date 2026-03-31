import os
import shutil
import subprocess
import uuid

from django.conf import settings
from pdf2docx import Converter as PDFConverter

UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'uploads')
OUTPUT_DIR = os.path.join(settings.BASE_DIR, 'outputs')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def libreoffice_convert(input_path, target_format):
    soffice_path = shutil.which("soffice") or shutil.which("libreoffice")

    if not soffice_path:
        raise Exception(
            "LibreOffice is not installed or not found in PATH. "
            "Install it with: sudo apt install libreoffice"
        )

    result = subprocess.run(
        [
            soffice_path,
            '--headless',
            '--convert-to', target_format,
            '--outdir', OUTPUT_DIR,
            input_path,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise Exception(
            f"LibreOffice conversion failed: {result.stderr.strip() or result.stdout.strip()}"
        )

    base = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(OUTPUT_DIR, base + f".{target_format}")

    if not os.path.exists(output_path):
        raise Exception(
            f"LibreOffice ran but output file was not created: {output_path}"
        )

    return output_path


def pdf_to_docx(input_path):
    output_path = os.path.join(OUTPUT_DIR, str(uuid.uuid4()) + ".docx")

    cv = PDFConverter(input_path)
    cv.convert(output_path)
    cv.close()

    return output_path


def convert_document(input_path, input_ext, target_format):
    target_format = target_format.lower()
    input_ext = input_ext.lower()

    # PDF → DOCX  (pdf2docx, no LibreOffice needed)
    if input_ext == '.pdf' and target_format == 'docx':
        return pdf_to_docx(input_path)

    # Anything → PDF  (LibreOffice)
    if target_format == 'pdf':
        return libreoffice_convert(input_path, 'pdf')

    # Other office formats via LibreOffice
    supported = ['docx', 'doc', 'pptx', 'ppt', 'xlsx', 'xls']
    if target_format in supported:
        return libreoffice_convert(input_path, target_format)

    raise Exception(f"Unsupported conversion: {input_ext} → {target_format}")
