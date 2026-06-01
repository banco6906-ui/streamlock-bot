# menus.py
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# List of staff/moderator Telegram User IDs
STAFF_IDS = [123456789, 987654321]

def register_menu_handlers(bot):
    
    # 1. MAIN WELCOME MENU
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        user_id = message.chat.id
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Pass the user's ID to your CPA locker link via the s1 parameter for tracking
        cpa_url = f"https://your-adbluemedia-link.com?s1={user_id}"
        
        btn_trial = InlineKeyboardButton(text="📺 Get Free 24h Trial", url=cpa_url)
        btn_guides = InlineKeyboardButton(text="📖 Device Setup Guides", callback_data="view_guides")
        btn_support = InlineKeyboardButton(text="🙋‍♂️ Contact Support", callback_data="contact_staff")
        
        markup.add(btn_trial, btn_guides, btn_support)
        
        welcome_text = (
            "🔥 **Welcome to Premium IPTV Automated Server** 🔥\n\n"
            "Get access to over 15,000 premium channels, live sports, and VOD movies.\n\n"
            "👇 Choose an option below to begin:"
        )
        bot.send_message(user_id, welcome_text, reply_markup=markup, parse_mode="Markdown")

    # 2. DEVICE SETUP GUIDES SUB-MENU
    @bot.callback_query_handler(func=lambda call: call.data == "view_guides")
    def show_guides(call):
        markup = InlineKeyboardMarkup(row_width=1)
        
        btn_firestick = InlineKeyboardButton(text="🟠 Amazon Firestick Setup", callback_data="guide_fire")
        btn_smarttv = InlineKeyboardButton(text="🔵 Smart TV (Smarters Pro)", callback_data="guide_smart")
        btn_back = InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="back_main")
        
        markup.add(btn_firestick, btn_smarttv, btn_back)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="📖 **Select your device to view the step-by-step connection guide:**",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 3. GUIDE CONTENT RESPONSES
    @bot.callback_query_handler(func=lambda call: call.data.startswith("guide_"))
    def send_guide_text(call):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text="⬅️ Back to Guides", callback_data="view_guides"))
        
        if call.data == "guide_fire":
            text = (
                "🟠 **Firestick Installation Instructions:**\n\n"
                "1. Download the **Downloader App** from your Amazon App Store.\n"
                "2. Open Downloader and enter the code for **Downloader Code Here**.\n"
                "3. Install the app, open it, and select Xtream Codes API.\n"
                "4. Grab your login data by generating a test token from the main menu!"
            )
        elif call.data == "guide_smart":
            text = (
                "🔵 **Smart TV Installation Instructions:**\n\n"
                "1. Search for **IPTV Smarters Pro** or **IBO Player** on your TV app store.\n"
                "2. Install and launch the application.\n"
                "3. Select 'Login with Xtream Codes API'.\n"
                "4. Input the host URL and your unique credentials generated from your trial."
            )
            
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # BACK TO MAIN MENU ROUTER
    @bot.callback_query_handler(func=lambda call: call.data == "back_main")
    def back_to_main(call):
        # Clears current markup and brings back the original start text/buttons
        send_welcome(call.message)

    # 4. STAFF SUPPORT FORWARDING (ANONYMOUS TICKETS)
    @bot.callback_query_handler(func=lambda call: call.data == "contact_staff")
    def handle_support_click(call):
        bot.send_message(call.message.chat.id, "📝 Please type your question below. A staff member will reply directly in this chat environment:")
        bot.register_next_step_handler(call.message, forward_to_staff)

    def forward_to_staff(message):
        user_id = message.chat.id
        for staff_id in STAFF_IDS:
            try:
                support_ticket = (
                    f"⚠️ **NEW IPTV SUPPORT TICKET**\n"
                    f"👤 User ID: `{user_id}`\n"
                    f"💬 Message: {message.text}\n\n"
                    f"👉 *Reply directly to this specific notification message to answer.*"
                )
                bot.send_message(staff_id, support_ticket, parse_mode="Markdown")
            except Exception:
                pass
        bot.send_message(user_id, "✅ Your message has been sent to our tech team. Please remain active here for their reply.")

    # STAFF RESPONSE ROUTING
    @bot.message_handler(func=lambda message: message.chat.id in STAFF_IDS and message.reply_to_message is not None)
    def handle_staff_reply(message):
        try:
            original_text = message.reply_to_message.text
            target_user_id = int(original_text.split("User ID: ")[1].split("\n")[0].strip())
            
            staff_response = f"💬 **Message from Support Team:**\n\n{message.text}"
            bot.send_message(target_user_id, staff_response, parse_mode="Markdown")
            bot.send_message(message.chat.id, "🚀 Reply safely delivered.")
        except Exception:
            bot.send_message(message.chat.id, "❌ Verification failed. Ensure you are directly replying to the ticket message template.")
