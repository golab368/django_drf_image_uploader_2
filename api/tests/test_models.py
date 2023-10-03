import os
from django.test import TestCase
from api.models import AccountTier, ImageSize, Thumbnail, User, Images, UserProfile
from .factories import (
    UserFactory,
    ImageSizeFactory200,
    UploadedImageFactory,
    AccountTierFactory,
    UserProfileFactory,
    ThumbnailFactory,
)


class UserAndProfileTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user_profile = UserProfileFactory(user=self.user)

    def test_user_creation(self):
        self.assertIsInstance(self.user, User)
        self.assertTrue(self.user.has_usable_password())

    def test_user_profile_creation(self):
        self.assertIsInstance(self.user_profile, UserProfile)
        self.assertEqual(self.user, self.user_profile.user)


class ImageSizeTest(TestCase):
    def setUp(self):
        self.image_size = ImageSizeFactory200()

    def test_image_size_creation(self):
        self.assertIsInstance(self.image_size, ImageSize)


class AccountTierTest(TestCase):
    def setUp(self):
        self.account_tier = AccountTierFactory()

    def test_account_tier_creation(self):
        self.assertIsInstance(self.account_tier, AccountTier)


class ThumbnailTest(TestCase):
    def setUp(self):
        self.thumbnail = ThumbnailFactory()

    def test_thumbnail_creation(self):
        self.assertIsInstance(self.thumbnail, Thumbnail)


class ImagesTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.image_obj = UploadedImageFactory()

    def test_image_creation(self):
        image = Images.objects.create(image=self.image_obj, author=self.user)
        self.assertIsInstance(image, Images)

    def test_image_expiration(self):
        image = Images.objects.create(image=self.image_obj, author=self.user)
        self.assertIsNotNone(image.expiring_seconds)

    def test_image_deletion(self):
        image = Images.objects.create(image=self.image_obj, author=self.user)
        image_id = image.id

        image.delete()

        with self.assertRaises(Images.DoesNotExist):
            Images.objects.get(id=image_id)

    def tearDown(self):
        for image in Images.objects.all():
            if image.image and os.path.isfile(image.image.path):
                os.remove(image.image.path)
