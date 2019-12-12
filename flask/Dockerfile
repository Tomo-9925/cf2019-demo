FROM python:latest
LABEL maintainer="Tomo <example@example.com>"

ENV PYTHONUNBUFFERED 1
RUN mkdir /code && \
    pip install --upgrade pip
WORKDIR /code
ADD ./code/requirements.txt /code
RUN pip install -r requirements.txt
ADD ./code /code
