FROM python:3.7

ENV PYTHONBUFFERED 1

RUN apt-get update
# Install GnuText
RUN apt-get install -y gettext

COPY requirements.txt /
RUN pip install -r requirements.txt

RUN mkdir /app

WORKDIR app
