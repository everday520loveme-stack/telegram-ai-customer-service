import asyncio
import random
import re

from config import REPLY_DELAY_MIN, REPLY_DELAY_MAX

HANDOFF_KEYWORDS = [
    "人工", "真人", "客服", "主管", "投诉", "申诉", "退款", "退费",
    "报警", "被骗", "诈骗", "不处理", "生气", "不满意"
]

def is_admin(user_id, admin_ids):
    return int(user_id) in admin_ids

def should_handoff(text):
    return any(k in text for k in HANDOFF_KEYWORDS)

async def human_delay(text):
    length = len(text or "")
    min_delay = REPLY_DELAY_MIN
    max_delay = REPLY_DELAY_MAX
    if length > 80:
        min_delay += 3
        max_delay += 6
    elif length > 30:
        min_delay += 1
        max_delay += 3
    await asyncio.sleep(random.uniform(min_delay, max_delay))

def clean_reply(text):
    text = text.strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:3500]
