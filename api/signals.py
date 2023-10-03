import os
from django.dispatch import receiver
from .models import Images


from django.db.models.signals import pre_delete


@receiver(pre_delete, sender=Images)
def delete_image(sender, instance, **kwargs):
    """
    Deletes the image file associated with an Image instance
    """
    related_thumbnails = instance.thumbnails.all()

    for thumbnail in related_thumbnails:
        if thumbnail.image and os.path.isfile(thumbnail.image.path):
            os.remove(thumbnail.image.path)
        thumbnail.delete()

    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)
