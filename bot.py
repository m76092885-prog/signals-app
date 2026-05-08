from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    Update,
    MenuButtonWebApp
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

# ===== TOKEN =====

TOKEN = "8355508722:AAEgH0tfnjxh7G1ke_gGsmt7TdwvZNkw8uk"

# ===== YOUR RENDER SITE =====

WEBAPP_URL = "https://signals-app-1-kbm1.onrender.com/?v=7000"

# ===== START =====

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [

        [
            InlineKeyboardButton(

                text="🚀 OPEN CYBER SIGNALS",

                web_app=WebAppInfo(
                    url=WEBAPP_URL
                )
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(
        keyboard
    )

    await update.message.reply_text(

        text=(
            "🔥 CYBER SIGNALS\n\n"
            "Realtime Trading Interface\n"
            "Live Charts • Buy/Sell Signals"
        ),

        reply_markup=reply_markup
    )

# ===== MAIN =====

def main():

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    # ===== MENU BUTTON =====

    app.bot.set_chat_menu_button(

        menu_button=MenuButtonWebApp(

            text="🚀 Signals",

            web_app=WebAppInfo(
                url=WEBAPP_URL
            )
        )
    )

    # ===== COMMANDS =====

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    print("BOT STARTED")

    # ===== RUN =====

    app.run_polling()

# ===== START APP =====

if __name__ == "__main__":
    main()
