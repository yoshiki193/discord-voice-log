import discord
from discord.ext import commands
import datetime
import time
import psycopg2
import json

with open("id.json") as f:
    idl=json.load(f)

USERS=idl["postgres"]
HOST=idl["host"]
PASSWORD=idl["password"]
DATABASE="dvl"
TABLENAME="vlog"

class command(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.logch=None
        self.psql=psycopg2.connect(host=HOST,user=USERS,password=PASSWORD,database=DATABASE)
        with self.psql.cursor() as cursor:
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname not like 'pg_%' and schemaname != 'information_schema'")

            if not [ i for i in cursor.fetchall() if "vlog" in i]:
                cursor.execute("CREATE TABLE vlog (guild_name varchar(255),guild_id bigint,ch_id bigint,message_id bigint,unix bigint)")
                self.psql.commit()

    def judge(self,vs:discord.VoiceState):
        if vs.channel!=None:
            er=[i for i in vs.channel.changed_roles if "@everyone" == i.name]
            if len(er)==1 and vs.channel.overwrites[er[0]].is_empty() or len(er)==0:
                return 1
    
    @commands.Cog.listener()
    async def on_voice_state_update(self,member:discord.Member,before:discord.VoiceState,after:discord.VoiceState):
        if before.channel!=None and len(before.channel.members)==0 and self.judge(before):
            sendch=member.guild.system_channel
            with self.psql.cursor() as cursor:
                sql=f"SELECT unix, message_id FROM {TABLENAME} WHERE guild_id = %s AND ch_id = %s"
                cursor.execute(sql,(f"{member.guild.id}",f"{before.channel.id}"))
                tmp=cursor.fetchone()
            if tmp is not None:
                retime=int(time.time())-tmp[0]
                delme=await sendch.fetch_message(tmp[1])
                await delme.delete()
            else:
                retime=0
            data={
                "title":f"{before.channel}",
                "color":16729344,
                "fields":[
                    {
                        "name":"Time",
                        "value":f"{datetime.timedelta(seconds=retime)}",
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
    
        if after.channel!=None and len(after.channel.members)==1 and self.judge(after):
            sendch=member.guild.system_channel
            unix=int(time.time())
            data={
                "title":f"通話が開始されました <t:{unix}:R>",
                "color":16729344,
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