"""
Base test class for handling media files in tests.
"""
from django.test import TestCase
from django.conf import settings
import os
import tempfile
import shutil
from PIL import Image

class MediaTestCase(TestCase):
    """Base test case for handling media files."""
    
    # Default test image names
    test_images = [
        'test_image_1.jpg',
        'test_image_2.jpg',
        'test_image_3.jpg'
    ]
    
    @classmethod
    def setUpClass(cls):
        """Set up test media environment."""
        super().setUpClass()
        # Create a temp directory for media files during tests
        cls.temp_dir = tempfile.mkdtemp()
        settings.MEDIA_ROOT = cls.temp_dir
        
        # Create the media directories
        cls.create_media_directories()
        
        # Create test images
        cls.create_test_images()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test media environment."""
        super().tearDownClass()
        # Remove the temp directory and all its contents
        shutil.rmtree(cls.temp_dir)
    
    @classmethod
    def create_media_directories(cls):
        """Create necessary media directories."""
        media_dirs = [
            'question_images',
            'user_uploads',
            'temp'
        ]
        for directory in media_dirs:
            os.makedirs(os.path.join(cls.temp_dir, directory), exist_ok=True)
    
    @classmethod
    def create_test_images(cls):
        """Create test images for use in tests."""
        for image_name in cls.test_images:
            image_path = os.path.join(cls.temp_dir, 'question_images', image_name)
            # Create a small test image
            image = Image.new('RGB', (100, 100), 'white')
            draw = Image.ImageDraw.Draw(image)
            draw.text((10, 40), image_name.replace('.jpg', ''), fill='black')
            image.save(image_path)
    
    def get_image_path(self, image_name):
        """Get the full path to a test image."""
        return os.path.join('question_images', image_name)
