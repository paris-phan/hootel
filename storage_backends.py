"""
Custom storage backend for Vercel Blob Storage
"""

import os
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

        # Upload to Vercel Blob
        response = requests.put(
            f"{self.api_url}/upload",
            headers={
                'Authorization': f'Bearer {self.token}',
                'x-content-type': content_type,
            },
            params={
                'pathname': name,
            },
            data=file_data
        )

        if response.status_code != 200:
            raise Exception(f"Failed to upload file to Vercel Blob: {response.text}")

        result = response.json()
        # Return the pathname that Vercel Blob assigned
        return result['pathname']

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
        # List all blobs and check if any match the pathname
        list_response = requests.get(
            f"{self.api_url}/list",
            headers={
                'Authorization': f'Bearer {self.token}',
            }
        )

        if list_response.status_code != 200:
            return False

        blobs = list_response.json()['blobs']

        for blob in blobs:
            if blob['pathname'] == name:
                return True

        return False

    def url(self, name):
        """
        Get public URL for file
        """
        # List all blobs to find the one with matching pathname
        list_response = requests.get(
            f"{self.api_url}/list",
            headers={
                'Authorization': f'Bearer {self.token}',
            }
        )

        if list_response.status_code != 200:
            # Return a placeholder URL if we can't list blobs
            return f"https://blob.vercel-storage.com/{name}"

        blobs = list_response.json()['blobs']

        # Find the blob with matching pathname
        for blob in blobs:
            if blob['pathname'] == name:
                return blob['url']

        # Return a placeholder URL if file not found
        return f"https://blob.vercel-storage.com/{name}"

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
        """
        # Replace spaces with underscores and remove special characters
        import re
        name = re.sub(r'[^\w\s\-\./]', '', name)
        name = name.replace(' ', '_')
        return name