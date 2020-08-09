from pydrive.auth import AuthenticationError, GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters
import os
from oauth2client.file import Storage
import json

# GDrive auth
SECRET = os.environ['client_secrets']
CREDENTIALS = os.environ['client_credentials']
ZONE, NAME, PHOTO = range(3)

json_secret = json.loads(SECRET) # creates a json file based of the client_credentials
with open('client_secrets.json', 'w') as outfile:
    json.dump(json_secret, outfile)

try:
    gauth = GoogleAuth()
    if gauth.credentials is None:
        json_credentials = json.loads(CREDENTIALS) # creates a json file based of the client_credentials
        with open('credentials.json', 'w') as outfile:
            json.dump(json_credentials, outfile)
        gauth.credentials = Storage('credentials.json').get()
    drive = GoogleDrive(gauth)
except AuthenticationError:
    print("Authentication Error")

def get_conv_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('upload_doorway_picture', upload_door_pic)],

        states={
            ZONE: [MessageHandler(Filters.regex('^(Zone A|Zone B|Zone C|Zone D)$'), get_zone)],

            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],

            PHOTO: [MessageHandler(Filters.photo, get_pic)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

def upload_door_pic(update, context):
    reply_keyboard = [['Zone A', 'Zone B', 'Zone C', 'Zone D']]

    update.message.reply_text(
        'Hi! '
        'Send /cancel to stop talking to me.\n\n'
        'What zone are you from?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return ZONE

def get_pic(update, context):
    try:
        # Download the picture
        file = update.message.photo[-1].get_file()
        file_name = file.download()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Picture received")

        # Upload picture
        try:
            folder = drive.ListFile({'q': f"title='{context.user_data['zone']}'"}).GetList()[0]
            file = drive.CreateFile({'parents': [{'id': folder['id']}], 'title': context.user_data['name']})
            file.SetContentFile(file_name)
            file.Upload()
        except ApiRequestError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Upload failed. Please contact admin")

        # Remove the picture once uploaded
        os.remove(file_name)
    except IndexError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="I couldn't receive the image. Are you sure you sent it correctly?")

    return ConversationHandler.END

def get_zone(update, context):
    context.user_data['zone'] = update.message.text
    update.message.reply_text(
        f'So you are from {update.message.text}! Can you tell me your name?\n'
        'If you selected the wrong zone, send /cancel to stop. Then send /upload_doorway_picture again',
        reply_markup=ReplyKeyboardRemove())

    return NAME

def get_name(update, context):
    context.user_data['name'] = update.message.text
    update.message.reply_text(
        f'Hi {update.message.text}! Now, send me the photo you want to upload!\n'
        'If you typed your name wrongly, send /cancel to stop. Then send /upload_doorway_picture again')

    return PHOTO

def cancel(update, context):
    update.message.reply_text('Bye!',
                            reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END



