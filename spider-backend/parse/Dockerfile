FROM 172.16.3.193:5000/common/python:3.6-alpine

WORKDIR /app

ADD . /app

RUN apk add --no-cache build-base openssl-dev \
    && apk add --no-cache libxslt-dev libffi-dev \
    && pip install --no-cache-dir -r requirements.txt \
	&& apk del build-base openssl-dev

EXPOSE 10013

CMD ["python", "run.py"]
