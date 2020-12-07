FROM python:latest

# RUN  pip3 install -U setuptools
RUN  pip install flask jsonpickle \
     pika flask_mongoengine requests

RUN  mkdir /app
COPY  rest-server.py /app

EXPOSE	5000
CMD	python /app/rest-server.py