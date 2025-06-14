FROM python:3.11
RUN apt-get update && apt -y upgrade
RUN pip install --upgrade pip && pip install --upgrade setuptools
RUN pip install discord.py && pip install sqlalchemy
CMD ["python3","/opt/bot.py"]