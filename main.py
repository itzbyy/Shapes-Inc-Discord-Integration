import os
import discord
from openai import OpenAI
from flask import Flask
from threading import Thread
import asyncio
import time

app = Flask("")

@app.route("/")
def home():
    return "✨ your bot its alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

SHAPESINC_API_KEY = os.getenv("SHAPESINC_API_KEY")
SHAPE_MODEL = os.getenv("SHAPESINC_SHAPE_USERNAME")
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

if not SHAPESINC_API_KEY or not SHAPE_MODEL or not DISCORD_TOKEN or not GUILD_ID or not CHANNEL_ID:
    raise ValueError("⚠️ variable error: SHAPESINC_API_KEY, SHAPESINC_SHAPE_USERNAME, DISCORD_BOT_TOKEN, DISCORD_GUILD_ID y DISCORD_CHANNEL_ID")

print("shape model:", SHAPE_MODEL)

shapes = OpenAI(
    api_key=SHAPESINC_API_KEY,
    base_url="https://api.shapes.inc/v1/",
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# cooldown system
last_request_time = 0
cooldown_seconds = 5  # ajusta esto según tu límite de uso

@client.event
async def on_ready():
    print(f"✅ Bot conected as: {client.user}")

@client.event
async def on_message(msg):
    global last_request_time

    if msg.author.bot:
        return
    if msg.guild is None or msg.guild.id != GUILD_ID:
        return
    if msg.channel.id != CHANNEL_ID:
        return

    now = time.time()
    if now - last_request_time < cooldown_seconds:
        await msg.channel.send(f"wait a little for asking again xd ({cooldown_seconds}s cooldown)")
        return

    last_request_time = now

    print(f"message by {msg.author}: {msg.content} in the channel {msg.channel.name} in the server {msg.guild.name}")

    async with msg.channel.typing():
        try:
            resp = shapes.chat.completions.create(
                model=SHAPE_MODEL,
                messages=[{"role": "user", "content": msg.content}]
            )
            respuesta = resp.choices[0].message.content
            print("respuesta shapes:", respuesta)
            await msg.reply(respuesta)
        except Exception as e:
            print("error al consultar shapes:", str(e))
            await msg.reply("hubo un error al responder uwu")

if __name__ == "__main__":
    keep_alive()
    client.run(DISCORD_TOKEN)
