import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
DB_PATH = os.getenv("DB_PATH", "data/customer_service.db").strip()

ADMIN_IDS = [
    int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x.strip()
]

BOT_NAME = os.getenv("BOT_NAME", "小糖").strip()
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "客服中心").strip()
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "20"))
REPLY_DELAY_MIN = float(os.getenv("REPLY_DELAY_MIN", "2"))
REPLY_DELAY_MAX = float(os.getenv("REPLY_DELAY_MAX", "7"))
