import asyncio
import discord
from discord.ext import commands
import os

token=os.getenv("BOT_TOKEN")

EXTENTIONS=["cog"]

intents=discord.Intents.all()
bot=commands.Bot(command_prefix="$",intents=intents)

async def load_extensions():
    for ex in EXTENTIONS:
        await bot.load_extension(ex)

async def main():
    async with bot:
        await load_extensions()
        await bot.start(token=token)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online")
    await bot.tree.sync()

asyncio.run(main())