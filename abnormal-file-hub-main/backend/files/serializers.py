from rest_framework import serializers
from .models import File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            'id',
            'file',
            'original_filename',
            'file_type',
            'size',
            'file_hash',        # This field contains the hash of the file for deduplication.
            'reference_count',  # This field stores the count of references to the file (used for deduplication).
            'uploaded_at'       # This is the upload date field that can be used for filtering.
        ]
        read_only_fields = ['file_hash', 'reference_count']

