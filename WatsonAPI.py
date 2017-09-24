import json
import configparser
from os.path import join, dirname
import string
import urllib
import cloudconvert 

import requests
import codecs
import sys, time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from convertAudioVideo import ffmpegconvert

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 as features

from watson_developer_cloud import TextToSpeechV1
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud import VisualRecognitionV3


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

def call_visionapi(imageurl):
    Config=configparser.ConfigParser()
    Config.read("watson.ini")
    apikey=ConfigSectionMap(Config,"Visual Recognition-RAI")['api_key']
    visual_recognition = VisualRecognitionV3('2016-05-20', api_key= apikey)

    try:
        face_result = visual_recognition.detect_faces(images_url=imageurl)

        #face_path = join(dirname(__file__), imageFile)
        #with open(face_path, 'rb') as image_file:
            #face_result = visual_recognition.detect_faces(images_file=image_file)

        #print(json.dumps(face_result, indent=2))
        try:
            NumOfPeople=len(face_result["images"][0]["faces"])
            MALE_COUNT=0
            FEMALE_COUNT=0
            for i in range(0,NumOfPeople):
                if face_result["images"][0]["faces"][i]["gender"]["gender"] == "MALE":
                    MALE_COUNT=MALE_COUNT+1
                elif face_result["images"][0]["faces"][i]["gender"]["gender"] == "FEMALE":
                    FEMALE_COUNT=FEMALE_COUNT+1
            else:
                pass

            print("Number of People in Image : " + str(NumOfPeople))
            print("Number of Male in Image : " + str(MALE_COUNT))
            print("Number of Female in Image : " + str(FEMALE_COUNT))
            return NumOfPeople,MALE_COUNT,FEMALE_COUNT
        except:
            print("Can't find people in Image")
            return 0,0,0
        
    except:
        return
    

def call_nlgu(text_stmt):
    Config=configparser.ConfigParser()
    Config.read("watson.ini")
    userid=ConfigSectionMap(Config,"Natural Language Understanding-RAI")['username']
    pwd=ConfigSectionMap(Config,"Natural Language Understanding-RAI")['password']

    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2017-02-27',username=userid,password=pwd)
    response = natural_language_understanding.analyze(text=text_stmt,features=[features.Entities(), features.Keywords()])
    try:
        print(json.dumps(response, indent=2))
    except:
        return

def call_text2speech(text_stmt):
    Config=configparser.ConfigParser()
    Config.read("watson.ini")
    userid=ConfigSectionMap(Config,"Text to Speech-RAI")['username']
    pwd=ConfigSectionMap(Config,"Text to Speech-RAI")['password']

    text_to_speech = TextToSpeechV1(username=userid,password=pwd,x_watson_learning_opt_out=True)  # Optional flag
    #print(json.dumps(text_to_speech.voices(), indent=2))

    try:
        with open(join(dirname(__file__), 'output.wav'),'wb') as audio_file:
            audio_file.write(text_to_speech.synthesize(text_stmt, accept='audio/wav',voice="en-US_AllisonVoice"))

        print(json.dumps(text_to_speech.pronunciation('Watson', pronunciation_format='spr'), indent=2))
        #print(json.dumps(text_to_speech.customizations(), indent=2))
    except:
        return

def call_speech2text(audioFileLocation):
    Config=configparser.ConfigParser()
    Config.read("watson.ini")
    userid=ConfigSectionMap(Config,"Speech to Text-RAI")['username']
    pwd=ConfigSectionMap(Config,"Speech to Text-RAI")['password']

    speech_to_text = SpeechToTextV1(username=userid,password=pwd,x_watson_learning_opt_out=False)
    #status = downloadFileandConvert(audioFileLocation)
    status=ffmpegconvert(audioFileLocation,'wav') # Convert to WAV file
    if status == "Not Ok":
        print("Error in File Conversion - In Watson")
        return "Error in File Conversion - In Watson"

    #audioFileLocation=join(dirname(__file__), audioFile)
    #audioFileLocation = audioFile
    speech_to_text.get_model('en-US_NarrowbandModel')
    #speech_to_text.get_custom_model('9c1d00a0-330c-11e7-94ad-3b2269260fbc')

    with open(status,'rb') as audio_file:
        returnedJSON = json.dumps(speech_to_text.recognize(audio_file, content_type='audio/wav', timestamps=True,word_confidence=True,model='en-US_NarrowbandModel',continuous=True),indent=2)
        #print(returnedJSON)
        #Deserialize
        returnedJSONStr = json.loads(returnedJSON)
        print(returnedJSONStr)
        try:
            returnMsg=returnedJSONStr['results'][0]['alternatives'][0]['transcript']
            print(returnedJSONStr['results'][0]['alternatives'][0]['transcript'])
            return returnMsg
        except:
            return "Can't Convert Speech2Text"


def downloadFileandConvert(audioFileLocation):
    urllib.request.urlretrieve(audioFileLocation,'audioclip.aac')
    try:
        api = cloudconvert.Api('5wYY-t4lBPaS82pOFHCGuNvNeXEUBfrEkcLKTN7Pz3IFRc_T7IQ7_VHHsBVbv07AJihdRKP3tv96fFhc5il8Sw')
        process = api.convert({"inputformat": "aac","outputformat": "wav","input": "upload","converteroptions": { "audio_frequency": "16000"},"file": open('audioclip.aac', 'rb')})
        process.wait()
        process.download()
    except:
        return "Not Ok"

def CreateSTTCustomModel(modelName,description):
    ##########################################################################
    # Step 1: Create a custom model
    # Change "name" and "description" to suit your own model
    ##########################################################################
    Config=configparser.ConfigParser()
    Config.read("watson.ini")
    userid=ConfigSectionMap(Config,"Speech to Text-ph")['username']
    pwd=ConfigSectionMap(Config,"Speech to Text-ph")['password']

    print ("\nCreating custom mmodel...")
    data = {"name" : modelName, "base_model_name" : "en-US_BroadbandModel", "description" : description}
    uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/customizations"
    headers = {'Content-Type' : "application/json"}
    jsonObject = json.dumps(data).encode('utf-8')
    resp = requests.post(uri, auth=(userid,pwd), verify=False, headers=headers, data=jsonObject)
    print ("Model creation returns: " + str(resp.status_code))

    if resp.status_code != 201:
        print("Failed to create model")
        print(resp.text)
        sys.exit(-1)

    respJson = resp.json()
    customID = respJson['customization_id']
    print("Model customization_id: ", customID)

if __name__ == '__main__':
    text_stmt='I am attaching an updated version of our previous deck, with actual drone images and software screenshots included. As elaborated, our drone partner is an Ex-Royal Australian Air Force Engineer based in Melbourne and our AI / ML partner is a scientist at the European Space Agency in the Netherlands'
    print("==========NGLU==========")
    #call_nlgu(text_stmt)
    print("==========Text2Speech==========")
    #call_text2speech(text_stmt)
    print("==========Speech2Text==========")
    #audioFileLocation="https://cdn.fbsbx.com/v/t59.3654-21/18281921_1418297234880701_6984337424318988288_n.aac/audioclip-1495368234680-2619.aac?oh=6286f0d92df47a8d16257aeb08986a80&oe=5923E620"
    #text_stmt=call_speech2text(audioFileLocation)
    #print(text_stmt)
    #CreateSTTCustomModel("Custom model #2","STT custom model")
    #result=call_visionapi("https://www.oscars.org/sites/oscars/files/1998_02_sound_rydstrom_summers_nelson_judkins_presenter_huston.jpg")
