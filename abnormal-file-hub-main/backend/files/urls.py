# filepath: c:\Users\nanid\Downloads\AbnormalSecurityProject\abnormal-file-vault\abnormal-file-hub-main\backend\files\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileViewSet

router = DefaultRouter()
router.register(r'files', FileViewSet)

urlpatterns = [
    path('', include(router.urls)),  # All routes from 'router' will be included
]