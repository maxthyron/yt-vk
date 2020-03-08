FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /bot
WORKDIR /bot

COPY requirements.txt /bot
RUN apt-get update -y && apt-get upgrade -y && apt-get install ffmpeg -y

RUN pip install -r requirements.txt

COPY . /bot
