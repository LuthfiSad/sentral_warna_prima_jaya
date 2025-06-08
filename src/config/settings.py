import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
PORT = os.getenv("PORT", 8000)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
SUPABASE_URL=os.getenv("SUPABASE_URL")
SUPABASE_KEY=os.getenv("SUPABASE_KEY")
BUCKET_FACES=os.getenv("BUCKET_FACES", "faces")
ADMIN_KEY=os.getenv("ADMIN_KEY")
# Office location coordinates
OFFICE_LATITUDE = float(os.getenv("OFFICE_LATITUDE"))
OFFICE_LONGITUDE = float(os.getenv("OFFICE_LONGITUDE"))
ALLOWED_RADIUS_KM = float(os.getenv("ALLOWED_RADIUS_KM"))
