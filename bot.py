import logging
import random
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup,
    KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes,
    ConversationHandler
)

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Stages
AMOUNT, CONFIRM, ADDRESS, SCREENSHOT = range(4)

# Seller chat ID (replace with your actual Telegram ID)
SELLER_ID = 7241783674

# Permanent reply buttons
main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Order"), KeyboardButton("Contact")],
        [KeyboardButton("Language"), KeyboardButton("Menu")],
        [KeyboardButton("Help"), KeyboardButton("Cancel")]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "स्वागत है! Order देने के लिए 'Order' दबाएं या /order कमांड का इस्तेमाल करें।",
        reply_markup=main_keyboard
    )

async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Order Now", web_app= {"url": "https://katiharvloger.github.io/Order"})]]
    await update.message.reply_text("Order के लिए नीचे क्लिक करें:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("कृपया अपना कुल ऑर्डर अमाउंट भेजें (₹ में):", reply_markup=ReplyKeyboardRemove())
    return AMOUNT

async def amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text)
        if amount < 199:
            await update.message.reply_text("कम से कम ₹199 का ऑर्डर ज़रूरी है। कृपया दुबारा कोशिश करें।")
            return AMOUNT

        discount = 0
        extra = 0
        if 199 <= amount <= 248:
            discount = 90
            extra = 15
        elif 249 <= amount <= 298:
            discount = 110
        elif amount >= 299:
            discount = 125

        final_amount = amount - discount + extra
        context.user_data["order_amount"] = amount
        context.user_data["discount"] = discount
        context.user_data["extra"] = extra
        context.user_data["final_amount"] = final_amount

        await update.message.reply_text(
            f"Discount: ₹{discount}\nExtra Charge: ₹{extra}\nFinal Amount: ₹{final_amount}\n\nOrder Confirm karein? (yes/no)"
        )
        return CONFIRM

    except ValueError:
        await update.message.reply_text("कृपया एक वैध नंबर भेजें।")
        return AMOUNT

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "yes":
        await update.message.reply_text("अब कृपया अपना address link भेजें।")
        return ADDRESS
    else:
        await update.message.reply_text("ऑर्डर रद्द कर दिया गया।", reply_markup=main_keyboard)
        return ConversationHandler.END

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text("अब कृपया अपने cart का screenshot भेजें।")
    return SCREENSHOT

async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["screenshot"] = update.message.photo[-1].file_id

        order_id = f"ORD{random.randint(1000,9999)}"
        context.user_data["order_id"] = order_id

        user = update.message.from_user
        amount = context.user_data["order_amount"]
        discount = context.user_data["discount"]
        extra = context.user_data["extra"]
        final = context.user_data["final_amount"]
        address = context.user_data["address"]

        # Send confirmation to customer
        await update.message.reply_text(
            f"धन्यवाद! आपका Order Confirm हो गया है।\n\n"
            f"Order ID: {order_id}\nFinal Amount: ₹{final}\n\n"
            "Delivery जल्द ही की जाएगी!",
            reply_markup=main_keyboard
        )

        # Send to seller
        await context.bot.send_message(
            chat_id=SELLER_ID,
            text=(
                f"नया Order आया है!\n\n"
                f"Order ID: {order_id}\n"
                f"User ID: {user.id}\nUsername: @{user.username or 'N/A'}\n"
                f"Amount: ₹{amount}\nDiscount: ₹{discount}\nExtra Charge: ₹{extra}\nFinal Amount: ₹{final}\n"
                f"Address: {address}"
            )
        )
        await context.bot.send_photo(chat_id=SELLER_ID, photo=context.user_data["screenshot"])

        return ConversationHandler.END
    else:
        await update.message.reply_text("कृपया एक valid screenshot भेजें।")
        return SCREENSHOT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("कार्रवाई रद्द कर दी गई।", reply_markup=main_keyboard)
    return ConversationHandler.END

if __name__ == "__main__":
    from telegram.ext import ApplicationBuilder

    app = ApplicationBuilder().token("7069586996:AAG5A-LLSWaQrLQ9EqM8_JihaQI3I90bFik").build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^Order$"), handle_order)
        ],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_input)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            SCREENSHOT: [MessageHandler(filters.PHOTO, screenshot)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("order", order_command))
    app.add_handler(CommandHandler("cancel", cancel))

    app.run_polling()
