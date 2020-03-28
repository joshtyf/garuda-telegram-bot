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
import datetime

# Get env variables
TOKEN = os.environ['token']
SECRET = os.environ['client_secrets']
CREDENTIALS = os.environ['client_credentials']

json_secret = json.loads(SECRET) # creates a json file based of the client_credentials
with open('client_secrets.json', 'w') as outfile:
    json.dump(json_secret, outfile)

if os.path.exists("client_credentials.json"):
  os.remove("client_credentials.json")
  print("file deleted")
else:
  print("The file does not exist")



# Construct Telegram updater and dispatcher objects
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
job_queue = updater.job_queue

# Set logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

 # Connect to gdrive
try:
    gauth = GoogleAuth()
    # Manually load the credentials
    if gauth.credentials is None:
        json_credentials = json.loads(CREDENTIALS) # creates a json file based of the client_credentials
        with open('credentials.json', 'w') as outfile:
            json.dump(json_credentials, outfile)
        gauth.credentials = Storage('credentials.json').get()
    drive = GoogleDrive(gauth)
except AuthenticationError:
    print("Authentication Error")


def start(update, context):
    text = "Hello fellow Garudian! I am still a work in progress, so please treat me nicely. Type /help to get instructions on how to upload files for garu.jpg."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def help(update, context):
    text = "Send a picture or a video to me and I will automatically upload it to house comm's google drive. Sending it as an uncompressed file works best!"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def get_pic(update, context):
    try:
        # Download the picture
        file = update.message.photo[-1].get_file()
        file_name = file.download()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Picture received")

        # Upload picture
        try:
            folder = drive.ListFile({'q': "title='garu.jpg'"}).GetList()[0]
            file = drive.CreateFile({'parents': [{'id': folder['id']}]})
            file.SetContentFile(file_name)
            file.Upload()
        except ApiRequestError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Upload failed. Please contact admin")

        # Remove the picture once uploaded
        os.remove(file_name)
    except IndexError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="I couldn't receive the image. Are you sure you sent it correctly?")

def get_vid(update, context):
    try:
        # Download the video
        file = update.message.video.get_file()
        file_name = file.download()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Picture received")

        # Upload video
        try:
            folder = drive.ListFile({'q': "title='garu.jpg'"}).GetList()[0]
            file = drive.CreateFile({'parents': [{'id': folder['id']}]})
            file.SetContentFile(file_name)
            file.Upload()
        except ApiRequestError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Upload failed. Please contact admin")

        # Remove the video once uploaded
        os.remove(file_name)
    except IndexError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="I couldn't receive the video. Are you sure you sent it correctly?")

def get_file(update, context):
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
        text = "*Here are all the announcements*: \n\n"
        for key, value in context.chat_data.items():
            text += value + "\n\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def daily_announcements(context:telegram.ext.CallbackContext):
    # Check if there are any announcements at all
    if  context.chat_data:
        text = "*Here are the daily announcements:* \n\n"
        for key, value in context.chat_data.items():
            text = value + "\n\n"
        context.bot.send_message(chat_id='158794071', text=text) # change the chat id to the house chat

timedelta = datetime.timedelta(hours=8)
tzinfo = datetime.timezone(timedelta)
job_queue.run_daily(daily_announcements, datetime.time(hour=8,tzinfo=tzinfo))
    

start_handler = CommandHandler('start', start)
picture_handler = MessageHandler(Filters.photo, get_pic)
video_handler = MessageHandler(Filters.video, get_vid)
file_handler = MessageHandler(Filters.document.image, get_file)
unknown_handler = MessageHandler(Filters.command, unknown)
new_announcement_handler = CommandHandler('new_announcement', new_announcement)
get_announcement_handler = CommandHandler('get_announcement', get_announcement)
get_all_announcements_handler = CommandHandler('get_all', get_all_announcements)
help_handler = CommandHandler('help', help)

# Note to self: order of adding the handlers are important
dispatcher.add_handler(start_handler)
dispatcher.add_handler(new_announcement_handler)
dispatcher.add_handler(get_announcement_handler)
dispatcher.add_handler(get_all_announcements_handler)
dispatcher.add_handler(picture_handler)
dispatcher.add_handler(video_handler)
dispatcher.add_handler(file_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(unknown_handler)

PORT = int(os.environ.get('PORT', '8443'))

if __name__ == "__main__":
    # updater.start_polling() # Use on local
    updater.start_webhook(listen="0.0.0.0", # Use on web server
                        port=PORT,
                        url_path=TOKEN)
    updater.bot.set_webhook("https://hidden-anchorage-87038.herokuapp.com/" + TOKEN)
    updater.idle()