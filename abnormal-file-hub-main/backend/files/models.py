from django.db import models
import uuid
import os
from django.db.models import Sum

def file_upload_path(instance, filename):
    """Generate file path for new file upload"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', filename)

class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=file_upload_path)
    original_filename = models.CharField(max_length=255, db_index=True)  # Added index for better search performance
    file_type = models.CharField(max_length=100, db_index=True)  # Added index for filtering by file type
    size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Added index for filtering by date
    file_hash = models.CharField(max_length=64, unique=True)
    reference_count = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.original_filename

    @property
    def storage_saved(self):
        """
        Calculate the storage saved due to the file being referenced multiple times.
        This assumes that the file is only stored once and subsequent references do not consume additional storage.
        """
        return (self.reference_count - 1) * self.size

    @classmethod
    def calculate_storage_savings(cls):
        """
        Calculate the overall storage savings across all files in the database.
        """
        unique_files = cls.objects.filter(reference_count__gte=1)

        total_requested_size = unique_files.aggregate(total_size=Sum('size'))['total_size'] or 0
        unique_storage_used = unique_files.aggregate(unique_size=Sum('size', filter=models.Q(reference_count=1)))['unique_size'] or 0

        # Calculate storage saved
        storage_saved = total_requested_size - unique_storage_used

        return {
            'total_requested_upload_size_mb': cls.bytes_to_mb(total_requested_size),
            'unique_storage_used_mb': cls.bytes_to_mb(unique_storage_used),
            'storage_saved_mb': cls.bytes_to_mb(storage_saved)
        }

    @staticmethod
    def bytes_to_mb(size_in_bytes):
        """Convert bytes to megabytes."""
        return round(size_in_bytes / (1024 * 1024), 2)
