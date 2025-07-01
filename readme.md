# Face Recognition API

Face Recognition API adalah aplikasi berbasis FastAPI yang menyediakan fitur pendaftaran dan verifikasi wajah menggunakan JWT authentication.

## Teknologi yang Digunakan

Aplikasi ini dibangun menggunakan:
- **FastAPI** - Framework web modern berbasis Python.
- **Pydantic** - Validasi data.
- **SQLAlchemy** - ORM untuk database.
- **JWT (JSON Web Token)** - Autentikasi dan otorisasi.
- **Alembic** - Migrasi database.
- **Uvicorn** - Server ASGI untuk menjalankan aplikasi.
- **MapboxGL** - Untuk tampilan peta jika diperlukan.
- **Material Tailwind React** - Untuk tampilan UI jika digunakan dalam frontend.

## Instalasi dan Menjalankan Aplikasi

### 1. Clone Repository
```sh
git clone https://github.com/{username}/face-id-detector-python.git
cd face-id-detector-python
```

### 2. Buat Virtual Environment
```sh
python -m venv env
source env/bin/activate  # MacOS/Linux
env\Scripts\activate  # Windows
```

### 3. Instalasi Dependencies
```sh
pip install -r requirements.txt
```

### 4. Konfigurasi Database
Sesuaikan konfigurasi database di `src/config/settings.py`.

### 5. Jalankan Migrasi Database
```sh
alembic upgrade head
```

### 6. Menjalankan Server
```sh
python -m src.main
```
atau
```sh
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

## Endpoint API

### 1. Autentikasi
- **POST /auth/login** → Login untuk mendapatkan token JWT.
- **POST /auth/register** → Registrasi pengguna baru.

### 2. Face Recognition
- **POST /face/register** → Mendaftarkan wajah pengguna dengan JWT authentication.
- **POST /face/verify** → Verifikasi wajah pengguna dengan JWT authentication.

### 3. Restricted Access
- **POST /restricted** → Endpoint yang hanya dapat diakses oleh user dengan username.

## Struktur Direktori
```
/face-id-detector-python
 ├── src/
 │   ├── config/             # Konfigurasi database & environment
 │   ├── routes/             # Routing layer
 │   ├── controllers/        # Controller layer
 │   ├── services/           # Business logic layer
 │   ├── models/             # Data models (Schemas & ORM)
 │   ├── schemas/            # Request & Response Schemas
 │   ├── middlewares/        # Middleware (Auth, Logging, etc.)
 │   ├── utils/              # Helper functions
 │   ├── main.py             # Entry point
 ├── .env                    # Environment variables
 ├── requirements.txt
 ├── alembic/                # Database migrations
 └── ...

```

