from base64 import b64encode
from os import makedirs
from os.path import join, basename
from sys import argv
import json
import urllib
import requests

from RAIPython import downloadFile
from RAIPython import parseArrayOCR

# Note Moved downloadFile function to RAIPython

def ExtractText(ImageFileLocation) :
    image_filename=downloadFile(ImageFileLocation)
    #APIKey = 'AIzaSyDuDYAxdOqpUWot4yMxE0mtyVMmlpf0uvc' # RobonomicsAI API Key
    
    with open(image_filename, 'rb') as f:
        ctxt = b64encode(f.read()).decode()
        image =  [ { "image": { "content": ctxt }, "features": [ { "type": "TEXT_DETECTION" } ] } ]
        image1 = json.dumps({"requests": image }).encode()
        response = requests.post('https://vision.googleapis.com/v1/images:annotate',
                           data=image1,
                           params={'key': 'AIzaSyCmpcg1XoyRk9riyaPWNJf_AtcWzWeAbjE'},
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
                
        return parseArrayOCR(returnArray,returnString)

                
if __name__ == '__main__':
    returnArray=ExtractText("https://scontent-sea1-1.xx.fbcdn.net/v/t34.0-12/20751455_1497809830262774_1107732524_n.jpg?_nc_ad=z-m&oh=a865490ac5fa8a9b013d06149320ce9f&oe=59901CD8")
    print(list(returnArray))
    
    
