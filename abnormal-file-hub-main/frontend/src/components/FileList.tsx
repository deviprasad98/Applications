import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fileService } from '../services/fileService';
import { File } from '../types/file';

const FileList: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [fileType, setFileType] = useState('');
  const [minSize, setMinSize] = useState('');
  const [maxSize, setMaxSize] = useState('');
  const [dateRange, setDateRange] = useState({ from: '', to: '' });

  const { data: files = [], isLoading: isLoadingFiles, error: errorFiles } = useQuery({
    queryKey: ['files'],
    queryFn: fileService.getFiles,
  });

  const { data: storageData, isLoading: isLoadingStorage, error: storageError } = useQuery({
    queryKey: ['storageStats'],
    queryFn: fileService.getStorageStats,
  });

  useEffect(() => {
    applyFilters(); // Apply filters initially when files load
  }, [files]);

  const applyFilters = () => {
    let filtered = files.filter(file =>
      file.original_filename.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Define MIME type mappings for each filter category
    const typeMappings: { [key: string]: string[] } = {
      PDF: ['application/pdf'],
      Image: ['image/jpeg', 'image/png', 'image/gif'],
      Text: ['text/plain', 'text/csv'],
      Video: ['video/mp4', 'video/webm', 'video/ogg'],
    };

    if (fileType && typeMappings[fileType]) {
      filtered = filtered.filter(file => typeMappings[fileType].includes(file.file_type.toLowerCase()));
    }
    if (minSize) filtered = filtered.filter(file => file.size >= Number(minSize) * 1024 * 1024);
    if (maxSize) filtered = filtered.filter(file => file.size <= Number(maxSize) * 1024 * 1024);
    if (dateRange.from) filtered = filtered.filter(file => new Date(file.uploaded_at) >= new Date(dateRange.from));
    if (dateRange.to) filtered = filtered.filter(file => new Date(file.uploaded_at) <= new Date(dateRange.to));

    setFilteredFiles(filtered);
  };

  const [filteredFiles, setFilteredFiles] = useState<File[]>(files);

  const storageSaved = storageData?.storage_saved_mb || 0;

  if (isLoadingFiles || isLoadingStorage) return <div className="text-center text-gray-600">Loading...</div>;
  if (errorFiles || storageError) return <div className="text-center text-red-600">Error loading files or storage data.</div>;

  const bytesToMB = (sizeInBytes: number) => (sizeInBytes / (1024 * 1024)).toFixed(2);

  return (
    <div className="container mx-auto p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">File List</h2>

      <div className="bg-blue-50 p-4 rounded-lg mb-6 shadow-md">
        <h3 className="text-lg font-semibold text-blue-800 mb-2">Storage Statistics</h3>
        <p className="text-sm text-gray-700">Total Requested Upload Size: {storageData?.total_requested_upload_size_mb || 0} MB</p>
        <p className="text-sm text-gray-700">Unique Storage Used: {storageData?.unique_storage_used_mb || 0} MB</p>
        <p className="text-sm text-green-600 font-medium">Storage Saved: {storageSaved} MB</p>
      </div>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Search files by name..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="bg-white p-4 shadow sm:rounded-lg mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <select
            value={fileType}
            onChange={(e) => setFileType(e.target.value)}
            className="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            <option value="PDF">PDF</option>
            <option value="Image">Image</option>
            <option value="Text">Text</option>
            <option value="Video">Video</option>
          </select>

          <input
            type="number"
            placeholder="Min Size (MB)"
            value={minSize}
            onChange={(e) => setMinSize(e.target.value)}
            className="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="number"
            placeholder="Max Size (MB)"
            value={maxSize}
            onChange={(e) => setMaxSize(e.target.value)}
            className="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Upload Date Range:</label>
          <div className="flex space-x-4">
            <input
              type="date"
              value={dateRange.from}
              onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
              className="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="date"
              value={dateRange.to}
              onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
              className="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <button
          onClick={applyFilters}
          className="w-full md:w-auto px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Apply Filters
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredFiles.map((file) => (
          <div key={file.id} className="p-4 border border-gray-200 rounded-lg shadow-md bg-white">
            <strong className="text-lg text-gray-800">{file.original_filename}</strong> ({file.file_type})
            <p className="text-sm text-gray-600 break-all">Size: {bytesToMB(file.size)} MB</p>
            <p className="text-sm text-gray-600 break-all">Hash: {file.file_hash}</p>
            <p className="text-sm text-gray-600">References: {file.reference_count}</p>
            <p className="text-sm text-gray-600">Uploaded: {new Date(file.uploaded_at).toLocaleDateString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

// Ensure default export
export default FileList;