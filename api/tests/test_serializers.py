from django.test import TestCase, RequestFactory
from api.models import Images
from api.serializers import ImagesSerializer
from .factories import (
    UserFactory,
    ImageSizeFactory200,
    ImageSizeFactory400,
    AccountTierFactory,
    UserProfileFactory,
    UploadedImageFactory,
)
import time
import os
from unittest import mock


class ImagesSerializerTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

        self.image_size_200 = ImageSizeFactory200()
        self.image_size_400 = ImageSizeFactory400()
        self.user_account_tier = AccountTierFactory(
            name="Enterprise", permission_to_custom_size=True
        )
        self.user_account_tier.available_sizes.add(
            self.image_size_200, self.image_size_400
        )
        self.image = Images.objects.create(
            title="Test Image", author=self.user, image=UploadedImageFactory()
        )
        self.user_profile = UserProfileFactory(
            user=self.user, account_type=self.user_account_tier
        )

        self.factory = RequestFactory()

    def test_serializer_superuser_with_customs(self):
        request = self.factory.get("/")
        request.user = self.user

        serializer = ImagesSerializer(context={"request": request})

        self.assertIn("custom_width", serializer.fields)

    def test_create_image(self):
        request = self.factory.get("/")
        request.user = self.user

        data = {
            "author": self.user.id,
            "image": UploadedImageFactory(),
            "custom_width": 500,
            "custom_height": 500,
        }

        serializer = ImagesSerializer(data=data, context={"request": request})

        self.assertTrue(serializer.is_valid())
        obj = serializer.save()
        self.assertIsInstance(obj, Images)

    def test_check_if_link_will_expire(self):
        request = self.factory.get("/")
        request.user = self.user
        serializer = ImagesSerializer(instance=self.image, context={"request": request})
        representation = serializer.to_representation(self.image)

        self.assertNotIn(
            "http://127.0.0.1:8000/media/expired.png", representation["image"]
        )

        self.image.expiring_seconds = 1
        self.image.save()

        time.sleep(2)

        representation = serializer.to_representation(self.image)
        self.assertEqual(
            representation["image"], "http://127.0.0.1:8000/media/expired.png"
        )

    def test_thumbnail_generation_called(self):
        with mock.patch("api.serializers.generate_thumbnails_for_user") as mock_method:
            request = self.factory.get("/")
            request.user = self.user
            data = {
                "author": self.user.id,
                "image": UploadedImageFactory(),
                "custom_width": 300,
                "custom_height": 300,
            }
            serializer = ImagesSerializer(data=data, context={"request": request})
            self.assertTrue(serializer.is_valid())
            serializer.save()
            mock_method.assert_called()

    def tearDown(self):
        for image in Images.objects.all():
            if image.image and os.path.isfile(image.image.path):
                os.remove(image.image.path)
