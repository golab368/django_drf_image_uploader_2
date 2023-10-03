from django.test import TestCase
from django.urls import reverse
from .factories import (
    UserFactory,
    UploadedImageFactory,
)
from api.admin import ImagesForm
from datetime import datetime


class AdminSiteTest(TestCase):
    @classmethod
    def setUp(self):
        self.superuser = UserFactory(
            username="admin", password="adminpassword", make_superuser=True
        )
        self.user = UserFactory(username="user", password="userpassword")

    def test_admin_login(self):
        self.client.login(username="admin", password="adminpassword")

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.superuser.is_authenticated)
        self.assertTrue(self.superuser.is_staff)

    def test_user_cannot_access_admin(self):
        self.client.login(username="user", password="userpassword")

        response = self.client.get(reverse("admin:index"))

        self.assertNotEqual(response.status_code, 200)


class ImagesFormTest(TestCase):
    @classmethod
    def setUp(self):
        self.superuser = UserFactory(
            username="admin", password="adminpassword", make_superuser=True
        )

    def test_valid_form(self):
        image_file = UploadedImageFactory()

        data = {
            "created": datetime.now(),
            "author": self.superuser.id,
            "thumbnail_width": 200,
            "thumbnail_height": 300,
            "expiring_seconds": 4,
        }

        files = {"image": image_file}
        form = ImagesForm(data, files)

        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        image_file = UploadedImageFactory()

        data = {
            "created": datetime.now(),
            "author": self.superuser.id,
            "thumbnail_width": 200,
            "thumbnail_height": -300,
            "expiring_seconds": 4,
        }

        files = {"image": image_file}
        form = ImagesForm(data, files)
        self.assertFalse(form.is_valid())
