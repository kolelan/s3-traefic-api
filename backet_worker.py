from minio import Minio
from minio.error import S3Error
import urllib3
import json

# Настройки подключения к MinIO
MINIO_ENDPOINT = "localhost:9000"  # или ваш адрес MinIO
MINIO_ACCESS_KEY = "admin"  # замените на ваш ключ
MINIO_SECRET_KEY = "password123"  # замените на ваш секретный ключ
MINIO_SECURE = False  # True, если используется HTTPS

# Название бакета public-bucket
BUCKET_NAME = "files"

# Включаем дебаг-логирование HTTP-запросов
http_client = urllib3.PoolManager(
    timeout=urllib3.Timeout.DEFAULT_TIMEOUT,
    cert_reqs="CERT_NONE",
    retries=urllib3.Retry(
        total=5,
        backoff_factor=0.2,
        status_forcelist=[500, 502, 503, 504]
    )
)

def debug_http_request(method, url, headers, body):
    print("\n--- HTTP REQUEST ---")
    print(f"Method: {method}")
    print(f"URL: {url}")
    print("Headers:")
    for k, v in headers.items():
        print(f"  {k}: {v}")
    if body:
        print("Body:")
        print(body.decode('utf-8') if isinstance(body, bytes) else body)

def debug_http_response(response):
    print("\n--- HTTP RESPONSE ---")
    print(f"Status: {response.status}")
    print("Headers:")
    for k, v in response.headers.items():
        print(f"  {k}: {v}")
    if response.data:
        print("Body:")
        print(response.data.decode('utf-8'))

# Перехватываем запросы/ответы MinIO
class DebugHTTPClient(urllib3.PoolManager):
    def request(self, method, url, fields=None, headers=None, **urlopen_kwargs):
        debug_http_request(method, url, headers or {}, urlopen_kwargs.get('body'))
        response = super().request(method, url, fields, headers, **urlopen_kwargs)
        debug_http_response(response)
        return response

def create_public_bucket():
    try:
        # Инициализация клиента MinIO с кастомным HTTP-клиентом
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
            http_client=DebugHTTPClient()  # Перехватываем запросы
        )

        # 1. Проверяем существование бакета (или создаём)
        if not client.bucket_exists(BUCKET_NAME):
            print("\n[1] Создаём бакет...")
            client.make_bucket(BUCKET_NAME)
            print(f"✅ Бакет '{BUCKET_NAME}' создан.")
        else:
            print(f"ℹ️ Бакет '{BUCKET_NAME}' уже существует.")

        # 2. Устанавливаем публичную политику
        print("\n[2] Устанавливаем публичную политику...")
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{BUCKET_NAME}/*"]
                },
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:ListBucket"],
                    "Resource": [f"arn:aws:s3:::{BUCKET_NAME}"]
                }
            ]
        }
        client.set_bucket_policy(BUCKET_NAME, json.dumps(policy))
        print(f"✅ Бакет '{BUCKET_NAME}' теперь публичный (read-only).")

    except S3Error as e:
        print(f"❌ Ошибка MinIO: {e}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    create_public_bucket()