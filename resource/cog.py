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
        self.psql=psycopg2.connect(host=HOST,user=USERS,password=PASSWORD,database=DATABASE)

    def judge(self,vs:discord.VoiceState):
        if vs.channel!=None:
            er=[i for i in vs.channel.changed_roles if "@everyone" == i.name]
            if len(er)==1 and vs.channel.overwrites[er[0]].is_empty() or len(er)==0:
                return 1

    @commands.Cog.listener()
    async def on_voice_state_update(self,member:discord.Member,before:discord.VoiceState,after:discord.VoiceState):
        if before.channel!=after.channel:
            if before.channel!=None and len(before.channel.members)==0 and self.judge(before):
                with self.psql.cursor() as cursor:
                    sql=f"SELECT send_ch FROM {TABLENAME} WHERE guild_id = %s AND guild_name = %s"
                    cursor.execute(sql,(f"{member.guild.id}","send"))
                    if (ch:=cursor.fetchone()) is None:
                        sendch=member.guild.system_channel
                    else:
                        sendch=member.guild.get_channel(ch[0])

                    sql=f"SELECT unix, message_id FROM {TABLENAME} WHERE guild_id = %s AND ch_id = %s"
                    cursor.execute(sql,(f"{member.guild.id}",f"{before.channel.id}"))
                    if (tmp:=cursor.fetchone()) is not None:
                        retime=int(time.time())-tmp[0]
                        delme=await sendch.fetch_message(tmp[1])
                        await delme.delete()
                    else:
                        retime=0

                    sql=f"SELECT total_time FROM {TABLENAME} WHERE guild_id = %s AND ch_id = %s"
                    cursor.execute(sql,(f"{member.guild.id}",f"{before.channel.id}"))
                    if None in (totaltime:=cursor.fetchone()):
                        sql=f"UPDATE {TABLENAME} SET total_time = %s WHERE guild_id = %s AND ch_id = %s"
                        cursor.execute(sql,(f"{retime}",f"{member.guild.id}",f"{before.channel.id}"))
                    else:
                        sql=f"UPDATE {TABLENAME} SET total_time = %s WHERE guild_id = %s AND ch_id = %s"
                        cursor.execute(sql,(f"{retime+totaltime[0]}",f"{member.guild.id}",f"{before.channel.id}"))
                self.psql.commit()
                data={
                    "title":f"{datetime.timedelta(seconds=retime)}",
                    "color":11584734,
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

            if after.channel!=None and len(after.channel.members)==1 and self.judge(after):
                with self.psql.cursor() as cursor:
                    sql=f"SELECT send_ch FROM {TABLENAME} WHERE guild_id = %s AND guild_name = %s"
                    cursor.execute(sql,(f"{member.guild.id}","send"))
                    if (ch:=cursor.fetchone()) is None:
                        sendch=member.guild.system_channel
                    else:
                        sendch=member.guild.get_channel(ch[0])
                unix=int(time.time())
                data={
                    "title":f"{after.channel}",
                    "color":11584734,
                    "fields":[
                        {
                            "name":"Time",
                            "value":f"<t:{unix}:R>",
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
                    sql=f"SELECT unix FROM {TABLENAME} WHERE guild_id = %s AND ch_id = %s"
                    cursor.execute(sql,(f"{member.guild.id}",f"{after.channel.id}"))
                    if cursor.fetchone() is None:
                        sql=f"INSERT INTO {TABLENAME} (guild_name, guild_id, ch_id, message_id, unix) VALUES (%s, %s, %s, %s, %s)"
                        cursor.execute(sql,(f"{member.guild.name}",f"{member.guild.id}",f"{after.channel.id}", f"{message.id}", f"{unix}"))
                    else:
                        sql=f"UPDATE {TABLENAME} SET message_id = %s, unix = %s WHERE guild_id = %s AND ch_id = %s"
                        cursor.execute(sql,(f"{message.id}", f"{unix}", f"{member.guild.id}", f"{after.channel.id}"))
                self.psql.commit()
    
    @discord.app_commands.command(
            description="change the sending channel"
    )
    async def sendch(self,interaction:discord.Interaction,ch:discord.TextChannel):
        await interaction.response.defer()
        with self.psql.cursor() as cursor:
            sql=f"SELECT send_ch FROM {TABLENAME} WHERE guild_id = %s AND guild_name = %s"
            cursor.execute(sql,(f"{interaction.guild_id}","send"))
            if cursor.fetchone() is None:
                sql=f"INSERT INTO {TABLENAME} (guild_name, guild_id, send_ch) VALUES (%s, %s, %s)"
                cursor.execute(sql,("send",f"{interaction.guild_id}",f"{ch.id}"))
            else:
                sql=f"UPDATE {TABLENAME} SET send_ch = %s WHERE guild_id = %s AND guild_name = %s"
                cursor.execute(sql,(f"{ch.id}",f"{interaction.guild_id}","send"))
        self.psql.commit()
        await interaction.followup.send(f"send to {ch}")

    @discord.app_commands.command(
        description="init the sending channel"
    )
    async def initch(self,interaction:discord.Interaction):
        await interaction.response.defer()
        with self.psql.cursor() as cursor:
            sql=f"DELETE FROM {TABLENAME} WHERE guild_id = %s AND guild_name = %s"
            cursor.execute(sql,(f"{interaction.guild.id}","send"))
        self.psql.commit()
        await interaction.followup.send(f"change {interaction.guild.system_channel}")

    @discord.app_commands.command(
        description="show total time on channel"
    )
    async def totaltime(self,interaction:discord.Interaction,ch:discord.VoiceChannel):
        await interaction.response.defer()
        with self.psql.cursor() as cursor:
            sql=f"SELECT total_time FROM {TABLENAME} WHERE guild_id = %s AND ch_id = %s"
            cursor.execute(sql,(f"{interaction.guild_id}",f"{ch.id}"))
            if (result:=cursor.fetchone()) is None:
                await interaction.followup.send("N/A")
            else:
                data={
                    "title":f"{datetime.timedelta(seconds=result[0])}",
                    "color":11584734,
                    "fields":[
                        {
                            "name":"Channel",
                            "value":f"{ch}",
                            "inline":True
                        }
                    ]
                }
                await interaction.followup.send(embed=discord.Embed.from_dict(data=data))

async def setup(bot:commands.Bot):
    await bot.add_cog(command(bot))