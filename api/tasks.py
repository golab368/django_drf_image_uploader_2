import logging
import os
import uuid
from io import BytesIO
from PIL import Image
from celery import shared_task
from celery.exceptions import Retry
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile

logger = logging.getLogger(__name__)

FILE_TYPES = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".gif": "GIF",
    ".png": "PNG",
}


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def generate_thumbnail(self, image_id, width=None, height=None, custom_width=None, custom_height=None):
    from .models import ImageSize, Thumbnail, Images

    try:
        image_instance = Images.objects.get(id=image_id)
        file_path = image_instance.image.path

    except Images.DoesNotExist:
        if self.request.retries == self.max_retries:
            logger.error(f"Image with ID {image_id} does not exist after {self.max_retries + 1} attempts.")
            return
        logger.warning(f"Image with ID {image_id} does not yet exist. Retrying...")
        raise self.retry(exc=Images.DoesNotExist(f"Image with ID {image_id} does not exist."), countdown=10)

    try:
        if not os.path.exists(file_path):
            logger.error(f"File {file_path} does not exist")
            return


        with Image.open(file_path) as image:
            thumb_name = uuid.uuid4().hex
            thumb_extension = os.path.splitext(file_path)[1]

            image_copy = image.copy()
            if width and height:
                image_copy.thumbnail((width, height))
                thumb_filename = f"{thumb_name}_thumb_{width}x{height}{thumb_extension}"
            elif custom_width and custom_height:
                image_copy.thumbnail((custom_width, custom_height))
                thumb_filename = f"{thumb_name}_thumb_{custom_width}x{custom_height}{thumb_extension}"
            else:
                logger.error("Missing width/height or custom_width/custom_height.")
                return

            FTYPE = FILE_TYPES.get(thumb_extension)
            if not FTYPE:
                logger.error(f"Unsupported file type for {thumb_filename}")
                return

            temp_thumb_io = BytesIO()
            image_copy.save(temp_thumb_io, format=FTYPE)
            temp_thumb_io.seek(0)
            temp_thumb = SimpleUploadedFile(
                name=thumb_filename,
                content=temp_thumb_io.read(),
                content_type=f"image/{FTYPE.lower()}",
            )

            thumb_data = InMemoryUploadedFile(
                temp_thumb,
                None,
                thumb_filename,
                f"image/{FTYPE.lower()}",
                temp_thumb.tell(),
                None,
            )

            size_data = (
                (width, height) if width and height else (custom_width, custom_height)
            )
            size_obj, _ = ImageSize.objects.get_or_create(
                width=size_data[0], height=size_data[1]
            )

            thumbnail = Thumbnail.objects.create(size=size_obj, image=thumb_data)
            image_instance.thumbnails.add(thumbnail)

    except Exception as e:
            logger.exception(f"Error generating thumbnail for file {file_path}")

