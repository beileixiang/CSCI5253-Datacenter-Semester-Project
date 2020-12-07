import pymongo
from pymongo import MongoClient

import jsonpickle, pickle
import io, os, sys
import pika
import secrets, requests
import hashlib

import json
import subprocess

#Config
mongoDBHost = os.getenv("mongoDB_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and mongoDB({})".format(rabbitMQHost,mongoDBHost))

#RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMQHost))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
channel.exchange_declare(exchange='logs', exchange_type='topic')

#mongoDB
client = MongoClient(mongoDBHost, 27017)
db = client.fileinfo
collection = db["user"]

# hash = db.StringField()
# originalfiles = db.DictField()
# convertedfiles= db.DictField()

#RabbitMQ
def callback(ch, method, properties, body):
    data = json.loads(body)
    content = data["content"]
    filename = data["filename"]
    sh = data["hash"]
    
    #save data to file
    filedir = 'files/'+ filename
    with open(filedir, 'w') as f:
        f.write(content)

    # run java on content
    command = "java -mx4g -cp \"*\" edu.stanford.nlp.naturalli.OpenIE " + filedir
    try:
        output = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as e:                                                                                                   
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

    #update new converted file content to db
    convfilesDict = collection.find_one({"hash": sh})["convertedfiles"]
    # print(convfilesDict)
    convfilesDict[filename] = output.decode('utf-8')
    filter = { 'hash': sh } 
    newvalues = { "$set": { 'convertedfiles': convfilesDict } }
    collection.update_one(filter, newvalues) 

    ch.basic_ack(delivery_tag=method.delivery_tag)



channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)
channel.start_consuming()