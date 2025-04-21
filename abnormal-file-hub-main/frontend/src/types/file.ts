export interface File {
  id: string;
  original_filename: string;
  file_type: string;
  size: number;
  uploaded_at: string;  // New field for upload date
  file_hash: string;  // Assuming file hash is being used for deduplication
  reference_count: number;  // Tracks the number of references to the file
}
