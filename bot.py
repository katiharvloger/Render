from flask import Flask, request
import telegram
import os

TOKEN = os.environ.get("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    if update.message and update.message.text == "/start":
        bot.send_message(chat_id=update.message.chat_id, text="Welcome to Helpbot via Render!")
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(debug=True)
