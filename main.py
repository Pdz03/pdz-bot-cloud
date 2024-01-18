import os
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from telegram import Update, Bot
from pydantic import BaseModel
from pymongo import MongoClient

MONGODB_CONNECTION_STRING = "mongodb+srv://test:sparta@cluster0.9xken9a.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp"
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.dbpdzcloud

class TelegramUpdate(BaseModel):
    update_id: int
    message: dict


app = FastAPI()

# Load variables from .env file if present
load_dotenv()

# Read the variable from the environment (or .env file)
bot_token = os.getenv('BOT_TOKEN')
secret_token = os.getenv("SECRET_TOKEN")
# webhook_url = os.getenv('CYCLIC_URL', 'http://localhost:8181') + "/webhook/"

bot = Bot(token=bot_token)
# bot.set_webhook(url=webhook_url)
# webhook_info = bot.get_webhook_info()
# print(webhook_info)


def auth_telegram_token(x_telegram_bot_api_secret_token: str = Header(None)) -> str:
    # return true # uncomment to disable authentication
    if x_telegram_bot_api_secret_token != secret_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return x_telegram_bot_api_secret_token


@app.post("/webhook/")
async def handle_webhook(update: TelegramUpdate, token: str = Depends(auth_telegram_token)):
    print(update.message)
    chat_id = update.message["chat"]["id"]
    try:
        text = update.message["text"]
    # document = update.message["document"]
    except KeyError:
        text = ""
        # Jika bukan pesan teks, coba akses chat_id dari jenis pesan lain
    # print("Received message:", update.message)

    if text == "/start":
        user = {
            'tele_id': chat_id,
            'tele_name': update.message["chat"]["first_name"],
            'username': update.message["chat"]["username"]
        }

        print(user)
        
        auth_user = db.users.find_one({'tele_id': user['tele_id']})
        if auth_user:
            print('Akun sudah terdaftar')
        else:            
            db.users.insert_one(user)

        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text="Selamat datang di Pdz Cloud, silakan upload filemu di sini!\n\nTekan /help untuk informasi lebih lanjut")
    elif text == "/help":
        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text="Selamat datang di Pdz Cloud, anda dapat mengupload file apa saja di sini.\n\nJadikan bot ini sebagai media penyimpanan pribadimu.\n\nGunakan bot ini dengan bijak.\n\nJika terjadi kendala selama penggunaan bot, hubungi akun ini @Pdz03\n\nTerimakasih")
    elif "forward_origin" in update.message:
        sender = ""
        type = ""
        caption = ""
        if "caption" in update.message:
            caption = update.message["caption"]
        else:
            caption = "No Caption"

        if "document" in update.message:
            type = "Dokumen"
        elif "photo" in update.message:
            type = "Gambar"
        elif "video" in update.message:
            type = "Video"
        elif "audio" in update.message:
            type = "Audio"

        if update.message["forward_origin"]["type"] == "hidden_user":
            sender = update.message["forward_origin"]["sender_user_name"]
        elif update.message["forward_origin"]["type"] == "user":
            id_sender = update.message["forward_origin"]["sender_user"]["username"]
            sender_name = update.message["forward_origin"]["sender_user"]["first_name"]
            sender = f"{sender_name} (@{id_sender})"

        if "text" in update.message:
            await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text="Maaf, gunakan bot ini hanya untuk mengupload File!")
        else:
            await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text=f"File berhasil diteruskan ke sini!\n\nFile diteruskan dari {sender}\nTipe = {type}\nCaption = {caption}")
    elif "photo" in update.message:
        type = "Gambar"
        caption = ""
        if "caption" in update.message:
            caption = update.message["caption"]
        else:
            caption = "No Caption"
        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text=f"Yeayy, file berhasil terupload!\n\nTipe = {type}\nCaption = {caption}")
    elif "video" in update.message:
        type = "Video"
        caption = ""
        if "caption" in update.message:
            caption = update.message["caption"]
        else:
            caption = "No Caption"
        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text=f"Yeayy, file berhasil terupload!\n\nTipe = {type}\nCaption = {caption}")
    elif "audio" in update.message:
        type = "Audio"
        caption = ""
        if "caption" in update.message:
            caption = update.message["caption"]
        else:
            caption = "No Caption"
        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text=f"Yeayy, file berhasil terupload!\n\nTipe = {type}\nCaption = {caption}")
    elif "document" in update.message:
        type = "Dokumen"
        caption = ""
        if "caption" in update.message:
            caption = update.message["caption"]
        else:
            caption = "No Caption"
        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text=f"Yeayy, file berhasil terupload!\n\nTipe = {type}\nCaption = {caption}")
    else:
        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text="Maaf, gunakan bot ini hanya untuk mengupload File!")

    return {"ok": True}
