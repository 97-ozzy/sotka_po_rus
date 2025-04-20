from dotenv import load_dotenv
import os


load_dotenv('utils/.env')

TOKEN = os.getenv("BOT_TOKEN")


ADMIN_IDS = os.getenv("ADMIN_IDS")
ADMIN_IDS = ADMIN_IDS.split(',')
ADMIN_IDS = [ int(admin_id) for admin_id in ADMIN_IDS]

