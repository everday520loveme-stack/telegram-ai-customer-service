Telegram AI 私聊客服机器人 V1

Railway 环境变量：

BOT_TOKEN=你的 BotFather Token
OPENAI_API_KEY=你的 OpenAI API Key
ADMIN_IDS=你的 Telegram 数字 ID
OPENAI_MODEL=gpt-4o-mini
DB_PATH=data/customer_service.db
BOT_NAME=小糖
BUSINESS_NAME=客服中心
REPLY_DELAY_MIN=2
REPLY_DELAY_MAX=7
MAX_HISTORY=20

指令：

/start
/help
/reset

管理员：
/pause 用户ID
/resume 用户ID
/status 用户ID

修改 knowledge.txt 可以增加客服知识库。

不要把 BOT_TOKEN 和 OPENAI_API_KEY 上传到 GitHub。
只能放在 Railway Variables。
