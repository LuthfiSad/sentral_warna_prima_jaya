FROM python:3.12.4

# Install OS-level dependencies (dlib needs full compiler + math libs)
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

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]