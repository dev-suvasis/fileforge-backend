import os
import uuid
import zipfile
import tempfile

from django.conf import settings
from django.http import FileResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.processor import convert_image, SUPPORTED_FORMATS
from .services.image_to_pdf import image_to_pdf
from .services.pdf_to_image import pdf_to_image

UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _cleanup(*paths):
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except OSError:
            pass


def _save_upload(file):
    """Save an uploaded file with a UUID name. Returns (input_path, extension)."""
    extension = os.path.splitext(file.name)[1].lower()
    filename = str(uuid.uuid4()) + extension
    input_path = os.path.join(UPLOAD_DIR, filename)
    with open(input_path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)
    return input_path, extension


@api_view(['POST'])
def convert_image_view(request):
    """
    Convert an image from one format to another.

    Form fields:
      file          – image file
      target_format – e.g. png, jpg, webp, bmp, tiff, gif
    """
    file = request.FILES.get('file')
    target_format = request.data.get('target_format', '').strip().lower()

    if not file or not target_format:
        return Response({'error': 'file and target_format are required'}, status=400)

    input_ext = os.path.splitext(file.name)[1].lower().lstrip('.')

    if input_ext not in SUPPORTED_FORMATS:
        return Response({'error': f'Unsupported input format: {input_ext}'}, status=400)

    if target_format not in SUPPORTED_FORMATS:
        return Response({'error': f'Unsupported target format: {target_format}'}, status=400)

    input_path, _ = _save_upload(file)
    output_path = None

    try:
        output_path = convert_image(input_path, target_format)

        def _iter_and_cleanup():
            with open(output_path, 'rb') as fh:
                yield from fh
            _cleanup(input_path, output_path)

        return FileResponse(
            _iter_and_cleanup(),
            as_attachment=True,
            filename=os.path.basename(output_path),
        )

    except Exception as e:
        _cleanup(input_path, output_path)
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def image_to_pdf_view(request):
    """
    Convert an image to PDF.

    Form fields:
      file – image file (jpg, png, webp, …)
    """
    file = request.FILES.get('file')

    if not file:
        return Response({'error': 'file is required'}, status=400)

    input_path, _ = _save_upload(file)   # ✅ UUID filename — no path traversal
    output_path = None

    try:
        output_path = image_to_pdf(input_path)

        def _iter_and_cleanup():
            with open(output_path, 'rb') as fh:
                yield from fh
            _cleanup(input_path, output_path)

        return FileResponse(
            _iter_and_cleanup(),
            as_attachment=True,
            filename=os.path.basename(output_path),
        )

    except Exception as e:
        _cleanup(input_path, output_path)
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def pdf_to_image_view(request):
    """
    Convert a PDF to images (one per page), returned as a ZIP archive.

    Form fields:
      file          – PDF file
      target_format – image format (default: png)
    """
    file = request.FILES.get('file')
    target_format = request.data.get('target_format', 'png').strip().lower()

    if not file:
        return Response({'error': 'file is required'}, status=400)

    input_path, _ = _save_upload(file)   # ✅ UUID filename — no path traversal
    output_files = []

    try:
        output_files = pdf_to_image(input_path, target_format)

        if not output_files:
            raise Exception("No pages were extracted from the PDF")

        # If only one page, return it directly
        if len(output_files) == 1:
            single = output_files[0]

            def _iter_single():
                with open(single, 'rb') as fh:
                    yield from fh
                _cleanup(input_path, single)

            return FileResponse(
                _iter_single(),
                as_attachment=True,
                filename=os.path.basename(single),
            )

        # Multiple pages → zip them all
        tmp_zip = tempfile.NamedTemporaryFile(
            delete=False, suffix='.zip', dir=os.path.join(settings.BASE_DIR, 'outputs')
        )
        tmp_zip.close()

        with zipfile.ZipFile(tmp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for page_path in output_files:
                zf.write(page_path, arcname=os.path.basename(page_path))

        def _iter_zip():
            with open(tmp_zip.name, 'rb') as fh:
                yield from fh
            _cleanup(input_path, tmp_zip.name, *output_files)

        return FileResponse(
            _iter_zip(),
            as_attachment=True,
            filename='pages.zip',
            content_type='application/zip',
        )

    except Exception as e:
        _cleanup(input_path, *output_files)
        return Response({'error': str(e)}, status=500)
