#!/usr/bin/env python3

import requests
import json
import sys, os
import shutil
import secrets

def upload(folder, addr):
    url = addr + '/upload'
    token = secrets.token_hex(16)

    for filename in os.listdir(folder):
        if filename.endswith('.txt'):
            f = open(folder + '/' + filename, 'r').read()
            data = {"token":token, "filename":filename,"content":f}
            response = requests.post(url, json=data)
    print("Response is", response)
    print(json.loads(response.text))

def download(hash, addr, output, debug=False):
    dir = output
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

    url = addr + '/download/'+ hash
    response = requests.get(url)
    files = json.loads(response.text)
    if len(files) == 1:
        print(json.loads(response.text))
    else:
        for filename, content in files.items():
            filename = filename.split('.')[0]
            with open(output + '/' + filename + '.tsv', 'w') as f:
                f.write(content)
        print('Your converted files have been downloaded to the output folder.')

    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))


host = sys.argv[1]
cmd = sys.argv[2]

addr = 'http://{}'.format(host)

if cmd == 'upload':
    filedir = sys.argv[3]
    upload(filedir, addr)
elif cmd == 'download':
    hash = sys.argv[3]
    output = sys.argv[4]
    download(hash, addr, output, debug = False)

