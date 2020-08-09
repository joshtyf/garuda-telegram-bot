from telegram.ext import Updater
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram.error import TelegramError
import telegram.ext
import logging
from uuid import uuid4
from doorway_submission import get_conv_handler
import os



TOKEN = os.environ['token']

# Construct Telegram updater and dispatcher objects
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
job_queue = updater.job_queue

# Set logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update, context):
    text = "Hello fellow Garudian! I am still a work in progress and Josh T didn't do extensive testing on me. So please don't try funny stuff on this bot because the code might break somewhere. \n If there are any bugs or suggestions for improvements, you can just pm Josh directly. \n You can get a list of available commands by typing /help"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def get_uhms_link(update, context):
    text = "Here is the uhms link: https://uhms.nus.edu.sg"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def get_meal_credits_link(update, context):
    text = "Here is the link to check your meal credits: https://aces.nus.edu.sg/Prjhml/login.do" 
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

def help_command(update, context):
    text = '''These are the available commands: \n
/upload_doorway_picture - for you to upload your doorway picture \n
/get_uhms_link - gets the link for the uhms website \n
/get_meal_credits_link - gets the link to check for your meal credit balance'''
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

start_handler = CommandHandler('start', start)
uhms_link_handler = CommandHandler('get_uhms_link', get_uhms_link)
meal_credits_handler = CommandHandler('get_meal_credits_link', get_meal_credits_link)
help_handler =  CommandHandler('help', help_command)
unknown_handler = MessageHandler(Filters.command, unknown)

# Note to self: order of adding the handlers are important
dispatcher.add_handler(start_handler)
dispatcher.add_handler(uhms_link_handler)
dispatcher.add_handler(meal_credits_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(get_conv_handler())
dispatcher.add_handler(unknown_handler)

PORT = int(os.environ.get('PORT', '8443'))

if __name__ == "__main__":
    # updater.start_polling() # Use on local
    updater.start_webhook(listen="0.0.0.0", # Use on web server
                        port=PORT,
                        url_path=TOKEN)
    updater.bot.set_webhook("https://hidden-anchorage-87038.herokuapp.com/" + TOKEN)
    updater.idle()