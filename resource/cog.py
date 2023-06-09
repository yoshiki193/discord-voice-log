import discord
from discord import app_commands
from discord.ext import commands
import datetime
import time
import psycopg2

USERS="postgres"
HOST=""
PASSWORD=""
DATABASE="dvl"
TABLENAME="vlog"

class command(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.logch=None
        self.psql=psycopg2.connect(host=HOST,user=USERS,password=PASSWORD,database=DATABASE)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        if after.channel!=before.channel:
            if before.channel!=None:
                if len(before.channel.members)==0 and len(before.channel.changed_roles)==0:
                    sendch=member.guild.system_channel
                    with self.psql:
                        with self.psql.cursor() as cursor:
                            sql=f"SELECT unix, message_id FROM {TABLENAME} WHERE guild_id = %s AND ch_id = %s"
                            cursor.execute(sql,(f"{member.guild.id}",f"{before.channel.id}"))
                            tmp=cursor.fetchone()
                    retime=int(time.time())-tmp[0]
                    delme=await sendch.fetch_message(tmp[1])
                    await delme.delete()
                    data={
                        "title":"通話記録",
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
                                "value":f"{datetime.timedelta(seconds=retime)}",
                                "inline":True
                            }
                        ]
                    }
                    await sendch.send(embed=discord.Embed.from_dict(data=data))
            
            if after.channel!=None:
                if len(after.channel.members)==1 and len(after.channel.changed_roles)==0:
                    sendch=member.guild.system_channel
                    unix=int(time.time())
                    data={
                        "title":f"通話が開始されました <t:{unix}:R>",
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
                    message=await sendch.send(content="@everyone",embed=discord.Embed.from_dict(data=data))
                    with self.psql:
                        with self.psql.cursor() as cursor:
                            ssql=f"SELECT unix FROM {TABLENAME} WHERE guild_id = %s AND ch_id = %s"
                            cursor.execute(ssql,(f"{member.guild.id}",f"{after.channel.id}"))
                            if cursor.fetchone() is None:
                                sql=f"INSERT INTO {TABLENAME} (guild_name, guild_id, ch_id, message_id, unix) VALUES (%s, %s, %s, %s, %s)"
                                cursor.execute(sql,(f"{member.guild.name}",f"{member.guild.id}",f"{after.channel.id}", f"{message.id}", f"{unix}"))
                            else:
                                sql=f"UPDATE {TABLENAME} SET message_id = %s, unix = %s WHERE guild_id = %s AND ch_id = %s"
                                cursor.execute(sql,(f"{message.id}", f"{unix}", f"{member.guild.id}", f"{after.channel.id}"))
                        self.psql.commit()

async def setup(bot:commands.Bot):
    await bot.add_cog(command(bot))