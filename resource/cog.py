import discord
from discord import app_commands
from discord.ext import commands
import datetime

class command(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.logch=None
    
    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        if after.channel!=before.channel:
            if before.channel!=None:
                sendch=member.guild.system_channel
                if len(before.channel.members)==0:
                    data={
                        "title":f"{before.channel}終了",
                        "fields":[
                            {
                                "name":"Channel",
                                "value":f"{before.channel}",
                                "inline":True
                            },
                            {
                                "name":"By",
                                "value":f"{member}",
                                "inline":True
                            }
                        ]
                    }
                    await sendch.send(embed=discord.Embed.from_dict(data=data))
            if after.channel!=None:
                sendch=member.guild.system_channel
                if len(after.channel.members)==1:
                    data={
                        "title":f"{after.channel}開始",
                        "fields":[
                            {
                                "name":"Channel",
                                "value":f"{after.channel}",
                                "inline":True
                            },
                            {
                                "name":"By",
                                "value":f"{member}",
                                "inline":True
                            }
                        ]
                    }
                    await sendch.send(content="@everyone",embed=discord.Embed.from_dict(data=data))

async def setup(bot:commands.Bot):
    await bot.add_cog(command(bot))