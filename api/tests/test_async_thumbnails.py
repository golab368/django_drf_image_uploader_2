import os
from django.test import TestCase
from unittest import mock
from api.celery import app
from api.models import Images, UserProfile, AccountTier
from api.utils import generate_thumbnails_for_user
from .factories import (
    UserFactory,
    ImageSizeFactory200,
    ImageSizeFactory400,
    UploadedImageFactory,
)


class ThumbnailsGenerationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._original_celery_always_eager = app.conf.CELERY_ALWAYS_EAGER
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    @classmethod
    def tearDownClass(cls):
        app.conf.CELERY_ALWAYS_EAGER = cls._original_celery_always_eager
        super().tearDownClass()

    def setUp(self):
        self.user = UserFactory()
        self.account_tier = AccountTier.objects.create(
            name="Enterprise", permission_to_custom_size=True
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user, account_type=self.account_tier
        )
        self.image = Images.objects.create(
            title="Test Image", author=self.user, image=UploadedImageFactory()
        )

        self.image_size_200 = ImageSizeFactory200()
        self.image_size_400 = ImageSizeFactory400()
        self.account_tier.available_sizes.add(self.image_size_200, self.image_size_400)

    @mock.patch("api.utils.generate_thumbnail.apply_async")
    def test_generate_thumbnails_for_enterprise_user(self, mock_apply_async):
        generate_thumbnails_for_user(
            self.user, self.image, custom_width=300, custom_height=300
        )

        self.assertEqual(mock_apply_async.call_count, 3)
        mock_apply_async.assert_any_call(args=[self.image.id, 200, 200])
        mock_apply_async.assert_any_call(
            args=[self.image.id],
            kwargs={"custom_width": 300, "custom_height": 300}
        )
