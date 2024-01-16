import os
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from telegram import Update, Bot
from pydantic import BaseModel


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
        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text="Selamat datang di Pdz Cloud, silakan upload filemu di sini!\n\nTekan /help untuk informasi lebih lanjut")
    elif text == "/help":
        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text="Selamat datang di Pdz Cloud, anda dapat mengupload file apa saja di sini.\n\nJadikan bot ini sebagai media penyimpanan pribadimu.\n\nGunakan bot ini dengan bijak.\n\nJika terjadi kendala selama penggunaan bot, hubungi akun ini @Pdz03\n\nTerimakasih")
    elif update.message["forward_origin"]:
        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text="Pesan berhasil diteruskan ke sini!")
    else:
        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text="Maaf, gunakan bot ini hanya untuk mengupload File!")

    # if update.message["photo"]:
    #     caption = update.message["caption"] or "No Caption"
    #     await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text=f"Yeayy, file berhasil terupload!\n\nTipe = Gambar\nCaption = {caption}")
    # elif update.message["video"]:
    #     caption = update.message["caption"] or "No Caption"
    #     await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text=f"Yeayy, file berhasil terupload!\n\nTipe = Video\nCaption = {caption}")
    # elif update.message["audio"]:
    #     caption = update.message["caption"] or "No Caption"
    #     await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text=f"Yeayy, file berhasil terupload!\n\nTipe = Audio\nCaption = {caption}")
    # elif update.message["document"]:
    #     caption = update.message["caption"] or "No Caption"
    #     await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text=f"Yeayy, file berhasil terupload!\n\nTipe = Dokumen\nCaption = {caption}")

    # if update.message.content_type in ['document', 'audio', 'photo', 'video']:
    #     await bot.send_message(chat_id=chat_id, text="Yeayy, file berhasil terupload")

    return {"ok": True}
