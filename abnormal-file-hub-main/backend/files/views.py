import hashlib
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import File
from .serializers import FileSerializer
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum



class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the file hash based on its content (using SHA256)
        sha256_hash = hashlib.sha256()

        try:
            # Read the file in chunks to handle large files
            for chunk in file_obj.chunks():
                sha256_hash.update(chunk)
        except Exception as e:
            return Response({'error': 'Error processing file for hashing'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        file_hash = sha256_hash.hexdigest()

        # Prepare the file data for creation or update
        file_data = {
            'original_filename': file_obj.name,
            'file_type': file_obj.content_type,
            'size': file_obj.size,
            'file_hash': file_hash
        }

        # Try to fetch the file by its hash (duplicate detection)
        try:
            file_instance = File.objects.get(file_hash=file_hash)
            # File exists, so we increment the reference count
            file_instance.reference_count += 1
            file_instance.save()

            serializer = self.get_serializer(file_instance)
            return Response({
                'message': 'Duplicate file detected. Returning existing file.',
                'file': serializer.data
            }, status=status.HTTP_200_OK)

        except File.DoesNotExist:
            # File doesn't exist, so create a new file
            file_instance = File.objects.create(file=file_obj, **file_data)
            file_instance.reference_count = 1  # Set reference count to 1 for new file
            file_instance.save()

            serializer = self.get_serializer(file_instance)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        queryset = File.objects.all()
        name = self.request.query_params.get('name')
        file_type = self.request.query_params.get('file_type')
        min_size = self.request.query_params.get('min_size')
        max_size = self.request.query_params.get('max_size')
        upload_date = self.request.query_params.get('upload_date')  # format: YYYY-MM-DD

        if name:
            queryset = queryset.filter(original_filename__icontains=name)
        if file_type:
            queryset = queryset.filter(file_type__icontains=file_type)
        if min_size:
            queryset = queryset.filter(size__gte=int(min_size))
        if max_size:
            queryset = queryset.filter(size__lte=int(max_size))
        if upload_date:
            queryset = queryset.filter(uploaded_at__date=upload_date)

        return queryset

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        file_instance = get_object_or_404(File, pk=pk)
        file_handle = file_instance.file.open()
        response = FileResponse(file_handle, content_type=file_instance.file_type)
        response['Content-Disposition'] = f'attachment; filename="{file_instance.original_filename}"'
        return response

    def bytes_to_mb(self, size_in_bytes):
        return round(size_in_bytes / (1024 * 1024), 2)

    @action(detail=False, methods=['get'], url_path='storage-savings', permission_classes=[AllowAny])
    def storage_savings(self, request):
        """
        This view calculates the storage savings for all files, showing the total requested storage size,
        the unique storage used, and the storage saved due to deduplication.
        """
        # Calculate storage savings by considering reference counts
        unique_files = File.objects.all()

        total_requested_size = 0
        unique_storage_used = 0

        for file in unique_files:
            # Add to actual storage used
            unique_storage_used += file.size

            # Add to total upload size across all references
            total_requested_size += file.size * file.reference_count

        storage_saved = total_requested_size - unique_storage_used

        return Response({
            'total_requested_upload_size_mb': self.bytes_to_mb(total_requested_size),
            'unique_storage_used_mb': self.bytes_to_mb(unique_storage_used),
            'storage_saved_mb': self.bytes_to_mb(storage_saved)
        })
