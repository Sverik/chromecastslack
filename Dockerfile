FROM python:3.6-alpine

RUN apk update && apk add gcc libc-dev linux-headers

WORKDIR /src

ADD . /src/

RUN pip install -r requirements.txt

CMD python3 listener.py
