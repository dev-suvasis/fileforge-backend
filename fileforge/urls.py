from django.urls import path, include
from .views import health_check

urlpatterns = [
    path('health/', health_check),
    path('api/docs/', include('documents.urls')),
    path('api/images/', include('images.urls')),
]
