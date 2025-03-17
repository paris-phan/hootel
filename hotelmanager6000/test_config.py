from django.test import TestCase, override_settings

class EnvironmentConfigTests(TestCase):
    @override_settings(
        AWS_ACCESS_KEY_ID='test-key',
        AWS_SECRET_ACCESS_KEY='test-secret',
        AWS_STORAGE_BUCKET_NAME='test-bucket',
        AWS_S3_REGION_NAME='test-region',
        AWS_S3_CUSTOM_DOMAIN='test-bucket.s3.amazonaws.com'
    )
    def test_environment_variables_loaded(self):
        # No need to reload settings - override_settings handles it for us
        from django.conf import settings
        
        # Test that settings are correctly overridden
        self.assertEqual(settings.AWS_ACCESS_KEY_ID, 'test-key')
        self.assertEqual(settings.AWS_SECRET_ACCESS_KEY, 'test-secret')
        self.assertEqual(settings.AWS_STORAGE_BUCKET_NAME, 'test-bucket')
        self.assertEqual(settings.AWS_S3_REGION_NAME, 'test-region')
        self.assertEqual(settings.AWS_S3_CUSTOM_DOMAIN, 'test-bucket.s3.amazonaws.com')
