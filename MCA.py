import os
import sys
import json
import time

import urllib.request as req
import string


def CheckMCA(recipient_id,companyName):

    apikey='0563d38dda3db13a142c168c55ef9630'

    #replace the "spaces" in the companyName with "%20"
    companyNameinURL = companyName.replace(" ","%20")

    #the data set link
    datasetlink = 'https://data.gov.in/api/datastore/resource.json?resource_id='

    #create a list of all the resource id 
    full_resource_array = ['d1ac29db-549d-44b2-9bea-28d6e449ff85',
                 '3f328009-8f64-426d-9228-750a3fe8e326',
                 '071758ef-8b2b-4ff6-8774-bcf782214779',
                 'ccd42a4e-b657-4244-a43f-a203e3cf7dd8',
                 'f8547c08-a7bf-4e85-b179-c57b5bd135a8',
                 '74a2d302-e24f-42cf-b95c-ff279bcf133d',
                 'a1513fa4-007e-4085-a367-7a65562e9bf4',
                 '997ad190-4308-4d8e-808c-8148c2c9ed08',
                 'f4a928ea-757e-462c-957e-f783f6cfc206',
                 '3bac7cea-66b4-49b0-b310-4cd730e28287',
                 '133dd8f2-44b3-4a6d-a208-72b1030c51fb',
                 '73d8110b-4492-48b5-9f8b-b5bf2ce65261',
                 '44486d32-3c20-41f4-9376-9f4ac360eaa1',
                 '57ae016f-b67f-42dc-b473-2fdae3621f3b',
                 '76fdab68-795b-42f4-bc6d-188442b3ff57',
                 '6a6e802c-66e2-47c2-ad20-4abc9289c85b',
                 'f526be27-c0bf-4d99-b931-0f8e247e59d0',
                 '1ea03789-3147-4a39-a85e-22f4ca128689',
                 'fc0730f1-9736-409d-b3d8-0ac64122c225',
                 'da1e82e7-fb09-48b3-96cb-8fd0411d4ee6',
                 'f8dd5590-8843-49be-9ae2-79c5b3e23ed0',
                 'b4eb9d9b-c8e7-4ec3-b564-e6a018f7249e',
                 '080e668f-1e57-4376-8269-b41ca9c39cc6',
                 '071aa695-4a6e-4bb9-a109-6e9da1329967',
                 '37cb05be-4210-432d-a19a-423ebfe374dd',
                 '4081f64b-6702-46de-b380-d73edf1ca395',
                 '6a0b8194-3e00-4a2b-908e-04470a1f98b3',
                 '7502bd54-2f04-43a5-ae40-437628b0145a',
                 '4dbe5667-7b6b-41d7-82af-211562424d9a',
                 '6a48e198-1b5c-46e6-ad9e-789b231992c1',
                 '8173b4fa-001a-4891-9806-057d87a60fe8',
                 '006e6aff-6108-4bb6-ba60-ecd9b83a5280',
                 '6f1d971f-ea19-4bbe-b956-2568887c1f37',
                 'df73b4ed-2355-4f2e-9392-4b3201bde8b3',
                 'fe6081c0-a880-44b4-9acd-715d73b4032f'
               ]

    resource_array=['f8547c08-a7bf-4e85-b179-c57b5bd135a8',
                    'd1ac29db-549d-44b2-9bea-28d6e449ff85',
                    '73d8110b-4492-48b5-9f8b-b5bf2ce65261',
                    '1ea03789-3147-4a39-a85e-22f4ca128689',
                    '080e668f-1e57-4376-8269-b41ca9c39cc6',
                    '071758ef-8b2b-4ff6-8774-bcf782214779',
                    '006e6aff-6108-4bb6-ba60-ecd9b83a5280',
                    '3f328009-8f64-426d-9228-750a3fe8e326',
                    '7502bd54-2f04-43a5-ae40-437628b0145a'
                    ]

    
    foundFlag="N"
    returnString=companyName

    for eachresourceid in resource_array:
        url = datasetlink + eachresourceid + '&api-key=' + apikey  + '&filters[COMPANYNAME]=' + companyNameinURL
        #print(eachresourceid)
        response = req.urlopen(url)
        returnedJSON = json.loads(response.read().decode())
        for r in returnedJSON['records']:
            if companyName in  r['COMPANYNAME']:
                #print ('REGISTERED OFFICE ADDRESS')
                #print (r['REGISTEREDOFFICEADDRESS'])
                #print ('AUTHORIZED CAPITAL')
                #print (r['AUTHORIZEDCAPITAL'])
                #print ('LICENSE NUMBER')
                #print (r['CORPORATEIDENTIFICATIONNUMBER'])
                returnString = "Company Name :" + r['COMPANYNAME'] + "\n"
                returnString = returnString + "Company ID : " +r['CORPORATEIDENTIFICATIONNUMBER']+ "\n"
                returnString = returnString + "Office Address : " + r['REGISTEREDOFFICEADDRESS']+ "\n"
                returnString = returnString + "Authorized Capital : " +r['AUTHORIZEDCAPITAL']+ "\n"
                print(returnString)
                foundFlag="Y"
                

        print(eachresourceid)
        if foundFlag == "Y":
            break


    if foundFlag=="N":
        returnString = "Information of Company " + returnString + " not available"

    return returnString
        
    


if __name__ == '__main__':
    start_time = time.time()
    returnMsg = CheckMCA("12345678","SATNA PLANTATION PRIVATE LIMITED")
    elapsed_time = time.time() - start_time
    print("In Main " + returnMsg)
    print(elapsed_time)
                         
