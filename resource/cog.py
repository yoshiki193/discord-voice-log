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
            if before.channel!=None:
                sendch=member.guild.system_channel if self.logch is None else self.logch
                if len(before.channel.members)==0:
                    await sendch.send(embed=discord.Embed(title="end call",description=f"{before.channel} by {member}"))
            if after.channel!=None:
                sendch=member.guild.system_channel if self.logch is None else self.logch
                if len(after.channel.members)==1:
                    await sendch.send(content="@everyone",embed=discord.Embed(title="initiating call",description=f"{after.channel} by {member}"))

async def setup(bot:commands.Bot):
    await bot.add_cog(command(bot))