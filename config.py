from dotenv import load_dotenv
import os


load_dotenv('utils/.env')

TOKEN = os.getenv("BOT_TOKEN")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

ADMIN_IDS = os.getenv("ADMIN_IDS")

ADMIN_IDS = ADMIN_IDS.split(',')
ADMIN_IDS = [ int(admin_id) for admin_id in ADMIN_IDS]
TASKS = [4, 9, 10, 11, 12, 15]

PREMIUM_PRICE_RUB = 40
RENEWAL_RETURN_URL = "https://t.me/sotka_po_rus_bot"
SHOP_ID = os.getenv("SHOP_ID")
UKASSA_TOKEN = os.getenv("UKASSA_TOKEN")
PATH_TO_PHOTOS = os.getenv('PATH_TO_PHOTOS')

MONTHLY_REFERRED_NUMBER = 20
DAILY_REFERRED_NUMBER = 2