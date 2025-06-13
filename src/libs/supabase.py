import io
from typing import List
import supabase
from uuid import uuid4
from src.config.settings import SUPABASE_URL, SUPABASE_KEY, BUCKET_FACES
from src.utils.error import AppError
from PIL import Image
from src.utils.message_code import MESSAGE_CODE

supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

async def upload_image_to_supabase(image_data: bytes):
    try:
        image_type = Image.open(io.BytesIO(image_data)).format.lower()

        if image_type not in ["jpeg", "png", "webp", "jpg"]:
            raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Format file tidak didukung!")

        image_name = f"{uuid4().hex}.{image_type}"

        image_bytes = io.BytesIO(image_data).getvalue()

        try:
            supabase_client.storage.from_(BUCKET_FACES).upload(
                path=image_name,
                file=image_bytes,
                file_options={"content-type": f"image/{image_type}"},  # Set Content-Type
            )
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Upload gagal: {str(e)}")

        # 5. Kembalikan URL file
        return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_FACES}/{image_name}"
    except Exception as e:
        raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Upload gagal: {str(e)}")

async def delete_images_from_supabase(image_urls: List[str]):
    """
    Delete multiple images from Supabase storage
    """
    try:
        # Extract file paths from URLs
        file_paths = []
        for url in image_urls:
            # Extract filename from URL
            # URL format: {SUPABASE_URL}/storage/v1/object/public/{BUCKET_FACES}/{filename}
            if BUCKET_FACES in url:
                filename = url.split(f"{BUCKET_FACES}/")[-1]
                file_paths.append(filename)
        
        if file_paths:
            # Delete files from Supabase storage
            supabase_client.storage.from_(BUCKET_FACES).remove(file_paths)
            
    except Exception as e:
        # Log error but don't raise - database deletion already succeeded
        print(f"Warning: Failed to delete some images from storage: {str(e)}")