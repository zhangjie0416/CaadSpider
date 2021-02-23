FROM 172.16.3.193:5000/common/python:3.6-centos

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10021

CMD ["python", "manage.py", "runserver", "0.0.0.0:10021"]
