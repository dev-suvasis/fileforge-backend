from django.urls import path

from .views import convert_doc_to_pdf, convert_document_api

urlpatterns = [
    path('to-pdf/', convert_doc_to_pdf),
    path('convert/', convert_document_api),
]
