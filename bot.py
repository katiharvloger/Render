# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)

BOT_TOKEN = "7069586996:AAG5A-LLSWaQrLQ9EqM8_JihaQI3I90bFik"
SELLER_CHAT_ID = "7241783674"

FOOD_AMOUNT, TAX, DISTANCE, CONFIRM = range(4)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kripya food amount ₹ me bataye (min ₹199)")
    return FOOD_AMOUNT

# Get food amount
async def get_food_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        food = int(update.message.text)
        if food < 199:
            await update.message.reply_text("Minimum order ₹199 hona chahiye. Wapas ₹ amount bhejein.")
            return FOOD_AMOUNT
        context.user_data["food_amount"] = food
        await update.message.reply_text("Ab tax amount ₹ me bataye:")
        return TAX
    except:
        await update.message.reply_text("Sirf number bhejein jaise: 250")
        return FOOD_AMOUNT

# Get tax
async def get_tax(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tax = int(update.message.text)
        context.user_data["tax"] = tax
        await update.message.reply_text("Delivery distance kitna km hai? (max 7 km)")
        return DISTANCE
    except:
        await update.message.reply_text("Sirf number bhejein jaise: 15")
        return TAX

# Get distance
async def get_distance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        distance = float(update.message.text)
        if distance > 7:
            await update.message.reply_text("Max delivery distance 7 km allowed hai.")
            return DISTANCE
        context.user_data["distance"] = distance

        food = context.user_data["food_amount"]
        tax = context.user_data["tax"]

        # Discount rules
        discount = 90
        if food >= 199:
            discount = 110
        elif food >= 249:
            discount = 125
        elif food >= 299:
            discount = 0

        context.user_data["discount"] = discount

        # Extra charges
        extra = 0
        if food > 249:
            extra = 15
        context.user_data["extra"] = extra

        # Final amount
        final = food + tax + extra - discount
        context.user_data["final"] = final

        await update.message.reply_text(
            f"""Order Detail:
🍱 Food: ₹{food}
🧾 Tax: ₹{tax}
📍 Distance: {distance} km
💸 Discount: ₹{discount}
➕ Extra: ₹{extra}
✅ Final Total: ₹{final}

Aap order confirm karna chahte ho? (yes/no)"""
        )
        return CONFIRM

    except:
        await update.message.reply_text("Sirf number bhejein jaise: 2.5")
        return DISTANCE

# Confirm order
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = update.message.text.lower()
    if "yes" in reply:
        data = context.user_data
        msg = (
            f"🛒 *New Order Received!*\n\n"
            f"🍱 *Food:* ₹{data['food_amount']}\n"
            f"🧾 *Tax:* ₹{data['tax']}\n"
            f"📍 *Distance:* {data['distance']} km\n"
            f"💸 *Discount:* ₹{data['discount']}\n"
            f"➕ *Extra:* ₹{data['extra']}\n"
            f"✅ *Final Total:* ₹{data['final']}\n\n"
            f"⚠️ Screenshot & Address not collected yet!"
        )
        await context.bot.send_message(chat_id=7241783674, text=msg, parse_mode="Markdown")
        await update.message.reply_text("Order confirm ho gaya bhai! Screenshot aur address alag se bhej dena seller ko /contact use karo aur bhejo cart ka screenshot and address link.")
    elif "no" in reply:
        await update.message.reply_text("Order cancel kar diya gaya. Agar kuch aur poochhna hai to /contact karo.")
    return ConversationHandler.END

# Contact seller
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Seller se baat karne ke liye yeh link use karo:\n👉 https://t.me/katiharvloger2")

# Cancel fallback
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Order process cancel kar diya gaya.")
    return ConversationHandler.END

# Main function
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
        
