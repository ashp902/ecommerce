FROM python:3

RUN pip3 install --upgrade pip

ENV PYTHONUNBUFFERED 1

WORKDIR /app
ADD . /app
COPY ./requirements.txt /app/requirements.txt

EXPOSE 8003

RUN pip3 install -r requirements.txt

COPY . /app