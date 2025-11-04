"""Cloud Storage service for file operations"""
import logging
import uuid
from typing import BinaryIO, Optional
from datetime import timedelta, datetime

from fastapi import HTTPException, status, UploadFile

from app.core.dependencies import get_storage_bucket
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for Cloud Storage operations"""
    
    def __init__(self):
        self.bucket = get_storage_bucket()
        self.settings = get_settings()
    
    def validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file type and size
        
        Args:
            file: Uploaded file
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate file type
        allowed_types = self.settings.allowed_file_types.split(',')
        if file.content_type not in allowed_types:
            logger.warning(f"Invalid file type: {file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Only PDF files are allowed."
            )
        
        # Validate file extension
        if not file.filename.lower().endswith('.pdf'):
            logger.warning(f"Invalid file extension: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file extension. Only .pdf files are allowed."
            )
    
    async def upload_pdf(
        self,
        file: UploadFile,
        user_id: str
    ) -> tuple[str, str]:
        """
        Upload PDF file to Cloud Storage
        
        Args:
            file: Uploaded PDF file
            user_id: User ID for folder organization
            
        Returns:
            Tuple of (storage_url, blob_name)
            
        Raises:
            HTTPException: If upload fails
        """
        try:
            # Validate file
            self.validate_file(file)
            
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Validate file size
            if file_size > self.settings.max_file_size_bytes:
                logger.warning(f"File too large: {file_size} bytes")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size exceeds maximum limit of {self.settings.max_file_size_mb}MB"
                )
            
            # Generate unique filename
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            blob_name = f"users/{user_id}/{unique_filename}"
            
            # Upload to Cloud Storage
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(
                file_content,
                content_type=file.content_type
            )
            
            logger.info(f"Uploaded file to Cloud Storage: {blob_name}")
            
            # Return storage URL and blob name
            storage_url = f"gs://{self.bucket.name}/{blob_name}"
            
            return storage_url, blob_name
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file"
            )
    
    def generate_signed_url(self, blob_name: str) -> tuple[str, datetime]:
        """
        Generate signed URL for secure file download
        
        Args:
            blob_name: Blob name in Cloud Storage
            
        Returns:
            Tuple of (signed_url, expiration_datetime)
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            # Check if blob exists
            if not blob.exists():
                logger.warning(f"Blob not found: {blob_name}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Generate signed URL
            expiration = timedelta(hours=self.settings.signed_url_expiration_hours)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET"
            )
            
            expires_at = datetime.utcnow() + expiration
            
            logger.info(f"Generated signed URL for: {blob_name}")
            
            return signed_url, expires_at
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate download URL"
            )
    
    def delete_file(self, blob_name: str) -> None:
        """
        Delete file from Cloud Storage
        
        Args:
            blob_name: Blob name in Cloud Storage
            
        Raises:
            HTTPException: If deletion fails
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            # Check if blob exists
            if not blob.exists():
                logger.warning(f"Blob not found for deletion: {blob_name}")
                return
            
            # Delete blob
            blob.delete()
            logger.info(f"Deleted file from Cloud Storage: {blob_name}")
            
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file"
            )
    
    def download_file(self, blob_name: str) -> bytes:
        """
        Download file content from Cloud Storage
        
        Args:
            blob_name: Blob name in Cloud Storage
            
        Returns:
            File content as bytes
            
        Raises:
            HTTPException: If download fails
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            # Check if blob exists
            if not blob.exists():
                logger.warning(f"Blob not found: {blob_name}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Download file content
            file_content = blob.download_as_bytes()
            logger.info(f"Downloaded file from Cloud Storage: {blob_name}")
            
            return file_content
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to download file"
            )
    
    def get_blob_name_from_url(self, storage_url: str) -> str:
        """
        Extract blob name from storage URL
        
        Args:
            storage_url: Cloud Storage URL (gs://bucket/path)
            
        Returns:
            Blob name (path)
        """
        # Remove gs://bucket/ prefix
        if storage_url.startswith('gs://'):
            parts = storage_url.replace('gs://', '').split('/', 1)
            if len(parts) > 1:
                return parts[1]
        
        return storage_url
