FROM python:3.6

RUN pip install psycopg2
RUN pip install django==2.0.4

RUN pip install channels
RUN pip install channels_redis

RUN apt-get update && apt-get install -y postgresql-client

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /opt/app
COPY . /opt/app/web_auction/

COPY entrypoint.sh /opt/app/web_auction/entrypoint.sh
RUN chmod +x /opt/app/web_auction/entrypoint.sh

WORKDIR /opt/app/web_auction/

