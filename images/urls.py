from django.urls import path
from .views import convert_image_view, image_to_pdf_view, pdf_to_image_view

urlpatterns = [
    path('convert/', convert_image_view),
    path('to-pdf/', image_to_pdf_view),
    path('pdf-to-image/', pdf_to_image_view),
]