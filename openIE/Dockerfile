FROM openkbs/jre-mvn-py3

RUN  pip install pika pymongo 
RUN sudo apt-get install unzip

RUN  mkdir /app
ADD http://nlp.stanford.edu/software/stanford-corenlp-latest.zip /app
RUN unzip /app/stanford-corenlp-latest.zip

COPY worker.py /app/stanford-corenlp-4.2.0

WORKDIR "/app/stanford-corenlp-latest"
CMD python worker.py