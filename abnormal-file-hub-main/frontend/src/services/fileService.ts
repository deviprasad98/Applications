import axios from 'axios';
import { File as FileType } from '../types/file';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const fileService = {
  async uploadFile(file: File): Promise<FileType> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_URL}/files/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Upload error:', error);
      throw new Error('Failed to upload file');
    }
  },

  async getFiles(): Promise<FileType[]> {
    try {
      const response = await axios.get(`${API_URL}/files/`);
      return response.data;
    } catch (error) {
      console.error('Get files error:', error);
      throw new Error('Failed to fetch files');
    }
  },

  async deleteFile(id: string): Promise<void> {
    try {
      await axios.delete(`${API_URL}/files/${id}/`);
    } catch (error) {
      console.error('Delete error:', error);
      throw new Error('Failed to delete file');
    }
  },

  async downloadFile(fileUrl: string, filename: string): Promise<void> {
    try {
      const response = await axios.get(fileUrl, {
        responseType: 'blob',
      });
      
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
      throw new Error('Failed to download file');
    }
  },

  async getStorageStats(): Promise<{
    total_requested_upload_size_mb: number;
    unique_storage_used_mb: number;
    storage_saved_mb: number;
  }> {
    try {
      const response = await axios.get(`${API_URL}/files/storage-savings/`);
      return response.data;
    } catch (error) {
      console.error('Get storage stats error:', error);
      throw new Error('Failed to fetch storage statistics');
    }
  },
};