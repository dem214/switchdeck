FROM python:3.7

ENV PYTHONBUFFERED 1

RUN apt-get update
# Install GnuText
RUN apt-get install -y gettext

RUN useradd -ms /bin/bash switchdeck

USER switchdeck

WORKDIR /home/switchdeck

COPY --chown=switchdeck . /home/switchdeck/

RUN pip install -r requirements/production.txt

