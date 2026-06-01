# menus.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, MessageHandler, CommandHandler, filters, ContextTypes

# 🟢 CHANGE THIS: Put your real Telegram User ID here so you receive the tickets
STAFF_IDS = [123456789]

# A clean string of your locker URL so menus.py doesn't have to look back at main.py
ADBLUEMEDIA_LOCKER_URL = "https://locked-content.com/?a5c505a"

def register_menu_handlers(application):
    # Register commands and callback buttons into the main app engine
    application.add_handler(CommandHandler("start", start_menu_trigger))
    application.add_handler(CallbackQueryHandler(show_guides, pattern="view_guides"))
    application.add_handler(CallbackQueryHandler(send_guide_text, pattern="guide_"))
    application.add_handler(CallbackQueryHandler(back_to_main, pattern="back_main"))
    application.add_handler(CallbackQueryHandler(handle_support_click, pattern="contact_staff"))
    
    # Listen to messages sent by staff members replying to support tickets
    application.add_handler(MessageHandler(filters.REPLY & filters.Chat(chat_id=set(STAFF_IDS)), handle_staff_reply))

# FUNCTION TO GENERATE THE CORE BUTTON MATRIX
def get_main_menu_keyboard(user_id, locker_url):
    personalized_url = f"{locker_url}&s1={user_id}"
    keyboard = [
        [InlineKeyboardButton("📺 Get Free 24h Trial", url=personalized_url)],
        [InlineKeyboardButton("📖 Device Setup Guides", callback_data="view_guides")],
        [InlineKeyboardButton("🙋‍♂️ Contact Support", callback_data="contact_staff")]
    ]
    return InlineKeyboardMarkup(keyboard)

# THE ASYNC START TRIGGER
async def start_menu_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    reply_markup = get_main_menu_keyboard(user_id, ADBLUEMEDIA_LOCKER_URL)
    
    await update.message.reply_text(
        f"Hello! To get your high-speed 24h IPTV Test Line, please complete one quick verification offer below.\n\n"
        "As soon as you finish, your line will be sent directly into this chat instantly!",
        reply_markup=reply_markup
    )

# DEVICE SETUP GUIDES SUB-MENU
async def show_guides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Amazon Firestick Setup", callback_data="guide_fire")],
        [InlineKeyboardButton("Smart TV (Smarters Pro)", callback_data="guide_smart")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="📖 **Select your device to view the step-by-step connection guide:**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# GUIDE CONTENT RESPONSES
async def send_guide_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("Back to Guides", callback_data="view_guides")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query.data == "guide_fire":
        text = (
            "**Firestick Installation Instructions:**\n\n"
            "1. Download the **Downloader App** from your Amazon App Store.\n"
            "2. Open Downloader and enter your application installer code.\n"
            "3. Select Xtream Codes API inside the app once installed.\n"
            "4. Grab your login details by completing the trial task on the main menu!"
        )
    elif query.data == "guide_smart":
        text = (
            "**Smart TV Installation Instructions:**\n\n"
            "1. Search for **IPTV Smarters Pro** on your TV app store.\n"
            "2. Install and launch the application.\n"
            "3. Select 'Login with Xtream Codes API'.\n"
            "4. Input the host URL and your unique survey reward credentials."
        )
        
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="Markdown")

# BACK TO MAIN MENU ROUTER
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    reply_markup = get_main_menu_keyboard(user_id, ADBLUEMEDIA_LOCKER_URL)
    
    await query.edit_message_text(
        text=f"Hello! To get your high-speed 24h IPTV Test Line, please complete one quick verification offer below.\n\n"
             "As soon as you finish, your line will be sent directly into this chat instantly!",
        reply_markup=reply_markup
    )

# STAFF SUPPORT FORWARDING
async def handle_support_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="📝 Please send your support question directly as a text message right now. Our staff will see it and reply right here."
    )
    context.user_data["waiting_for_support"] = True

# HOOK TO FORWARD INCOMING MESSAGES TO STAFF
async def check_and_forward_to_staff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_for_support"):
        user_id = update.message.from_user.id
        user_msg = update.message.text
        
        for staff_id in STAFF_IDS:
            try:
                support_ticket = (
                    f"⚠️ **NEW IPTV SUPPORT TICKET**\n"
                    f"👤 User ID: `{user_id}`\n"
                    f"💬 Message: {user_msg}\n\n"
                    f"👉 *To reply, use Telegram's built-in Reply feature on this exact message.*"
                )
                await context.bot.send_message(chat_id=staff_id, text=support_ticket, parse_mode="Markdown")
            except Exception:
                pass
                
        context.user_data["waiting_for_support"] = False
        await update.message.reply_text("✅ Your message has been sent to our tech team. Please wait right here for their reply.")

# STAFF RESPONSE ROUTING BACK TO USER
async def handle_staff_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        original_text = update.message.reply_to_message.text
        target_user_id = int(original_text.split("User ID: ")[1].split("\n")[0].strip())
        
        staff_response = f"💬 **Message from Support Team:**\n\n{update.message.text}"
        await context.bot.send_message(chat_id=target_user_id, text=staff_response, parse_mode="Markdown")
        await update.message.reply_text("🚀 Reply safely delivered.")
    except Exception:
        await update.message.reply_text("❌ Failed to route reply. Ensure you are replying directly to the active ticket message template.")
