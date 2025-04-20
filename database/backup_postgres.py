import os
import subprocess
from datetime import datetime
from config import BACKUP_DIR, DB_NAME, DB_USER, DB_PORT,DB_HOST, DB_PASSWORD



def backup_postgres():
    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{DB_NAME}_backup_{timestamp}.sql"
    filepath = os.path.join(BACKUP_DIR, filename)

    command = [
        "pg_dump",
        f"--dbname=postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        "-f", filepath
    ]

    try:
        subprocess.run(command, check=True)
        print(f"✅ Backup успешно сохранён: {filepath}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при создании бэкапа: {e}")

if __name__ == "__main__":
    backup_postgres()
