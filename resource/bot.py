import asyncio
import discord
from discord.ext import commands
import json

with open("id.json") as f:
    idl=json.load(f)

token=idl["token"]

intents=discord.Intents.default()
bot=commands.Bot(command_prefix="$",intents=intents)

async def main():
    async with bot:
        await bot.load_extension("cog")
        await bot.start(token=token)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online")
    await bot.tree.sync()

asyncio.run(main())