FROM python:3.10-slim

# Install OS-level build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3-dev \
    libboost-all-dev \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    && cmake --version \
    && rm -rf /var/lib/apt/lists/*

# Buat folder kerja
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Jalankan app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
