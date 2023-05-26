import discord
from discord import app_commands
from discord.ext import commands

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
            if before.channel==None and after.channel!=None:
                sendch=member.guild.system_channel if self.logch is None else self.logch
                if len(after.channel.members)==1:
                    await sendch.send(content=f"started by {member}")
            elif before.channel!=None:
                sendch=member.guild.system_channel if self.logch is None else self.logch
                if len(before.channel.members)==0:
                    await sendch.send(content=f"ended by {member}")

async def setup(bot:commands.Bot):
    await bot.add_cog(command(bot))