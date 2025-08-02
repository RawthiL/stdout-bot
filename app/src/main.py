#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from openai import OpenAI
import os
import sys
sys.path.append('/home/app/code')
from bot_graph import build_model, build_graph, user_graph_interaction



TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
if TELEGRAM_TOKEN == "":
    raise ValueError("Could not retrieve telegram token from enviroment variable TELEGRAM_TOKEN")
print(TELEGRAM_TOKEN)

LLM_URL = os.getenv("LLM_URL", "")
if LLM_URL == "":
    raise ValueError("Model url from enviroment variable LLM_URL")
print(LLM_URL)

LLM_TOKEN = os.getenv("LLM_TOKEN", "")
if LLM_TOKEN == "":
    raise ValueError("Could not retrieve model token from enviroment variable LLM_TOKEN")
print(LLM_TOKEN)

MODEL_NAME = os.getenv("MODEL_NAME", "")
if MODEL_NAME == "":
    raise ValueError("Could not retrieve model name from enviroment variable MODEL_NAME")
print(MODEL_NAME)



POSTGRESQL_DB_URI = os.getenv("POSTGRESQL_DB_URI", None)
if POSTGRESQL_DB_URI is None or len(POSTGRESQL_DB_URI) == 0:
    print("WARNING: No postgresql URI set, falling back to InMemorySaver!")
    POSTGRESQL_DB_URI = None
print(POSTGRESQL_DB_URI)


llm = build_model(LLM_URL, LLM_TOKEN, MODEL_NAME)

graph = build_graph(llm, postgresql_db_uri=POSTGRESQL_DB_URI)




# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)







# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # """Echo the user message."""
    # await update.message.reply_text(update.message.text)
    
    await update.message.reply_text(user_graph_interaction(graph, update.message.from_user.id, update.message.text, user_name=update.message.from_user.first_name))


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()