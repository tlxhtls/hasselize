"""
Cloudflare R2 storage service for Hasselize AI Backend.

Handles direct uploads, presigned URLs, and file management.
"""

import logging
import uuid
from datetime import timedelta
from pathlib import Path
from typing import BinaryIO, Optional

import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError

from core.config import settings
from core.security import sanitize_filename

logger = logging.getLogger(__name__)


class R2StorageService:
    """
    Cloudflare R2 storage service using S3-compatible API.

    Features:
    - Direct upload via presigned URLs
    - Server-side upload for small files
    - Automatic key generation with UUID
    - ContentType preservation
    """

    def __init__(self):
        """Initialize R2 client with credentials."""
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint_url,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )
        self.bucket = settings.r2_bucket_name

    def generate_key(
        self,
        prefix: str,
        filename: Optional[str] = None,
        extension: Optional[str] = None,
    ) -> str:
        """
        Generate unique storage key with optional filename.

        Args:
            prefix: Key prefix (e.g., "original", "transformed", "thumbnails")
            filename: Original filename for reference (sanitized)
            extension: File extension (overrides filename extension)

        Returns:
            Storage key path
        """
        # Generate UUID for uniqueness
        unique_id = str(uuid.uuid4())

        # Determine extension
        if extension:
            ext = extension.lstrip(".")
        elif filename:
            ext = Path(filename).suffix.lstrip(".")
        else:
            ext = "jpg"

        # Build key path
        if filename:
            safe_name = sanitize_filename(filename)
            return f"{prefix}/{unique_id}_{safe_name}"
        return f"{prefix}/{unique_id}.{ext}"

    def generate_presigned_url(
        self,
        key: str,
        operation: str = "put_object",
        expiration: int = 3600,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Generate presigned URL for direct upload/download.

        Args:
            key: Storage key
            operation: S3 operation (put_object, get_object)
            expiration: URL expiration in seconds
            content_type: Content-Type for upload

        Returns:
            Presigned URL string

        Raises:
            StorageError: If URL generation fails
        """
        try:
            params = {"Bucket": self.bucket, "Key": key}
            if content_type:
                params["ContentType"] = content_type

            url = self.client.generate_presigned_url(
                ClientMethod=operation,
                Params=params,
                ExpiresIn=expiration,
            )
            return url

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise StorageError(f"Presigned URL generation failed: {e}")

    def upload_file(
        self,
        file_data: bytes | BinaryIO,
        key: str,
        content_type: str = "image/jpeg",
        metadata: Optional[dict[str, str]] = None,
    ) -> str:
        """
        Upload file to R2 (server-side).

        Use for smaller files or when presigned URLs are not suitable.

        Args:
            file_data: File content as bytes or file-like object
            key: Storage key
            content_type: MIME type
            metadata: Optional metadata dictionary

        Returns:
            Public URL of uploaded file

        Raises:
            StorageError: If upload fails
        """
        try:
            extra_args = {"ContentType": content_type}
            if metadata:
                extra_args["Metadata"] = metadata

            self.client.upload_fileobj(
                Fileobj=file_data if hasattr(file_data, "read") else BytesIO(file_data),
                Bucket=self.bucket,
                Key=key,
                ExtraArgs=extra_args,
            )

            url = self.get_public_url(key)
            logger.info(f"Uploaded file to R2: {key}")
            return url

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to upload file: {e}")
            raise StorageError(f"Upload failed: {e}")

    def download_file(self, key: str) -> bytes:
        """
        Download file from R2.

        Args:
            key: Storage key

        Returns:
            File content as bytes

        Raises:
            StorageError: If download fails
        """
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to download file {key}: {e}")
            raise StorageError(f"Download failed: {e}")

    def delete_file(self, key: str) -> bool:
        """
        Delete file from R2.

        Args:
            key: Storage key

        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted file from R2: {key}")
            return True

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to delete file {key}: {e}")
            return False

    def get_public_url(self, key: str) -> str:
        """
        Get public URL for a storage key.

        Args:
            key: Storage key

        Returns:
            Full URL to file
        """
        # R2 public URL format
        return f"{settings.r2_endpoint_url}/{self.bucket}/{key}"

    def file_exists(self, key: str) -> bool:
        """
        Check if file exists in R2.

        Args:
            key: Storage key

        Returns:
            True if file exists
        """
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True

        except ClientError:
            return False


class StorageError(Exception):
    """Storage operation error."""

    pass


# Global storage service instance
storage_service = R2StorageService()
