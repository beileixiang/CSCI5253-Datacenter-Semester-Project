from flask import Response, Flask, request
from flask_mongoengine import MongoEngine

import jsonpickle
import io, os, sys
import pika
import secrets, requests
import hashlib

import json



#Config
mongoDBHost = os.getenv("mongoDB_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and mongoDB({})".format(rabbitMQHost,mongoDBHost))

app = Flask(__name__)

#RabbitMQ


#mongoDB
app.config['MONGODB_SETTINGS'] = {
    'db': 'fileinfo',
    'host': mongoDBHost,
    'port': 27017
}
db = MongoEngine(app)
class User(db.Document):
    hash = db.StringField()
    originalfiles = db.DictField()
    convertedfiles= db.DictField()

#FLASK
@app.route('/upload', methods=['POST'])
def upload_file():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMQHost))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)
    channel.exchange_declare(exchange='logs', exchange_type='topic')

    if request.method == 'POST':
        #get data from request
        data = request.json
        token = data["token"]
        content = data["content"]
        filename = data["filename"]

        hash_object = hashlib.md5(token.encode('UTF-8'))
        sh = hash_object.hexdigest() 
        data['hash'] =sh
        #update database
        try:
            user = User.objects(hash=sh).get()
        except:
            user = User(hash=sh, originalfiles={},convertedfiles={})
            user.save()
        user = User.objects(hash=sh).get()
        current_origfiles = user.originalfiles
        current_origfiles[filename] = content
        user.update(originalfiles=current_origfiles)
        user.reload()
        #send data to worker
        channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        #send message back to client    
        response = {'hash': sh}
        response_pickled = jsonpickle.encode(response)
        connection.close()
        return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route("/download/<hash>")
def download(hash):
    user = User.objects(hash=hash).get_or_404()
    convfiles = user.to_mongo().to_dict()['convertedfiles'] 
    print(convfiles)
    if not convfiles:
        response = {'status': "Your files haven't been processed yet."}
    else:
        response = convfiles
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")



# start flask app
app.run(host="0.0.0.0", port=5000) #, debug = True



