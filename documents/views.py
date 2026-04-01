import os
import uuid

from django.conf import settings
from django.http import FileResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.converter import convert_document

UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _cleanup(*paths):
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except OSError:
            pass


@api_view(['POST'])
def convert_document_api(request):
    """
    General document conversion endpoint.

    Form fields:
      file          – the document to convert
      target_format – desired output format (pdf, docx, xlsx, pptx, …)
    """
    file = request.FILES.get('file')
    target_format = request.data.get('target_format', '').strip().lower()

    if not file:
        return Response({'error': 'file is required'}, status=400)
    if not target_format:
        return Response({'error': 'target_format is required'}, status=400)

    extension = os.path.splitext(file.name)[1].lower()

    filename = str(uuid.uuid4()) + extension
    input_path = os.path.join(UPLOAD_DIR, filename)
    output_path = None

    with open(input_path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)

    try:
        output_path = convert_document(input_path, extension, target_format)

        def _iter_and_cleanup():
            with open(output_path, 'rb') as fh:
                yield from fh
            _cleanup(input_path, output_path)

        response = FileResponse(
            _iter_and_cleanup(),
            as_attachment=True,
            filename=os.path.basename(output_path),
        )
        return response

    except Exception as e:
        _cleanup(input_path, output_path)
        return Response({'error': str(e)}, status=500)
