import os
import sys
import json
import os.path
import configparser
import string
from random import randrange
import wikipedia

from flask import jsonify
from flask import Flask, request

from RAIPython import word_tokenize
from RAIPython import extractIntent
from RAIPython import removePunctuation
from RAIPython import similarIntent
from RAIPython import searchIntentInList

from asic import CheckABN
from OCRTextExtract import ExtractText
from googlePlace import GooglePlace
from googleDrive import createFile

from WatsonAPI import call_speech2text
from WatsonAPI import call_visionapi

from MCA import CheckMCA

import ffmpy
import urllib.request as req
import requests
import xmltodict
import string
from sys import exit


app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    saveString = ["REMEMBER","SAVE","MEMORISE","MEMORIZE"]
    recallString = ["RECALL", "REMIND"]
    deleteString = ["DELETE","THRASH","BIN"]
    
    # endpoint for processing incoming messaging events
    
    data = request.get_json()
    print("In Webhook")
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    
    if data["object"] == "page":

        for entry in data["entry"]:

            app_id = entry["id"]

            for messaging_event in entry["messaging"]:
                
                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

                    for messageinfo in messaging_event["message"]:
                        if 'text' in messageinfo:
                            message_text = messaging_event["message"]["text"]  # the message's text

                            if message_text == "Try Again":
                                break                            

                            # Read Last Saved Intent
                            subject = readFile(app_id,sender_id)
                            subject = subject.upper()
                            print("Intent is :"+ subject)

                            if subject == "CHECK ABN":
                                message_text = "CHECK ABN " + message_text
                            elif subject == "CHECK MCA":
                                message_text = "CHECK MCA " + message_text
                            elif subject == "OCR":
                                message_text = "OCR " + message_text
                            elif subject == "NEARBY":
                                message_text = "NEARBY " + message_text
                            else:
                                message_text = similarIntent(message_text)  # If there is no Intent

                            print (message_text)


                            if message_text.upper().strip().startswith("CHECK ABN"):
                                MyWordList = [word.strip(string.punctuation) for word in message_text.upper().split()]
                                if len(MyWordList) > 2:
                                    #ABN=MyWordList[2]
                                    ABN=''.join(MyWordList[2:])
                                    #print(ABN)
                                    msg_to_sender = CheckABN(sender_id, ABN)
                                    writeFile(app_id,sender_id,"ok") # Write Intent
                                    sendMessageJson(sender_id,msg_to_sender)
                                else:
                                    #print("Sending Message. ABN Number is Missing")
                                    #msg_to_sender="ABN Number is Missing. Please Type Check ABN 123456789"
                                    writeFile(app_id,sender_id,"CHECK ABN") # Write Intent
                                    msg_to_sender="Please advise ABN"
                                    sendMessageJson(sender_id,msg_to_sender)
                                    
                            elif message_text.upper().strip().startswith("THANK"):
                                writeFile(app_id,sender_id,"ok") # Write Intent
                                welcomeMessage = ['No Problem', 'You are welcome', 'I am glad that I was able to help you', 'I am glad to be your service']
                                random_index = randrange(0,len(welcomeMessage)) 
                                msg_to_sender=welcomeMessage[random_index]
                                sendMessageJson(sender_id,msg_to_sender)

                            elif message_text.upper().strip().startswith("OCR"):
                                writeFile(app_id,sender_id,"OCR") # Write Intent
                                msg_to_sender="Please send image"
                                sendMessageJson(sender_id,msg_to_sender)

                            elif message_text.upper().strip().startswith("CHECK MCA"):
                                MyWordList = [word.strip(string.punctuation) for word in message_text.upper().split()]
                                if len(MyWordList) > 2:
                                    #COMPANY=MyWordList[2]
                                    COMPANY=' '.join(MyWordList[2:])
                                    #print(COMPANY)
                                    try:
                                        msg_to_sender = CheckMCA(sender_id, COMPANY.upper())
                                        writeFile(app_id,sender_id,"ok") # Write Intent
                                        sendMessageJson(sender_id,msg_to_sender)
                                    except:
                                        sendMessageJson(sender_id,"Can't find information of " + COMPANY.upper() + " Reason : Timeout")
                                else:
                                    #print("Sending Message. Company Name is Missing")
                                    #msg_to_sender="Company Name is Missing. Please Type Check MCA ROBONOMICSAI PTY LTD"
                                    writeFile(app_id,sender_id,"CHECK MCA") # Write Intent
                                    msg_to_sender="Please advise Company Name"
                                    sendMessageJson(sender_id,msg_to_sender)
                                    
                            elif message_text.upper().strip().startswith("NEARBY"):

                                MyWordList = [word.strip(string.punctuation) for word in message_text.upper().split()] # Convert to List
                                
                                if len(MyWordList) > 2:
                                    if MyWordList[0] == "NEARBY" and MyWordList[1] == "PLACES":
                                        keyword=' '.join(MyWordList[2:]) # Combine keywords
                                        writeFile(app_id,sender_id,keyword) # Write Intent
                                        sendLocation(sender_id,"Please share your location:")
                                    else:
                                        keyword=' '.join(MyWordList[1:]) # Combine keywords
                                        writeFile(app_id,sender_id,keyword) # Write Intent
                                        sendLocation(sender_id,"Please share your location:")
                                elif len(MyWordList) == 2:
                                    if MyWordList[0] == "NEARBY" and MyWordList[1] == "PLACES":
                                        keyword = "NEARBY"
                                        writeFile(app_id,sender_id,keyword) # Write Intent
                                        sendMessageJson(sender_id,"What do you want to find?")
                                        #sendLocation(sender_id,"Please share your location:")
                                    elif MyWordList[0] == "NEARBY" and MyWordList[1] != "PLACES":
                                        keyword = MyWordList[1]
                                        writeFile(app_id,sender_id,keyword) # Write Intent
                                        sendLocation(sender_id,"Please share your location:")
                                        #findIntent(app_id,sender_id)
                                else:
                                    writeFile(app_id,sender_id,"NEARBY") # Write Intent
                                    sendMessageJson(sender_id,"What do you want to find?")
                                
                            elif "CONTACT RAI" in message_text.upper():
                                callback(sender_id, message_text)

                            else:
                                if app_id == sender_id:
                                    pass
                                
                                else:

                                    MyWordList = [word.strip(string.punctuation) for word in message_text.split()] # Convert to List
                                    
                                    # Save, Recall & Delete
                                    print(MyWordList)
                                    if len(MyWordList)  > 1:
                                        if MyWordList[0].upper() in saveString:
                                            keyword=' '.join(MyWordList[1:]) # Combine keywords
                                            appendFile(app_id,"RAIBotHistory.txt",keyword) # Write to file
                                            appendFile(app_id,"RAIBotHistory.txt","\n") # append new line to file
                                            sendMessageJson(sender_id,"Message Saved")
                                        elif MyWordList[0].upper() in recallString:
                                            subject = readFile(app_id,"RAIBotHistory.txt")
                                            sendMessageJson(sender_id,subject)
                                        elif MyWordList[0].upper() in deleteString:
                                            writeFile(app_id,"RAIBotHistory.txt","")
                                            sendMessageJson(sender_id,"History Deleted")
                                        else:
                                            findIntent(app_id,sender_id)

                                    elif len(MyWordList)  == 1 :
                                        if MyWordList[0].upper() in recallString:
                                            subject = readFile(app_id,"RAIBotHistory.txt")
                                            sendMessageJson(sender_id,subject)
                                        elif MyWordList[0].upper() in deleteString:
                                            writeFile(app_id,"RAIBotHistory.txt","")
                                            sendMessageJson(sender_id,"History Deleted")
                                        else:
                                            findIntent(app_id,sender_id)
                                    else:
                                        findIntent(app_id,sender_id)

                        elif 'attachments' in messageinfo:
                            print("In attachments")
                            subject = readFile(app_id,sender_id)
                            print("Subject is :"+ subject)
                            decodeAttachment(app_id,recipient_id,sender_id,subject,messaging_event)
                                                            
                        else:
                            pass

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    postback_msg = messaging_event["postback"]["payload"] # Message in Payload

                    if "PostToFacebook" in postback_msg:
                        imageurl=postback_msg[15:]
                        print(imageurl)
                        #postToFacebook(sender_id,imageurl,"Post to Facebook")
                        pass

                    elif "PostToTwitter" in postback_msg:
                        imageurl=postback_msg[14:]
                        print(imageurl)
                        #postToTwitter(sender_id,imageurl,"Post to Twitter")
                        pass
                    
                    else:
                        pass

    return "ok", 200


def findIntent(app_id,sender_id):

    print("in findIntent function")
    if app_id != sender_id:
        userName = findUserProfile(sender_id)
        writeFile(app_id,sender_id,"") # Delete any Intent if present
        #message_text = "Welcome!! " + userName + ". I can verify ABN from ASIC, Find Nearby places"
        message_text = "Welcome!! " + userName + ". What would you like to do?"
    else:
        return "ok", 200

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message": {
            "text": message_text
        }
    })

    data1 = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message": {
		"text":message_text,
                "quick_replies":[
                      {
                        "content_type": "text",
                        "title": "Check ABN",
                        "payload": "CHECK ABN"
                      },
                      {
                        "content_type": "text",
                        "title": "Nearby Places",
                        "payload":"NEARBY PLACES"
                      },
                      {
                        "content_type": "text",
                        "title": "Check MCA",
                        "payload": "CHECK MCA"
                      },
                      {
                        "content_type":"text",
                        "title": "Contact RAI",
                        "payload":"Contact RAI Support"
                      }
                ]
        }
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data1)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def confirmText(sender_id,message_text):

    message_text = "Did you say ..." + message_text

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    data = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message": {
            "text": message_text
        }
    })

    data1 = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message": {
		"text":message_text,
                "quick_replies":[
                      {
                        "content_type": "text",
                        "title": "Yes",
                        "payload": "YES"
                      },
                      {
                        "content_type":"text",
                        "title": "No",
                        "payload":"NO"
                      }
                ]
        }
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data1)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

        
def confirmIntent(app_id,sender_id,text_msg,IntentString):

    print("In confirmIntent function")
    if (app_id != sender_id and IntentString==""):
        #IntentString = string.capwords(IntentString)
        IntentString=IntentString.upper()
        if searchIntentInList(IntentString) != "":
            message_text=text_msg
            replymsg=IntentString
            writeFile(app_id,sender_id,"") # Delete Intent
        else:
            message_text="Sorry I didn't understand. I am still learning"
            replymsg="Sorry"
            writeFile(app_id,sender_id,"") # Delete Intent

    elif (app_id != sender_id and IntentString !=""):
        message_text=text_msg
        replymsg=string.capwords(text_msg)
    else:
        return "ok", 200

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    data1 = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message": {
		"text":message_text,
                "quick_replies":[
                      {
                        "content_type": "text",
                        "title": replymsg,
                        "payload": "REPLY"
                      },
                      {
                        "content_type": "text",
                        "title": "Try Again",
                        "payload": "TRY"
                      }
                      
                ]
        }
    })

    
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data1)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

        
def sendMessageJson(recipient_id,message_text):

    if message_text == "":
        message_text = "Sorry!! No message found"
        
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
        

def sendImageJson(recipient_id, message_text,url):

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
		"attachment":{
        		"type":"image",
        		"payload":{
          		"url":url
        		}
      		}	
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def postImage(recipient_id, message_text,url):

    facebook_payload = "PostToFacebook:" + url
    twitter_payload = "PostToTwitter:" + url
    
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
		"attachment":{
        		"type":"template",
        		"payload":{
                            "template_type":"generic",
                            "elements":[
                                {
                                    "title":"RAI welcome you in CeBIT",
                                    "image_url":url,
                                    "buttons":[
                                        {
                                            "type":"postback",
                                            "title":"Facebook",
                                            "payload": facebook_payload
                                        },
                                        {
                                            "type":"postback",
                                            "title":"Twitter",
                                            "payload": twitter_payload
                                        },
                                        {
                                            "type":"postback",
                                            "title":"No. Thanks",
                                            "payload":"NoPost"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
            }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def sendLocation(recipient_id,message_text):

    #log("sending text message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
		"text":message_text,
                "metadata":"Pizza",
                "quick_replies":[
                      {
                        "content_type":"location",
                      }
                ]	
        }
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

    

def sendLocationWithKeyword(recipient_id,subject,lat_long):
    
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
		"text":"Find Pizza",
                "quick_replies":[
                      {
                        "content_type": "text",
                        "title": subject,
                        "payload": lat_long
                      }
                ]	
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

    return

def decodeAttachment(app_id,recipient_id,sender_id,keyword,messaging_event):

    if keyword == "ok":
        keyword = ""
        
    message_attachments = messaging_event["message"]["attachments"]  # the message's attachments
    print("In decodeAttachment, Length is" + str(len(message_attachments)))
    print(message_attachments)
                            
    if 'type' in message_attachments[0]:
        if message_attachments[0]["type"] == "location":
            if 'payload' in message_attachments[0]: # get Attachment
                message_payload = message_attachments[0]["payload"]
                print(message_payload)

                if 'coordinates' in message_payload:
                    lattitude = message_payload["coordinates"]["lat"]
                    longitude = message_payload["coordinates"]["long"]
                    returnList = GooglePlace(lattitude,longitude,50000,keyword)
                    writeFile(app_id,sender_id,"ok") # Write Intent
                    getNearbyElementsJson(sender_id,returnList)
                
                else:
                    pass
            else:
                pass
        elif message_attachments[0]["type"] == "image":
            if 'payload' in message_attachments[0]: # get Attachment
                message_payload = message_attachments[0]["payload"]
                print(message_payload)

                if ('url' in message_payload and keyword == ""):  # Gender Determination Using Watson
                    url=message_payload["url"]
                    Config=configparser.ConfigParser()
                    #postImage(sender_id, "Sending Default Image", url)
                    image_info = call_visionapi(url)
                    NumberOfPeople="Number of People in Image : " + str(image_info[0])
                    NumberOfMale= "Number of Male in Image : " + str(image_info[1])
                    NumberOfFemale= "Number of Female in Image : " + str(image_info[2])
                    writeFile(app_id,sender_id,"ok") # Write Intent
                    sendMessageJson(sender_id,NumberOfPeople)
                    sendMessageJson(sender_id,NumberOfMale)
                    sendMessageJson(sender_id,NumberOfFemale)
                    
                elif ('url' in message_payload and keyword == "OCR"): # OCR using Google
                    url=message_payload["url"]
                    returnArray=ExtractText(url)
                    list_returnArray=list(returnArray) # Convert To List
                    writeFile(app_id,sender_id,"ok") # Write Intent
                    
                    if list_returnArray[0]=="1":
                        msg_to_sender="Name :" + list_returnArray[1] + "\n"
                        msg_to_sender=msg_to_sender + " Address :" + list_returnArray[2] + "\n"
                        msg_to_sender=msg_to_sender + " LicenseNo :" + list_returnArray[3] + "\n"
                        msg_to_sender=msg_to_sender + " LicenseExpiryDate :" + list_returnArray[4]
                        
                    else:
                        msg_to_sender=list_returnArray[5]
                        
                    sendMessageJson(sender_id,msg_to_sender)

                else:
                    pass
            else:
                pass

        elif message_attachments[0]["type"] == "audio":
            lastIntent=keyword.upper()
            print("Last Saved Intet is :" + lastIntent)
            
            if 'payload' in message_attachments[0]: # get Attachment
                message_payload = message_attachments[0]["payload"]
                print(message_payload)

                if 'url' in message_payload:
                    url=message_payload["url"]
                    Config=configparser.ConfigParser()
                    text_msg=""
                    IntentString=""
                    try:
                        text_msg=call_speech2text(url)
                        print(text_msg)
                        
                        if lastIntent == "":
                            IntentString=similarIntent(text_msg)
                        else:
                            IntentString=lastIntent
                            
                        print("IntentString is : " + IntentString)
                    except:
                        text_msg="Unfortunately I was not able to convert audio messages to text"
                        print(text_msg)

                    confirmIntent(app_id,sender_id,text_msg,IntentString)
                else:
                    pass
            else:
                pass

        elif message_attachments[0]["type"] == "video":
            if 'payload' in message_attachments[0]: # get Attachment
                message_payload = message_attachments[0]["payload"]
                print(message_payload)

                if 'url' in message_payload:
                    url=message_payload["url"]
                    Config=configparser.ConfigParser()
                    text_msg=""
                    IntentString=""                    
                    try:
                        text_msg=call_speech2text(url)
                        print(text_msg)
                        
                        if lastIntent == "":
                            IntentString=similarIntent(text_msg)
                        else:
                            IntentString=lastIntent
                            
                        print("IntentString is : " + IntentString)
                    except:
                        text_msg="Unfortunately I was not able to convert video messages to text"
                        print(text_msg)

                    confirmIntent(app_id,sender_id,text_msg,IntentString)
                else:
                    pass
            else:
                pass
            
        else:
            pass
        
    else:
        pass

def askKeyword(recipient_id,lattitude,longitude):

    lat_long = lattitude + "," + longitude
    
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
                "text":"What do you want to search?",
                "metadata":"Pass Lattitude and Longitude"
        }
    })

    
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

    
def callback(recipient_id, message_text):

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
		"attachment":{
                  "type":"template",
                     "payload":{
                        "template_type":"button",
                        "text":"Need further assistance? Talk to a representative",
                        "buttons":[
                           {
                              "type":"phone_number",
                              "title":"Call RAI Helpdesk",
                              "payload":"+61434240250"
                           }
                        ]
                     }
                }	
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)        

def findUserProfile(recipient_id):
    userid = recipient_id
    pageToken='EAADkHnZAUGUIBAJpIoY5p1f4cGgmZBrrOJWkfebei8JZC86GHbvIexf8cYwMpUrOYkHSJUaIF4dzDKJ5w2ZBT4FxZCL30RWqlZAg8XzFEWG97ShACpAUu20U0hoc5sJzZBbv4jfCEXXYBZB6Hy0J0GJIIQMwHaFirnay75PsCzyZBnAZDZD'
    #conn1 = req.urlopen('https://graph.facebook.com/v2.6/'+ userid + '?fields=first_name,last_name&access_token=' + pageToken)
    url = "https://graph.facebook.com/v2.6/"+ recipient_id + "?fields=first_name,last_name&access_token=" + pageToken
    print(url)
    conn1 = req.urlopen(url)
    resultUser = conn1.read()

    #Deserialize
    resultUserStr = json.loads(resultUser)
    firstName=resultUserStr["first_name"]
    lastName=resultUserStr["last_name"]
    fullName = firstName + " " + lastName
    print(fullName)
    return fullName


def getNearbyElementsJson(recipient_id,elements_list):
    
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "list",
                    "top_element_style": "compact",
                     "elements": elements_list
                    }
                }
            }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


        
def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()

def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

def writeFile(app_id,filename,message_text):

    print("in writeFile function")
    if app_id != filename:
        f = open(filename, 'w')
        f.write(message_text)  # python will convert \n to os.linesep
        f.close()  # you can omit in most cases as the destructor will call it
    else:
        pass

def appendFile(app_id,filename,message_text):

    print("in appendFile function")
    if app_id != filename:
        f = open(filename, 'a')
        f.write(message_text)  # python will convert \n to os.linesep
        f.close()  # you can omit in most cases as the destructor will call it
    else:
        pass

def readFile(app_id,filename):

    print("in readFile function")
    if app_id != filename:
        if os.path.isfile(filename):
            filetext = open(filename, "rb").read()
            return filetext.decode("utf-8")
        else:
            return "ok"
    else:
        return "ok"



if __name__ == '__main__':
    app.run(debug=True)
