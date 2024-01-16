from telegram import Update  
from telegram import InputMedia , InputMediaAudio , InputMediaDocument ,  InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler  , ApplicationBuilder , ContextTypes , MessageHandler , filters , CallbackQueryHandler
import requests , io
from mutagen.id3 import ID3
from geniuslyrics import *
from lyricsdotcom import search

from typing import final
from musicHandler import getDownUrl

# Telegram Bot token
BOT_TOKEN:final = '6312020010:AAHfqBT5cjEkRKHH3FhsCGbnDCbifOr6wAw'

CHAT_ID:final = 6322389290

def extract_title(mp3_binary):
    tags = ID3(io.BytesIO(mp3_binary)).items()
    title_frame = next((frame for frame_id, frame in tags if frame_id == 'TIT2'), None)
    return title_frame.text[0].split("(")[0]

def split_text(text):
    midpoint = len(text) // 2
    return text[:midpoint], text[midpoint:]



async def start_command(update:Update , context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("i'm alive yay")

async def test_keyboard(update:Update  , context:ContextTypes.DEFAULT_TYPE) :
    results = search(context.args[0])

    keyboard_element = [ InlineKeyboardButton(f"{result['term']}" , callback_data = f"{result['link']}") for result in results]
    keyboard = []
    keyboard.append(keyboard_element)
    #keyboard = [
    #    [
    #        InlineKeyboardButton("Option 1", callback_data="1"),
    #        InlineKeyboardButton("Option 2", callback_data="2"),
    #    ],
    #    [InlineKeyboardButton("Option 3", callback_data="3")],
    #]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("chose one : " , reply_markup=reply_markup )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")


async def get_mp3(update:Update , context:ContextTypes.DEFAULT_TYPE , txt:str = None):
    
    if txt : 
        resp = requests.get(getDownUrl(txt))
        print(resp.content)
        audioFile = resp.content
        await update.message.reply_audio( write_timeout=300, read_timeout=300 , pool_timeout=300 ,   audio=audioFile )
        parts = ovhApiLyrics(extract_title(audioFile) , True)
        for part in parts : 
            await update.message.reply_text( " ".join(part)  , parse_mode='HTML')
    else :
        resp = requests.get(getDownUrl(context.args[0]))
        await update.message.reply_audio( write_timeout=300, read_timeout=300 , pool_timeout=300 ,   audio=resp.content )


async def handle_text(update:Update , context:ContextTypes.DEFAULT_TYPE):
    print("handeled")
    text = update.message.text
    await get_mp3(update , context , text)


async def get_lyrics(update:Update , context:ContextTypes.DEFAULT_TYPE):
    parts = ovhApiLyrics(" ".join(context.args) , True)
    for part in parts : 
        await update.message.reply_text( " ".join(part)  , parse_mode='HTML')
    
    

        


    
async def error(update:Update , context : ContextTypes.DEFAULT_TYPE):
    print(f'exception  cause error : {context.error}')


if __name__ == '__main__':
    
    
    print('bot is starting..')
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start' , start_command ))
    app.add_handler(CommandHandler('get_mp3' , get_mp3 , has_args=True))
    app.add_handler(CommandHandler('get_lyrics' , get_lyrics ))
    app.add_handler(CommandHandler('test_keyboard' , test_keyboard ))
    app.add_handler(CallbackQueryHandler(button))
    
    app.add_handler(MessageHandler(filters.TEXT , handle_text))
    

    app.add_error_handler(error)

    
    print("polling ...")
    app.run_polling(poll_interval=3)