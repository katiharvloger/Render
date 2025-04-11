from flask import Flask, request
import telegram
import os

TOKEN = os.environ.get("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    message = update.message

    if message:
        chat_id = message.chat_id
        text = message.text

        if text == "/start":
            bot.send_message(
                chat_id=chat_id,
                text="*Welcome to Swiggy Order Assistant!*\n\nReady to order your favorite food?\n\n👉 Tap on the *Order Now* button below to get started.\n\n/help - Need help?\n/language - Switch language\n/menu - View instructions\n/order - Place order\n\nFor any query, contact: [@katiharvloger2](https://t.me/katiharvloger2)",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

        elif text == "/order":
            bot.send_message(
                chat_id=chat_id,
                text="Click below to place your order:",
                reply_markup=telegram.InlineKeyboardMarkup([[
                    telegram.InlineKeyboardButton("Order Now", web_app=telegram.WebAppInfo(url="https://katiharvloger.github.io/Order"))
                ]])
            )

        elif text == "/help":
            bot.send_message(
                chat_id=chat_id,
                text="Need help? Contact @katiharvloger2 or type /menu for instructions."
            )

        elif text == "/menu":
            bot.send_message(
                chat_id=chat_id,
                text="How to use:\n1. Type /order to start\n2. Fill your order info\n3. Confirm & Send"
            )

        elif text == "/language":
            bot.send_message(
                chat_id=chat_id,
                text="Language toggled (functionality coming soon)."
            )

    return "ok"
                                                                                           

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(debug=True)
