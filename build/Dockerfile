FROM python:3.10

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/app"

ARG build_deps="apt-utils \
                vim \
                curl \
                bash \
                sudo \
                wget \
                inetutils-ping \
                telnet \
                screen \
                "

RUN apt update && \
    apt -y upgrade && \
    apt -y install ${build_deps} && \
    apt clean

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /app

