FROM python:3.8

RUN mkdir app

ADD . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

CMD python3 /app/bot.py
