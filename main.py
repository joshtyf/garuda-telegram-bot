from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.error import TelegramError
import telegram.ext
import logging
import config
from uuid import uuid4
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive



updater = Updater(token=config.token, use_context=True)
dispatcher = updater.dispatcher
job_queue = updater.job_queue

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def get_pic(update, context):
    try:
        # Download the file
        file = update.message.photo[-1].get_file()
        file_name = file.download()
        context.bot.send_message(chat_id=update.effective_chat.id, text="File downloaded")
        
        # Authorise to gdrive
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
        drive = GoogleDrive(gauth)

        # Upload file
        folder = drive.ListFile({'q': "title='garu.jpg'"}).GetList()[0]
        file = drive.CreateFile({'parents': [{'id': folder['id']}]})
        file.SetContentFile(file_name)
        file.Upload()

        # Remove the file once uploaded
        os.remove(file_name)
    except IndexError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="We only accept images at the moment")


def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

def new_announcement(update, context):
    key = str(uuid4())
    value = ' '.join(context.args)

    #Store value
    context.chat_data[key] = value

    context.bot.send_message(chat_id=update.effective_chat.id, text=key)

def get_announcement(update, context):
    key = ' '.join(context.args)
    
    # Load value
    try:
        value = context.chat_data[key]
        update.message.reply_text(value)

    except KeyError:
        update.message.reply_text('Announcement not found')

def get_all_announcements(update, context):
    # Check if there are any announcements at all
    if not context.chat_data:
        text = 'No announcements available. Use /new_announcement to add a new one'
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    else:
        for key, value in context.chat_data.items():
            text = key, "->", value
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def callback_minute(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id='158794071', # set chatid 
                             text='One message every minute')

# job_minute = job_queue.run_repeating(callback_minute, interval=60, first=0)


start_handler = CommandHandler('start', start)
caps_handler = CommandHandler('caps', caps)
picture_handler = MessageHandler(Filters.all, get_pic)
unknown_handler = MessageHandler(Filters.command, unknown)
new_announcement_handler = CommandHandler('new_announcement', new_announcement)
get_announcement_handler = CommandHandler('get_announcement', get_announcement)
get_all_announcements_handler = CommandHandler('get_all', get_all_announcements)

# Note to self: order of adding the handlers are important
dispatcher.add_handler(start_handler)
dispatcher.add_handler(caps_handler)
dispatcher.add_handler(new_announcement_handler)
dispatcher.add_handler(get_announcement_handler)
dispatcher.add_handler(get_all_announcements_handler)
dispatcher.add_handler(picture_handler)
dispatcher.add_handler(unknown_handler)


updater.start_polling()