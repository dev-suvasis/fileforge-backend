from django.urls import path

from .views import convert_document_api

urlpatterns = [
    path('convert/', convert_document_api),
]