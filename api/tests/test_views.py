import os
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from api.models import Images
from django.contrib.auth import get_user_model
from .factories import (
    UserFactory,
    UploadedImageFactory,
    UserProfileFactory,
    ImageSizeFactory200,
    ImageSizeFactory400,
    AccountTierFactory,
)


User = get_user_model()


class AuthViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()

    def test_login_view(self):
        url = reverse("api:login")
        data = {
            "username": self.user.username,
            "password": "password",  # Jeśli używasz innej nazwy dla hasła w factory, dostosuj tutaj.
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_view(self):
        url = reverse("api:logout")
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse("api:login"))


class ImagesViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.image_size_200 = ImageSizeFactory200()
        self.image_size_400 = ImageSizeFactory400()
        self.user_account_tier = AccountTierFactory(
            name="Enterprise", permission_to_custom_size=True
        )
        self.user_account_tier.available_sizes.add(
            self.image_size_200, self.image_size_400
        )
        self.user_profile = UserProfileFactory(
            user=self.user, account_type=self.user_account_tier
        )
        self.client.force_authenticate(user=self.user)
        self.image = UploadedImageFactory()

    def test_create_image(self):
        url = reverse("api:create")
        data = {"author": self.user, "image": self.image}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_user_images(self):
        Images.objects.create(author=self.user, image=self.image )

        another_user = UserFactory()
        another_image = UploadedImageFactory()
        Images.objects.create(author=another_user, image=another_image)

        url = reverse("api:user_images_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that only the author user image is returned
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author'], self.user.username)

    def test_get_original_file(self):
        image_instance = Images.objects.create(author=self.user, image=self.image)
        url = reverse("api:original_file", kwargs={"id": image_instance.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def tearDown(self):
        for image in Images.objects.all():
            if image.image and os.path.isfile(image.image.path):
                os.remove(image.image.path)
