from dotenv import load_dotenv
import os


load_dotenv('D:/Developing/sotka_po_rus/utils/.env')

TOKEN = os.getenv("BOT_TOKEN")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

PROVIDER_TOKEN = os.getenv('UKASSA_TOKEN')
ADMIN_IDS = os.getenv("ADMIN_IDS")
ADMIN_IDS = ADMIN_IDS.split(',')
ADMIN_IDS = [ int(admin_id) for admin_id in ADMIN_IDS]
TASKS = [4, 9, 10, 11, 12, 15]


