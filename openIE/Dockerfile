FROM openjdk:slim
COPY --from=python:3.6 / /
#FROM python:latest
#COPY --from=openjdk:16-slim-buster * /

#RUN apt-get update && apt-get install python3
RUN  pip install pika pymongo requests 
RUN apt-get install unzip

#RUN  mkdir /app
ADD http://nlp.stanford.edu/software/stanford-corenlp-latest.zip /
RUN unzip stanford-corenlp-latest.zip

COPY worker.py /stanford-corenlp-4.2.0

WORKDIR stanford-corenlp-4.2.0
CMD python worker.py
