FROM python:3.12-slim

LABEL maintainer="dev.h.naseri@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY src/requirements.txt .
RUN pip install -i https://mirror-pypi.runflare.com/simple \
    --no-cache-dir -r requirements.txt

COPY ./src .
