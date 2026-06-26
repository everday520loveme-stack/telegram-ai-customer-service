from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL
from prompts import system_prompt

client = OpenAI(api_key=OPENAI_API_KEY)

def build_input(history, user_message):
    items = [{"role": "system", "content": system_prompt()}]
    for role, content in history:
        if role in ("user", "assistant"):
            items.append({"role": role, "content": content})
    items.append({"role": "user", "content": user_message})
    return items

def generate_reply(history, user_message):
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=build_input(history, user_message),
        temperature=0.7,
        max_output_tokens=450,
    )

    if getattr(response, "output_text", None):
        return response.output_text.strip()

    try:
        return response.output[0].content[0].text.strip()
    except Exception:
        return "不好意思，我这边刚刚有点卡，我帮您重新确认一下。"
