FROM 172.16.3.193:5000/common/python:3.6-alpine
WORKDIR /app

ADD . /app

RUN apk add --no-cache build-base \
    && pip install --no-cache-dir -r requirements.txt \
	&& apk del build-base

EXPOSE 10014

CMD ["python", "run.py"]
