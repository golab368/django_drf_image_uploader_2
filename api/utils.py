from .tasks import generate_thumbnail


def generate_thumbnails_for_user(user, image, custom_width=None, custom_height=None):
    """
    Generates thumbnails for a given user and image.
    """
    available_sizes = user.userprofile.available_sizes.all()
    for size in available_sizes:
        generate_thumbnail.apply_async(args=[image.id, size.width, size.height])

    if user.userprofile.account_type.permission_to_custom_size or user.is_superuser:
        generate_thumbnail.apply_async(
            args=[image.id],
            kwargs={"custom_width": custom_width, "custom_height": custom_height},
        )
