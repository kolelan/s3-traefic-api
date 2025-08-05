import os
import configparser
import json
from datetime import datetime
from minio import Minio
from minio.error import S3Error
import xxhash


def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def get_file_hash(file_path):
    hasher = xxhash.xxh64()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def upload_to_s3(client, endpoint, secure, bucket, file_path, object_name):
    try:
        client.fput_object(bucket, object_name, file_path)
        protocol = "https" if secure else "http"
        url = f"{protocol}://{endpoint}/{bucket}/{object_name}"
        return url
    except S3Error as e:
        print(f"Error uploading {file_path}: {e}")
        return None


def should_skip_file(file_path, config):
    ext = os.path.splitext(file_path)[1].lower()
    allowed_ext = [x.strip() for x in config['settings']['allowed_extensions'].split(',')]
    if ext not in allowed_ext:
        return True

    exclude_paths = [x.strip() for x in config['settings']['exclude_path_contains'].split(',') if x.strip()]
    if any(exclude in file_path for exclude in exclude_paths):
        return True

    exclude_names = [x.strip() for x in config['settings']['exclude_name_contains'].split(',') if x.strip()]
    filename = os.path.basename(file_path)
    if any(exclude in filename for exclude in exclude_names):
        return True

    return False


def main():
    try:
        config = load_config()

        # Получаем параметры подключения
        endpoint = config['storage']['endpoint']
        secure = config['storage'].get('secure', 'false').lower() == 'true'
        bucket = config['storage']['bucket']

        # Инициализация клиента MinIO
        s3_client = Minio(
            endpoint,
            access_key=config['storage']['access_key'],
            secret_key=config['storage']['secret_key'],
            secure=secure
        )

        # Проверка и создание бакета
        if not s3_client.bucket_exists(bucket):
            s3_client.make_bucket(bucket)

        report = []
        scan_dir = config['settings']['scan_dir']

        # Рекурсивный обход файлов
        for root, _, files in os.walk(scan_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if should_skip_file(file_path, config):
                    continue

                object_name = os.path.relpath(file_path, scan_dir).replace('\\', '/')
                file_url = upload_to_s3(
                    s3_client,
                    endpoint,
                    secure,
                    bucket,
                    file_path,
                    object_name
                )

                if file_url:
                    report.append({
                        "file": file_path,
                        "link": file_url,
                        "hash": get_file_hash(file_path),
                        "s3code": object_name,
                        "date": datetime.now().isoformat()
                    })

        # Сохранение отчета
        report_path = config['settings']['report_path']
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

        print(f"Успешно обработано {len(report)} файлов. Отчёт сохранён в {report_path}")

    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")


if __name__ == "__main__":
    main()