import discord
from discord import app_commands
from discord.ext import commands
import datetime

class command(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.logch=None
    
    @app_commands.command(name="select_logch",description="select text channel for logging")
    async def select_logch(self,interaction:discord.Interaction,channel:discord.TextChannel=None):
        self.logch=channel
        if self.logch is None:
            await interaction.response.send_message(f"log system's message channel")
        else:
            await interaction.response.send_message(f"log {self.logch}")

    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        if after.channel!=before.channel:
            if before.channel!=None:
                sendch=member.guild.system_channel if self.logch is None else self.logch
                if len(before.channel.members)==0:
                    self.timee=datetime.datetime.now().replace(microsecond=0)
                    data={
                        "title":"Initiating call",
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
                            },
                            {
                                "name":"Time",
                                "value":f"{self.timee-self.times}",
                                "inline":True
                            }
                        ]
                    }
                    await sendch.send(embed=discord.Embed.from_dict(data=data))
            if after.channel!=None:
                sendch=member.guild.system_channel if self.logch is None else self.logch
                if len(after.channel.members)==1:
                    self.times=datetime.datetime.now().replace(microsecond=0)
                    data={
                        "title":"Initiating call",
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