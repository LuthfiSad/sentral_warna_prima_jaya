import io
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
        print(image_type)

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
