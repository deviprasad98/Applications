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
