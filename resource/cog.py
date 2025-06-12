import discord
from discord.ext import commands
import logging
from db import Base, engine, SessionClass
from model import Dvl
import datetime
import time
import math
from sqlalchemy import select, insert, update

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers = [
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

class command(commands.Cog):
    def __init__(self,bot):
        Base.metadata.create_all(bind=engine)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member:discord.Member, before:discord.VoiceState, after:discord.VoiceState):
        if before.channel != after.channel and after.channel != None:
            if len(after.channel.members) == 1:
                db = SessionClass()
                embed = {
                    'title':f'Activate {after.channel}',
                    'color':32768,
                    'fields':[{
                        'name':'Event time',
                        'value':f'{datetime.datetime.now().replace(microsecond=0)}'
                    }]
                }
                sendMessage = await member.guild.system_channel.send(embed = discord.Embed.from_dict(data = embed))
                sql = select(Dvl).where(Dvl.ch_id == after.channel.id)
                result = db.execute(sql).scalars().first()
                if result == None:
                    sql = insert(Dvl).values(ch_id = after.channel.id, message_id = sendMessage.id, start_time = math.floor(time.time()), total_time = 0)
                    db.execute(sql)
                    db.commit()
                else:
                    sql = update(Dvl).where(Dvl.ch_id == after.channel.id).values(message_id = sendMessage.id, start_time = math.floor(time.time()))
                    db.execute(sql)
                    db.commit()
                db.close()

        elif before.channel != after.channel and before.channel != None:
            if len(before.channel.members) == 0:
                db = SessionClass()
                sql = select(Dvl).where(Dvl.ch_id == before.channel.id)
                result = db.execute(sql).scalars().first()
                callTime = time.time() - result.start_time
                totalTime = callTime + result.total_time
                delMessage = await member.guild.system_channel.fetch_message(result.message_id)
                await delMessage.delete()
                sql = update(Dvl).where(Dvl.ch_id == before.channel.id).values(total_time = totalTime)
                db.execute(sql)
                db.commit()
                db.close()
                embed = {
                    'title':f'Deactivate {before.channel}',
                    'color':16711680,
                    'fields':[{
                        'name':'Session time',
                        'value':f'{datetime.timedelta(seconds = math.floor(callTime))}'
                    }]
                }
                await member.guild.system_channel.send(embed = discord.Embed.from_dict(data = embed))
        
    @discord.app_commands.command(
        description="show total time on channel"
    )
    async def totaltime(self,interaction:discord.Interaction,ch:discord.VoiceChannel):
        db = SessionClass()
        sql = select(Dvl).where(Dvl.ch_id == ch.id)
        result = db.execute(sql).scalars().first()
        if result == None:
            await interaction.response.send_message(content = 'Not found')
        else:
            embed = {
                'title':f'{datetime.timedelta(seconds = math.floor(result.total_time))}',
                'fields':[{
                    'name':'Channel',
                    'value':f'{ch}'
                }]
            }
            await interaction.response.send_message(embed = discord.Embed.from_dict(data = embed))
        db.commit()
        db.close()
                

async def setup(bot:commands.Bot):
    await bot.add_cog(command(bot))