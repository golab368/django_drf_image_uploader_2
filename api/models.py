import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


def user_directory_path(instance, filename):
    extension = filename.split(".")[-1]
    return "{}.{}".format(uuid.uuid4(), extension)


class User(AbstractUser):
    def save(self, *args, **kwargs):
        if not self.pk:
            self.set_password(self.password)
        super(User, self).save(*args, **kwargs)


class ImageSize(models.Model):
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.width}x{self.height}"


class AccountTier(models.Model):
    name = models.CharField(max_length=50)
    available_sizes = models.ManyToManyField(ImageSize, blank=True)
    permission_to_custom_size = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.ForeignKey(AccountTier, on_delete=models.CASCADE)

    @property
    def available_sizes(self):
        return self.account_type.available_sizes.all()

    def __str__(self):
        return self.user.username


class Thumbnail(models.Model):
    size = models.ForeignKey(ImageSize, on_delete=models.CASCADE)
    image = models.ImageField()

    def __str__(self):
        return f"{self.size} - {self.image.name}"


class Images(models.Model):
    title = models.CharField(max_length=250, null=True, blank=True)
    image = models.ImageField(upload_to=user_directory_path)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    original_file_link = models.URLField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="author")
    expiration = models.BooleanField(default=False)
    thumbnails = models.ManyToManyField(Thumbnail, related_name="thumbnails")

    expiring_seconds = models.PositiveIntegerField(
        default=86400,
        null=True,
        blank=True,
        help_text="Enter a positive integer to set up expiration time",
    )

    def save(self, *args, **kwargs):
        self.title = self.image.name

        if self.image:
            self.original_file_link = self.image.url

        super().save(*args, **kwargs)

    def get_remaining_seconds(self):
        elapsed_time = timezone.now() - self.created
        remaining_time = self.expiring_seconds - elapsed_time.total_seconds()

        if remaining_time <= 0:
            if not self.expiration:
                self.expiration = True
                self.save(update_fields=["expiration"])
            return 0
        return remaining_time
