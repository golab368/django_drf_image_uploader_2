import factory
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from factory.django import DjangoModelFactory
from api.models import User, AccountTier, ImageSize, UserProfile, Thumbnail


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "password")

    @factory.post_generation
    def make_superuser(obj, create, extracted, **kwargs):
        if extracted:
            obj.is_staff = True
            obj.is_superuser = True
            obj.save()


class ImageSizeFactory200(DjangoModelFactory):
    class Meta:
        model = ImageSize

    width = 200
    height = 200


class ImageSizeFactory400(DjangoModelFactory):
    class Meta:
        model = ImageSize

    width = 400
    height = 400


class AccountTierFactory(DjangoModelFactory):
    class Meta:
        model = AccountTier

    name = factory.Sequence(lambda n: f"tier{n}")
    permission_to_custom_size = False


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    account_type = factory.SubFactory(AccountTierFactory)


class UploadedImageFactory(factory.Factory):
    class Meta:
        model = SimpleUploadedFile

    name = factory.LazyAttribute(lambda _: "test_image.jpg")
    content_type = factory.LazyAttribute(lambda _: "image/jpeg")

    @factory.lazy_attribute
    def content(self):
        image_data = BytesIO()
        image = Image.new("RGB", (900, 900))
        image.save(image_data, format="JPEG")
        image_data.seek(0)
        return image_data.getvalue()

    @classmethod
    def _create(cls, *args, **kwargs):
        return SimpleUploadedFile(
            name=kwargs.get("name"),
            content=kwargs.get("content"),
            content_type=kwargs.get("content_type"),
        )


class ThumbnailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Thumbnail

    size = factory.SubFactory(ImageSizeFactory200)
    image = UploadedImageFactory()
