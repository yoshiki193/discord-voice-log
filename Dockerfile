FROM python:3
RUN apt-get update
RUN pip install --upgrade pip && pip install --upgrade setuptools
RUN pip install discord.py 
CMD [ "python3","/root/opt/resource/bot.py" ]