import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from api.tasks import generate_thumbnail
from api.models import Thumbnail, Images
from .factories import UploadedImageFactory, UserFactory


class GenerateThumbnailTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.image_instance = Images.objects.create(
            title="Test Image", author=self.user, image=UploadedImageFactory()
        )

    def test_generate_thumbnail_with_valid_dimensions(self):
        generate_thumbnail(self.image_instance.id, width=200, height=200)
        thumbnail = Thumbnail.objects.last()
        self.assertEqual(thumbnail.size.width, 200)
        self.assertEqual(thumbnail.size.height, 200)

    def test_generate_thumbnail_with_custom_dimensions(self):
        generate_thumbnail(self.image_instance.id, custom_width=123, custom_height=456)
        thumbnail = Thumbnail.objects.last()
        self.assertEqual(thumbnail.size.width, 123)
        self.assertEqual(thumbnail.size.height, 456)

    @patch("api.tasks.logger")
    def test_generate_thumbnail_without_dimensions(self, mock_logger):
        generate_thumbnail(self.image_instance.id)
        mock_logger.error.assert_called_with(
            "Missing width/height or custom_width/custom_height."
        )

    @patch("api.tasks.logger")
    def test_generate_thumbnail_with_invalid_path(self, mock_logger):
        self.image_instance.image.name = "invalid/path/to/image.jpg"
        self.image_instance.save()
        generate_thumbnail(self.image_instance.id, width=200, height=200)
        mock_logger.error.assert_called_with(
            f"File {self.image_instance.image.path} does not exist"
        )

    def test_generate_thumbnail_with_existing_thumbnail(self):
        generate_thumbnail(self.image_instance.id, width=200, height=200)
        generate_thumbnail(self.image_instance.id, width=200, height=200)
        self.assertEqual(self.image_instance.thumbnails.count(), 2)

