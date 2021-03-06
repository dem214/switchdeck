FROM python:3.9

ENV PYTHONBUFFERED 1

RUN apt-get update
# Install GnuText
RUN apt-get install -y gettext

COPY ./requirements /requirements
RUN pip install\
    --no-cache-dir\
    --disable-pip-version-check\
    -r /requirements/production.txt

RUN mkdir -p /app
WORKDIR /app
COPY . .



