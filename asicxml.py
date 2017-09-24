import os
import sys
import json

import urllib.request as req
import xmltodict
import string


def CheckABN(recipient_id,ABN):
    searchString = ABN
    includeHistoricalDetails = 'Y'
    authenticationGuid = 'd6bc9073-79a3-458d-8199-247c592b4fc3'		#Your GUID should go here

    conn = req.urlopen('http://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/' + 
					'SearchByABNv201408?searchString=' + searchString + 
					'&includeHistoricalDetails=' + includeHistoricalDetails  +
					'&authenticationGuid=' + authenticationGuid)
					
    #XML is returned by the webservice
    #Put returned xml into variable 'returnedXML' 
    returnedXML = conn.read()
    d = xmltodict.parse(returnedXML, xml_attribs=True)
    returnedJSON = json.dumps(d, indent=4)

    #Deserialize
    returnedJSONStr = json.loads(returnedJSON)

# Check 
    if 'entityStatusCode' in returnedJSON:
        print("ABN " + searchString + " is Active")
        message_text = "ABN " + searchString + " is Active"
    else:
        print("ABN " + searchString + " is not Active")
        message_text = "ABN " + searchString + " is not Active"
        organisationName = ""

# get mainName or MainTradingName        
    if 'mainName' in returnedJSON:
        mainName = returnedJSONStr['ABRPayloadSearchResults']['response']['businessEntity201408']['mainName']
        if type(mainName) is dict:
            print(returnedJSONStr['ABRPayloadSearchResults']['response']['businessEntity201408']['mainName']['organisationName'])
            organisationName=returnedJSONStr['ABRPayloadSearchResults']['response']['businessEntity201408']['mainName']['organisationName']
        elif type(mainName) is list:
            print(returnedJSONStr['ABRPayloadSearchResults']['response']['businessEntity201408']['mainName'][0]['organisationName'])
            organisationName=returnedJSONStr['ABRPayloadSearchResults']['response']['businessEntity201408']['mainName'][0]['organisationName']            
    elif 'mainTradingName' in returnedJSON:
        mainTradingName = returnedJSONStr['ABRPayloadSearchResults']['response']['businessEntity201408']['mainTradingName']
        if type(mainTradingName) is dict:
            print(returnedJSONStr['ABRPayloadSearchResults']['response']['businessEntity201408']['mainTradingName']['organisationName'])
            organisationName=returnedJSONStr['ABRPayloadSearchResults']['response']['businessEntity201408']['mainTradingName']['organisationName']
        elif type(mainTradingName) is list:
            print(returnedJSONStr['ABRPayloadSearchResults']['response']['businessEntity201408']['mainTradingName'][0]['organisationName'])
            organisationName=returnedJSONStr['ABRPayloadSearchResults']['response']['businessEntity201408']['mainTradingName'][0]['organisationName']


    if organisationName != "" :
        message_text = message_text + " and Organisation Name is " + organisationName

    #print(returnedXML)
    #print(returnedJSON)
    #print(returnedJSONStr)

    print (message_text)
    return message_text

if __name__ == '__main__':
    CheckABN("123456789","94123230240")

