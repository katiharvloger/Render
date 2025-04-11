import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from datetime import datetime
import random

# Constants
BOT_TOKEN = "7069586996:AAG5A-LLSWaQrLQ9EqM8_JihaQI3I90bFik"
SELLER_CHAT_ID = 7241783674

# Conversation steps
FOOD_AMOUNT, TAX, DISTANCE, CONFIRM = range(4)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# User data storage
user_orders = {}

# Helper
def generate_order_id():
    return f"ORD{random.randint(1000,9999)}"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Namaste! Welcome to Swiggy Order Assistant.

Aap kya order karna chahenge?
Kripya food amount ₹ me bataye (min ₹199)"
    )
    return FOOD_AMOUNT

# Step 1: Food Amount
async def get_food_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text.strip())
        if amount < 199:
            await update.message.reply_text("Amount ₹199 se kam hai bhai! Thoda aur add karo.")
            return FOOD_AMOUNT
        context.user_data["food_amount"] = amount
        await update.message.reply_text("GST + Platform Fee mila ke tax amount bataye (₹ me):")
        return TAX
    except:
        await update.message.reply_text("Sahi number dalo bhai, sirf ₹ amount.")
        return FOOD_AMOUNT

# Step 2: Tax
async def get_tax(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tax = float(update.message.text.strip())
        context.user_data["tax"] = tax
        await update.message.reply_text("Delivery distance kitna hai (km me)? (max 7 km):")
        return DISTANCE
    except:
        await update.message.reply_text("Sahi tax amount dalo (₹ me).")
        return TAX

# Step 3: Distance
async def get_distance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        dist = float(update.message.text.strip())
        if dist > 7:
            await update.message.reply_text("Sirf 7 km tak hi delivery hai bhai!")
            return DISTANCE
        context.user_data["distance"] = dist

        # Calculate
        amount = context.user_data["food_amount"]
        tax = context.user_data["tax"]
        total = amount + tax
        discount = 0
        extra = 0

        if total >= 299:
            discount = 125
        elif total >= 199:
            discount = 90
            extra = 15

        final = total - discount + extra
        context.user_data.update({
            "discount": discount,
            "extra": extra,
            "final": final,
            "order_id": generate_order_id(),
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })

        await update.message.reply_text(
            f"Calculation ho gaya bhai!

"
            f"Food: ₹{amount}
Tax: ₹{tax}
Discount: ₹{discount}
Extra: ₹{extra}
"
            f"Final Amount: ₹{final}

"
            f"Agar rate thik na lage, to /contact type karo.

Order confirm karna hai? (haan/na)"
        )
        return CONFIRM
    except:
        await update.message.reply_text("Please enter valid distance (km me)")
        return DISTANCE

# Step 4: Confirm Order
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "haan" in text or "yes" in text:
        data = context.user_data
        msg = (
            f"🛒 *New Order Received!*

"
            f"👤 *User:* @{update.effective_user.username or 'N/A'}
"
            f"🆔 *User ID:* {update.effective_user.id}
"
            f"🆔 *Order ID:* {data['order_id']}
"
            f"🕒 *Time:* {data['timestamp']}

"
            f"🍱 *Food:* ₹{data['food_amount']}
"
            f"🧾 *Tax:* ₹{data['tax']}
"
            f"📍 *Distance:* {data['distance']} km
"
            f"💸 *Discount:* ₹{data['discount']}
"
            f"➕ *Extra:* ₹{data['extra']}
"
            f"✅ *Final Total:* ₹{data['final']}

"
            f"⚠️ Screenshot & Address not collected yet!"
        )
        await context.bot.send_message(chat_id=SELLER_CHAT_ID, text=msg, parse_mode="Markdown")
        await update.message.reply_text("Order confirm ho gaya bhai! Screenshot aur address alag se bhej dena seller ko.")
    else:
        await update.message.reply_text("Order cancel kar diya gaya. Agar kuch aur poochhna hai to /contact karo.")
    return ConversationHandler.END

# Contact seller
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Seller se baat karne ke liye yeh link use karo:
👉 https://t.me/katiharvloger2")

# Cancel fallback
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Order process cancel kar diya gaya.")
    return ConversationHandler.END

# Main
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FOOD_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_food_amount)],
            TAX: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tax)],
            DISTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_distance)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("contact", contact))

    app.run_polling()

if __name__ == "__main__":
    main()
