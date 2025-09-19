"""
Custom storage backend for Vercel Blob Storage
"""

import os
import time
import re
import requests
import mimetypes
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.conf import settings
from urllib.parse import urlparse


@deconstructible
class VercelBlobStorage(Storage):
    """
    Custom storage backend for Vercel Blob
    Documentation: https://vercel.com/docs/storage/vercel-blob
    """

    def __init__(self):
        self.token = os.getenv('VERCEL_BLOB_READ_WRITE_TOKEN')
        self.api_url = 'https://blob.vercel-storage.com'
        self._blob_cache = {}  # Cache for blob URL mappings
        self._cache_timestamp = 0
        self._cache_duration = 300  # Cache for 5 minutes

        if not self.token:
            raise ValueError("VERCEL_BLOB_READ_WRITE_TOKEN is not set in environment variables")

    def _save(self, name, content):
        """
        Save file to Vercel Blob
        """
        # Read file content
        file_data = content.read()

        # Determine content type
        content_type, _ = mimetypes.guess_type(name)
        if not content_type:
            content_type = 'application/octet-stream'

        # Clean the name to be URL-safe but preserve path structure
        clean_name = self.get_valid_name(name)

        # Upload to Vercel Blob with PUT request
        # Using the PUT endpoint with pathname in URL to preserve the file path
        response = requests.put(
            f"{self.api_url}/{clean_name}",
            headers={
                'Authorization': f'Bearer {self.token}',
                'x-content-type': content_type,
                'x-add-random-suffix': 'false',  # Prevent random suffix
            },
            data=file_data
        )

        if response.status_code != 200:
            raise Exception(f"Failed to upload file to Vercel Blob: {response.text}")

        result = response.json()
        # Store the actual URL for later retrieval
        # The pathname should match what we sent
        return clean_name

    def _open(self, name, mode='rb'):
        """
        Open file from Vercel Blob
        """
        if 'w' in mode:
            raise ValueError("Writing to existing file not supported. Use save() instead.")

        # Get file URL
        url = self.url(name)

        # Download file content
        response = requests.get(url)
        if response.status_code != 200:
            raise FileNotFoundError(f"File not found: {name}")

        return ContentFile(response.content, name=name)

    def delete(self, name):
        """
        Delete file from Vercel Blob
        """
        # List all blobs to find the one with matching pathname
        list_response = requests.get(
            f"{self.api_url}/list",
            headers={
                'Authorization': f'Bearer {self.token}',
            }
        )

        if list_response.status_code != 200:
            raise Exception(f"Failed to list blobs: {list_response.text}")

        blobs = list_response.json()['blobs']

        # Find the blob with matching pathname
        blob_to_delete = None
        for blob in blobs:
            if blob['pathname'] == name:
                blob_to_delete = blob
                break

        if not blob_to_delete:
            # File doesn't exist, nothing to delete
            return

        # Delete the blob using its URL
        delete_response = requests.delete(
            f"{self.api_url}/delete",
            headers={
                'Authorization': f'Bearer {self.token}',
            },
            json={
                'urls': [blob_to_delete['url']]
            }
        )

        if delete_response.status_code != 200:
            raise Exception(f"Failed to delete file from Vercel Blob: {delete_response.text}")

    def exists(self, name):
        """
        Check if file exists in Vercel Blob
        """
        # Clean the name the same way we do when saving
        clean_name = self.get_valid_name(name)

        # Refresh cache to get latest blob list
        self._refresh_cache()

        # Check if either the original name or clean name exists in cache
        return clean_name in self._blob_cache or name in self._blob_cache

    def _refresh_cache(self):
        """
        Refresh the blob cache if needed
        """
        import time
        current_time = time.time()
        if current_time - self._cache_timestamp > self._cache_duration:
            list_response = requests.get(
                f"{self.api_url}/list",
                headers={
                    'Authorization': f'Bearer {self.token}',
                },
                params={
                    'limit': 5000,  # Get more blobs in one request
                }
            )

            if list_response.status_code == 200:
                self._blob_cache = {}
                blobs = list_response.json().get('blobs', [])
                for blob in blobs:
                    # Map both pathname and clean name to URL
                    pathname = blob.get('pathname', '')
                    url = blob.get('url', '')
                    if pathname and url:
                        self._blob_cache[pathname] = url
                        # Also store with cleaned name
                        clean_name = self.get_valid_name(pathname)
                        self._blob_cache[clean_name] = url
                self._cache_timestamp = current_time

    def url(self, name):
        """
        Get public URL for file
        """
        # Clean the name the same way we do when saving
        clean_name = self.get_valid_name(name)

        # Check cache first
        self._refresh_cache()

        # Try to find in cache
        if clean_name in self._blob_cache:
            return self._blob_cache[clean_name]
        if name in self._blob_cache:
            return self._blob_cache[name]

        # If not in cache, construct the URL directly
        # Vercel Blob URLs are predictable when we know the pathname
        return f"{self.api_url}/{clean_name}"

    def size(self, name):
        """
        Get file size
        """
        # List all blobs to find the one with matching pathname
        list_response = requests.get(
            f"{self.api_url}/list",
            headers={
                'Authorization': f'Bearer {self.token}',
            }
        )

        if list_response.status_code != 200:
            raise Exception(f"Failed to get file size: {list_response.text}")

        blobs = list_response.json()['blobs']

        # Find the blob with matching pathname
        for blob in blobs:
            if blob['pathname'] == name:
                return blob['size']

        raise FileNotFoundError(f"File not found: {name}")

    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that's free on the target storage system.
        """
        # Vercel Blob handles naming conflicts, so we can return the name as-is
        return name

    def get_valid_name(self, name):
        """
        Returns a filename suitable for use with Vercel Blob
        Preserves directory structure for static files
        """
        import re
        # Keep forward slashes for path structure, replace backslashes
        name = name.replace('\\', '/')
        # Remove any dangerous path elements
        name = name.replace('..', '')
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        # Keep alphanumeric, dash, underscore, dot, and forward slash
        name = re.sub(r'[^\w\-\./]', '_', name)
        # Remove leading slashes to prevent absolute paths
        name = name.lstrip('/')
        return name