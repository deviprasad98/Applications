from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import File

class FileUploadTests(APITestCase):
    def test_file_upload_success(self):
        """Test uploading a valid file."""
        file_data = SimpleUploadedFile("test.txt", b"Hello, world!", content_type="text/plain")
        response = self.client.post('/api/files/', {'file': file_data})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('file_hash', response.data)

    def test_file_upload_no_file(self):
        """Test uploading without providing a file."""
        response = self.client.post('/api/files/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'No file provided')

    def test_file_upload_large_file(self):
        """Test uploading a large file (simulate large content)."""
        large_content = b"A" * (10 * 1024 * 1024)  # 10 MB
        file_data = SimpleUploadedFile("large_file.txt", large_content, content_type="text/plain")
        response = self.client.post('/api/files/', {'file': file_data})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

