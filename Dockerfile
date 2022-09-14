FROM python:3.10 as wheel_builder

RUN apt-get update && \
apt-get install -y build-essential libssl-dev python3-dev bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev libpopt0

ENV POETRY_HOME /poetry
ENV POETRY_VERSION 1.2.0
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY ./poetry.lock /pyproject.toml ./

RUN mkdir ./wheelhouse && \
$POETRY_HOME/bin/poetry export -o ./requirements.txt --with-credentials &&\
pip wheel \
-w /wheelhouse \
--progress-bar off \
--no-cache-dir \
--no-clean \
--require-hashes \
-r ./requirements.txt


FROM python:3.10

ENV PYTHONBUFFERED 1

RUN apt-get update && apt-get install -y gettext

COPY --from=wheel_builder ./wheelhouse/ /tmp/wheelhouse
RUN pip install\
 --no-cache-dir\
 --disable-pip-version-check\
 --no-index\
 /tmp/wheelhouse/* && \
 rm -rf /tmp/wheelhouse

RUN mkdir -p /app
WORKDIR /app
COPY . .



