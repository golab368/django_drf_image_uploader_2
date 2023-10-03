from rest_framework import serializers
from .models import UserProfile, Images
from .utils import generate_thumbnails_for_user


class ImagesSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    expiring_seconds = serializers.IntegerField(write_only=True, required=False)
    thumbnails = serializers.SerializerMethodField()
    custom_width = serializers.IntegerField(write_only=True, required=False)
    custom_height = serializers.IntegerField(write_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context["request"].user
        if user.is_authenticated:
            try:
                account_tier = user.userprofile.account_type
                if not account_tier.permission_to_custom_size and not user.is_superuser:
                    self.fields.pop("expiring_seconds", None)
                    self.fields.pop("custom_width", None)
                    self.fields.pop("custom_height", None)
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=user, account_type="None")

    def get_thumbnails(self, obj):
        thumbnails = {}
        for thumbnail in obj.thumbnails.all():
            thumbnails[str(thumbnail.size)] = self.context[
                "request"
            ].build_absolute_uri(thumbnail.image.url)
        return thumbnails

    def create(self, validated_data):
        user = self.context["request"].user

        custom_width = validated_data.pop("custom_width", None)
        custom_height = validated_data.pop("custom_height", None)
        validated_data["author"] = user
        image = Images.objects.create(**validated_data)

        generate_thumbnails_for_user(user, image, custom_width, custom_height)

        return image

    class Meta:
        model = Images
        fields = (
            "title",
            "image",
            "slug",
            "created",
            "author",
            "thumbnails",
            "expiring_seconds",
            "custom_width",
            "custom_height",
        )
        read_only_fields = ("title", "slug", "created")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        remaining_time = instance.get_remaining_seconds()

        if remaining_time <= 0:
            data["image"] = "http://127.0.0.1:8000/media/expired.png"
            data["thumbnails"] = {
                key: "http://127.0.0.1:8000/media/expired.png"
                for key in data["thumbnails"]
            }
        else:
            data["remaining_time"] = remaining_time
            data["expiring_seconds"] = instance.expiring_seconds

        return data
