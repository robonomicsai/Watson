import json
import configparser
from os.path import join, dirname
import string
import urllib

from base64 import b64encode
from os import makedirs
from sys import argv
import json

import requests
import codecs
import sys, time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from convertAudioVideo import ffmpegconvert

from RAIPython import downloadFile
from RAIPython import parseArrayOCR

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



def ConfigSectionMap(Config,section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def call_visionapi(imageurl,purpose):
    Config=configparser.ConfigParser()
    Config.read("google.ini")
    apikey=ConfigSectionMap(Config,"googleVision-RAI")['api_key']

    try:
        image_filename=downloadFile(imageurl)
        print(image_filename)
    except:
        return "Can't download file"

    if purpose == 'TEXT_DETECTION':
        with open(image_filename, 'rb') as f:
            ctxt = b64encode(f.read()).decode()
            image =  [ { "image": { "content": ctxt }, "features": [ { "type": "TEXT_DETECTION" } ] } ]
            image1 = json.dumps({"requests": image }).encode()
            response = requests.post('https://vision.googleapis.com/v1/images:annotate',
                           data=image1,
                           params={'key': apikey},
                           headers={'Content-Type': 'application/json'})

            returnString=""

            if response.status_code != 200 or response.json().get('error'):
                print(response.text)
            else:
                for resp in response.json()['responses']:
                    try:
                        returnString = resp['textAnnotations'][0]['description']
                        returnArray=returnString.replace('\n','*').split("*")
                        returnString=returnString.replace('\n',' ')
                        print(returnArray)
                    except:
                        returnArray=["",""]  # Minimum 2 Elements are required because it is required in parseArray
                        returnString="Sorry even I could not read your handwriting!"
                        print(returnString)
                
        return parseArrayOCR(returnArray,returnString)
    

if __name__ == '__main__':
    imageurl='https://scontent-sea1-1.xx.fbcdn.net/v/t34.0-12/20751455_1497809830262774_1107732524_n.jpg?_nc_ad=z-m&oh=a865490ac5fa8a9b013d06149320ce9f&oe=59901CD8'
    purpose='TEXT_DETECTION'
    print(call_visionapi(imageurl,purpose))
