from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.error import TelegramError
import telegram.ext
import logging
from uuid import uuid4
import os
from pydrive.auth import AuthenticationError, GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError
import json
from oauth2client.file import Storage

# Get env variables
TOKEN = os.environ['token']
CREDENTIALS = os.environ['client_credentials']
json_object = json.loads(CREDENTIALS) # creates a json file based of the client_credentials
with open('client_credentials.json', 'w') as outfile:
    json.dump(json_object, outfile)

# Construct Telegram updater and dispatcher objects
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
job_queue = updater.job_queue

# Set logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

 # Connect to gdrive
try:
    gauth = GoogleAuth()
    gauth.credentials = Storage('client_credentials.json').get()
    drive = GoogleDrive(gauth)
except AuthenticationError:
    print("Authentication Error")


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello fellow Garudian!")

def get_pic(update, context):
    try:
        # Download the picture
        file = update.message.photo[-1].get_file()
        file_name = file.download()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Picture received")

        # Upload file
        try:
            folder = drive.ListFile({'q': "title='garu.jpg'"}).GetList()[0]
            file = drive.CreateFile({'parents': [{'id': folder['id']}]})
            file.SetContentFile(file_name)
            file.Upload()
        except ApiRequestError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Upload failed. Please contact admin")

        # Remove the file once uploaded
        os.remove(file_name)
    except IndexError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="I couldn't receive the image. Are you sure you sent it correctly?")

def get_pic_file(update, context):
    try:
        # Download the file
        file = update.message.document.get_file()
        file_name = file.download()
        context.bot.send_message(chat_id=update.effective_chat.id, text="File recevied")

        # Upload file
        try:
            folder = drive.ListFile({'q': "title='garu.jpg'"}).GetList()[0]
            file = drive.CreateFile({'parents': [{'id': folder['id']}]})
            file.SetContentFile(file_name)
            file.Upload()
        except ApiRequestError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Upload failed. Please contact admin")

        # Remove the file once uploaded
        os.remove(file_name)
    except TelegramError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="I couldn't receive the image file. Are you sure you sent it correctly?")

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


start_handler = CommandHandler('start', start)
picture_handler = MessageHandler(Filters.photo, get_pic)
pic_file_handler = MessageHandler(Filters.document.image, get_pic_file)
unknown_handler = MessageHandler(Filters.command, unknown)
new_announcement_handler = CommandHandler('new_announcement', new_announcement)
get_announcement_handler = CommandHandler('get_announcement', get_announcement)
get_all_announcements_handler = CommandHandler('get_all', get_all_announcements)

# Note to self: order of adding the handlers are important
dispatcher.add_handler(start_handler)
dispatcher.add_handler(new_announcement_handler)
dispatcher.add_handler(get_announcement_handler)
dispatcher.add_handler(get_all_announcements_handler)
dispatcher.add_handler(picture_handler)
dispatcher.add_handler(pic_file_handler)
dispatcher.add_handler(unknown_handler)

PORT = int(os.environ.get('PORT', '8443'))

if __name__ == "__main__":
    updater.start_webhook(listen="0.0.0.0",
                        port=PORT,
                        url_path=TOKEN)
    updater.bot.set_webhook("https://hidden-anchorage-87038.herokuapp.com/" + TOKEN)
    updater.idle()