"""
Custom storage backend for Vercel Blob Storage
"""

import os
import time
import re
import json
import requests
import mimetypes
from io import BytesIO
from pathlib import Path
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
        self._cache_file = Path(settings.BASE_DIR) / '.vercel_blob_cache.json'
        self._path_to_url = {}  # In-memory cache

        if not self.token:
            raise ValueError("VERCEL_BLOB_READ_WRITE_TOKEN is not set in environment variables")

        # Load persistent cache from file
        self._load_cache()

    def _load_cache(self):
        """Load URL mappings from persistent cache file"""
        try:
            if self._cache_file.exists():
                with open(self._cache_file, 'r') as f:
                    self._path_to_url = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load Vercel Blob cache: {e}")
            self._path_to_url = {}

    def _save_cache(self):
        """Save URL mappings to persistent cache file"""
        try:
            with open(self._cache_file, 'w') as f:
                json.dump(self._path_to_url, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save Vercel Blob cache: {e}")

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

        # Upload to Vercel Blob using the PUT endpoint with pathname
        # The PUT endpoint format preserves the pathname
        response = requests.put(
            f"{self.api_url}/{clean_name}",
            headers={
                'Authorization': f'Bearer {self.token}',
                'content-type': content_type,  # Use content-type not x-content-type
            },
            data=file_data
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to upload file to Vercel Blob: {response.text}")

        result = response.json()

        # Store the actual URL returned by Vercel
        actual_url = result.get('url', '')
        pathname = result.get('pathname', clean_name)

        if actual_url:
            # Store mapping from both the original name and clean name to the URL
            self._path_to_url[clean_name] = actual_url
            self._path_to_url[name] = actual_url

            # Save the cache to disk for persistence
            self._save_cache()

        # Return the pathname that Vercel stored it as
        return pathname if pathname else clean_name

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
        clean_name = self.get_valid_name(name)

        # Get the URL from our cache
        blob_url = None
        if clean_name in self._path_to_url:
            blob_url = self._path_to_url[clean_name]
        elif name in self._path_to_url:
            blob_url = self._path_to_url[name]

        if not blob_url:
            # File doesn't exist in cache, assume it doesn't exist
            return

        # Delete the blob using its URL
        delete_response = requests.delete(
            f"{self.api_url}/delete",
            headers={
                'Authorization': f'Bearer {self.token}',
            },
            json={
                'urls': [blob_url]
            }
        )

        if delete_response.status_code not in [200, 404]:
            raise Exception(f"Failed to delete file from Vercel Blob: {delete_response.text}")

        # Remove from cache after deletion attempt (even if file was already gone)
        self._path_to_url.pop(name, None)
        self._path_to_url.pop(clean_name, None)
        self._save_cache()

    def exists(self, name):
        """
        Check if file exists in Vercel Blob
        """
        # Clean the name the same way we do when saving
        clean_name = self.get_valid_name(name)

        # Check if either the original name or clean name exists in persistent cache
        return clean_name in self._path_to_url or name in self._path_to_url


    def url(self, name):
        """
        Get public URL for file
        """
        # Clean the name the same way we do when saving
        clean_name = self.get_valid_name(name)

        # Check direct path mapping first
        if clean_name in self._path_to_url:
            return self._path_to_url[clean_name]
        if name in self._path_to_url:
            return self._path_to_url[name]

        # For missing files, return a placeholder URL instead of raising an exception
        # This prevents infinite loops when error pages try to load static files
        print(f"Warning: Static file '{name}' not found in Vercel Blob cache. "
              f"Run 'python manage.py collectstatic' to upload static files.")

        # Return a placeholder URL that won't break the page
        return f"data:text/plain;charset=utf-8,Missing%20file%3A%20{name}"

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