from .aws_s3 import get_s3_client, generate_signed_url
from fastapi import HTTPException, status
import os
from .procedures import generate_random_string
from PIL import Image
import io
import aiobotocore


async def upload_file_s3(file):
    try:
        ext = file.filename.split('.')[-1]
        new_filename = '{}.{}'.format(generate_random_string(), ext)
        filepath = '{}/{}'.format('01agent_clients', new_filename)

        async with aiobotocore.session.get_session().create_client('s3', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')) as s3_client:
            await s3_client.put_object(
                Bucket=os.getenv('AWS_BUCKET'),
                Key=filepath,
                Body=await file.read()
            )

        return filepath
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload file to S3: {e}")


async def upload_screenshot_s3_bytesio(buffer: io.BytesIO, extension="png"):
    try:
        new_filename = f"{generate_random_string()}.{extension}"
        filepath = f"01agent_screenshots/{new_filename}"

        async with aiobotocore.session.get_session().create_client('s3', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')) as s3_client:
            await s3_client.put_object(
                Bucket=os.getenv('AWS_BUCKET'),
                Key=filepath,
                Body=buffer.getvalue()
            )

        return filepath
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {e}")


def generate_thumbnail(image_data, size):
    """
        Generate a thumbnail of the given size.

        :param image_data: Binary image data.
        :param size: Tuple (width, height) for the thumbnail.
        :return: BytesIO object containing the resized image.
        """
    image = Image.open(io.BytesIO(image_data))
    image.thumbnail(size)  # Resize the image while maintaining aspect ratio

    # Save thumbnail to a BytesIO object
    thumb_io = io.BytesIO()
    image.save(thumb_io, format=image.format)
    thumb_io.seek(0)
    return thumb_io


async def upload_image_s3(image):
    image_data = await image.read()
    thumb_sm = generate_thumbnail(image_data, (200, 200))
    thumb_lg = generate_thumbnail(image_data, (700, 700))

    ext = image.filename.split('.')[-1]
    random_string = generate_random_string()

    new_filename = '{}.{}'.format(random_string, ext)
    thumb_sm_name = '{}.thumb_sm.{}'.format(random_string, ext)
    thumb_lg_name = '{}.thumb_lg.{}'.format(random_string, ext)

    filepath = '{}/{}'.format('01agent_clients', new_filename)
    thumb_sm_path = '{}/{}'.format('01agent_clients', thumb_sm_name)
    thumb_lg_path = '{}/{}'.format('01agent_clients', thumb_lg_name)

    async with aiobotocore.session.get_session().create_client('s3', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')) as s3_client:
        await s3_client.put_object(
            Bucket=os.getenv('AWS_BUCKET'),
            Key=filepath,
            Body=image_data
        )

        await s3_client.put_object(
            Bucket=os.getenv('AWS_BUCKET'),
            Key=thumb_sm_path,
            Body=thumb_sm.getvalue()
        )

        await s3_client.put_object(
            Bucket=os.getenv('AWS_BUCKET'),
            Key=thumb_lg_path,
            Body=thumb_lg.getvalue()
        )

    return filepath


async def get_file_url(filepath):
    return await generate_signed_url(filepath, 3600 * 3)


async def construct_image_obj(image):
    ext = image.split('.')[-1]
    name = image.split('.')[0]

    image_path = '{}.{}'.format(name, ext)
    thumb_sm_path = '{}.thumb_sm.{}'.format(name, ext)
    thumb_lg_path = '{}.thumb_lg.{}'.format(name, ext)

    return {
        'original': await get_file_url(image_path),
        'thumb_sm': await get_file_url(thumb_sm_path),
        'thumb_lg': await get_file_url(thumb_lg_path)
    }
