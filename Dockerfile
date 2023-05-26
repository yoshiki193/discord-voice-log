FROM python:3
RUN apt-get update
RUN pip install --upgrade pip && pip install --upgrade setuptools
RUN pip install discord.py 