from django.test import TestCase
from django.conf import settings
from unittest.mock import patch
import os

class EnvironmentConfigTests(TestCase):
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test-key',
        'AWS_SECRET_ACCESS_KEY': 'test-secret',
        'AWS_STORAGE_BUCKET_NAME': 'test-bucket',
        'AWS_S3_REGION_NAME': 'test-region'
    })
    def test_environment_variables_loaded(self):
        # Force reload of settings
        import importlib
        from django.conf import settings
        importlib.reload(settings)
        
        # Test that environment variables are correctly loaded
        self.assertEqual(settings.AWS_ACCESS_KEY_ID, 'test-key')
        self.assertEqual(settings.AWS_SECRET_ACCESS_KEY, 'test-secret')
        self.assertEqual(settings.AWS_STORAGE_BUCKET_NAME, 'test-bucket')
        self.assertEqual(settings.AWS_S3_REGION_NAME, 'test-region')
        self.assertEqual(settings.AWS_S3_CUSTOM_DOMAIN, 'test-bucket.s3.amazonaws.com')
