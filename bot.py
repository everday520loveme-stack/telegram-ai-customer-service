from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from ai_client import generate_reply
from config import ADMIN_IDS, BOT_TOKEN, MAX_HISTORY, OPENAI_API_KEY
from database import (
    add_log, add_message, clear_history, get_history, init_db,
    is_paused, set_paused
)
from utils import clean_reply, human_delay, is_admin, should_handoff

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("您好～我在的。\n请直接告诉我您想咨询的问题。")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = "📖 指令\n\n/start 开始咨询\n/reset 清除当前对话记忆\n"
    if is_admin(user_id, ADMIN_IDS):
        text += "\n管理员：\n/pause 用户ID\n/resume 用户ID\n/status 用户ID"
    await update.message.reply_text(text)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_history(update.effective_user.id)
    await update.message.reply_text("已清除对话记忆，可以重新开始。")

async def pause_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, ADMIN_IDS):
        return
    if len(context.args) != 1:
        await update.message.reply_text("格式：/pause 用户ID")
        return
    set_paused(int(context.args[0]), True, "管理员暂停")
    await update.message.reply_text(f"已暂停用户 {context.args[0]} 的自动回复。")

async def resume_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, ADMIN_IDS):
        return
    if len(context.args) != 1:
        await update.message.reply_text("格式：/resume 用户ID")
        return
    set_paused(int(context.args[0]), False, "管理员恢复")
    await update.message.reply_text(f"已恢复用户 {context.args[0]} 的自动回复。")

async def status_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, ADMIN_IDS):
        return
    if len(context.args) != 1:
        await update.message.reply_text("格式：/status 用户ID")
        return
    paused = is_paused(int(context.args[0]))
    await update.message.reply_text(f"用户：{context.args[0]}\n状态：{'人工接管中' if paused else 'AI自动回复中'}")

async def notify_admins(context: ContextTypes.DEFAULT_TYPE, user_id, username, text):
    if not ADMIN_IDS:
        return

    msg = (
        "🔔 需要人工接管\n\n"
        f"用户ID：{user_id}\n"
        f"用户名：{username or '无'}\n\n"
        f"消息：\n{text}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=msg)
        except Exception:
            pass

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    user = update.effective_user
    user_id = user.id
    username = f"@{user.username}" if user.username else user.full_name
    text = update.message.text.strip()

    if is_paused(user_id):
        return

    add_message(user_id, "user", text)
    add_log(user_id, "用户消息", text)

    if should_handoff(text):
        set_paused(user_id, True, "触发人工接管")
        await notify_admins(context, user_id, username, text)
        await human_delay(text)
        reply = "好的，我帮您转接人工客服，请稍等一下。"
        add_message(user_id, "assistant", reply)
        await update.message.reply_text(reply)
        return

    history = get_history(user_id, MAX_HISTORY)

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await human_delay(text)
        reply = clean_reply(generate_reply(history, text))
        add_message(user_id, "assistant", reply)
        add_log(user_id, "AI回复", reply)
        await update.message.reply_text(reply)
    except Exception as e:
        add_log(user_id, "错误", str(e))
        await update.message.reply_text("不好意思，我这边刚刚有点卡，我帮您重新确认一下。")

def main():
    if not BOT_TOKEN:
        print("错误：请设置 BOT_TOKEN")
        return
    if not OPENAI_API_KEY:
        print("错误：请设置 OPENAI_API_KEY")
        return

    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("pause", pause_user))
    app.add_handler(CommandHandler("resume", resume_user))
    app.add_handler(CommandHandler("status", status_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("AI客服机器人已启动...")
    app.run_polling()

if __name__ == "__main__":
    main()
