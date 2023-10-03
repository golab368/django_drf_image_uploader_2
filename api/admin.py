from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.html import format_html
from .models import Images, UserProfile, User, AccountTier, ImageSize
from .utils import generate_thumbnails_for_user
from django.core.validators import MinValueValidator


class ImagesForm(forms.ModelForm):
    thumbnail_width = forms.IntegerField(
        required=False,
        label="Thumbnail Width (in pixels)",
        validators=[MinValueValidator(1)],
    )
    thumbnail_height = forms.IntegerField(
        required=False,
        label="Thumbnail Height (in pixels)",
        validators=[MinValueValidator(1)],
    )
    expiring_seconds = forms.IntegerField(
        required=False,
        label="Expiration time (in seconds)",
        validators=[MinValueValidator(1)],
        help_text="Enter a positive integer to set up expiration time",
    )

    class Meta:
        model = Images
        fields = (
            "image",
            "created",
            "author",
            # "expiration_time",
        )


class ImagesAdmin(admin.ModelAdmin):
    form = ImagesForm
    list_display = (
        "id",
        "title",
        "get_original_file_link_html",
        "created",
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Pobierz niestandardowe szerokości i wysokości z formularza
        custom_width = form.cleaned_data.get("thumbnail_width")
        custom_height = form.cleaned_data.get("thumbnail_height")

        # Wywołaj funkcję generującą miniaturki, przekazując niestandardowe rozmiary
        generate_thumbnails_for_user(request.user, obj, custom_width, custom_height)

    def get_original_file_link_html(self, obj):
        if obj.original_file_link:
            remaining_time = obj.get_remaining_seconds()
            if remaining_time <= 0:
                return f"Link has expired: {obj.expiration}"
            else:
                return format_html(
                    '<a href="{}?expires={}" target="_blank">View original file (expires in {} seconds)</a>',
                    reverse("api:original_file", args=[obj.id]),
                    remaining_time,
                    remaining_time,
                )
        else:
            return "No original file uploaded."


admin.site.register(Images, ImagesAdmin)
admin.site.register(UserProfile)
admin.site.register(User)
admin.site.register(AccountTier)
admin.site.register(ImageSize)
