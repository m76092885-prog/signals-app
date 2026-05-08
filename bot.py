import asyncio

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

# ===== NEW WEBAPP =====

WEBAPP_URL = "https://signals-app-1-kbm1.onrender.com/?v=999999"

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
            "Realtime Trading Interface"
        ),

        reply_markup=reply_markup
    )

# ===== POST INIT =====

async def post_init(app):

    await app.bot.set_chat_menu_button(

        menu_button=MenuButtonWebApp(

            text="🚀 Signals",

            web_app=WebAppInfo(
                url=WEBAPP_URL
            )
        )
    )

    print("MENU BUTTON UPDATED")

# ===== MAIN =====

def main():

    app = (
        Application
        .builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    print("BOT STARTED")

    app.run_polling()

# ===== RUN =====

if __name__ == "__main__":
    main()
