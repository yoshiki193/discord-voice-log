FROM python:3.11
RUN apt-get update && apt -y upgrade
RUN pip install --upgrade pip && pip install --upgrade setuptools
RUN pip install discord.py && pip install psycopg2
RUN apt-get -y install lsb-release && apt-get install wget curl gnupg2 -y
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' &&\
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update && apt-get -y install postgresql-client-15
CMD ["python3","/root/opt/resource/bot.py"]