import logging
import os
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

@app.route('/')
def index():
    return "Emotional Saathi is alive and listening 🌼"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi, I'm Emotional Saathi 🌻\n\nI'm here for you — to listen, comfort, and support you emotionally. Whenever you're ready, just share your thoughts. You can also type /help for more options."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💛 How I can support you:\n"
        "- Type how you feel or what's on your mind.\n"
        "- I’ll respond with empathy and gentle suggestions.\n\n"
        "Commands:\n"
        "/start - Introduction\n"
        "/help - Show this menu\n"
        "/clear - Clear memory and start fresh"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text("✨ Memory cleared. You can start fresh anytime.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_history = context.user_data.get("history", [])

    messages = [{
        "role": "system",
        "content": (
            "You're Emotional Saathi, a deeply empathetic, supportive, and practical emotional support companion. "
            "You always validate the user's emotions, respond with warmth and hope, and never say you can’t help. "
            "You offer gentle, solution-focused suggestions like breathing exercises, journaling prompts, or emotional grounding techniques. "
            "Keep responses short, non-judgmental, and culturally sensitive to India."
        )
    }]
    messages += chat_history
    messages.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=250,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content'].strip()

        await update.message.reply_text(reply)

        # Save conversation history
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": reply})
        context.user_data['history'] = chat_history[-10:]

    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        fallback_reply = (
            "I'm here for you 💛\nEven when things feel overwhelming, just know you're not alone. "
            "Try taking 3 deep breaths right now, or journaling one small thing you’re grateful for. "
            "You're stronger than you think, and I believe in you."
        )
        await update.message.reply_text(fallback_reply)

def run_bot():
    app_builder = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app_builder.add_handler(CommandHandler("start", start))
    app_builder.add_handler(CommandHandler("help", help_command))
    app_builder.add_handler(CommandHandler("clear", clear))
    app_builder.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app_builder.run_polling()

if __name__ == '__main__':
    run_bot()
