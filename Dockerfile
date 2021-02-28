FROM python:3.9

ENV PYTHONBUFFERED 1

RUN apt-get update
# Install GnuText
RUN apt-get install -y gettext

RUN mkdir -p /app
WORKDIR /app

COPY . .

RUN pip install\
    --no-cache-dir\
    --disable-pip-version-check\
    -r ./requirements/production.txt

