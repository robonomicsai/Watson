import os
import sys
import json

import urllib.request as req
import xmltodict
import string


def GooglePlace(lat,lng,radius,keyword):
  #making the url
  if keyword == "ok":
    keyword == "attraction"
  LOCATION = str(lat) + "," + str(lng)
  RADIUS = radius
  KEYWORD = keyword.replace(" ", "%20")
  AUTH_KEY = 'AIzaSyANg11eNLs3QH_U4THqox-OMzM-8s-j1XA'
  MyUrl = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json'
           '?location=%s'
           '&radius=%s'
           '&keyword=%s'
           '&key=%s') % (LOCATION, RADIUS, KEYWORD, AUTH_KEY)

  print(MyUrl)
  
  #Open a network object denoted by a URL for reading
  response = req.urlopen(MyUrl)
  
  # Get data stream from a socket
  jsonRaw = response.read()

  # Deserialize JSON Object to Python Object
  jsonDataStr = json.loads(jsonRaw)
  resultLength = len(jsonDataStr["results"])
  
  myList = [{}]

  # Check number of item in List
  if resultLength == 0:
    return
  elif resultLength > 4:
    numofitem = 4
  else :
    numofitem = resultLength

  print("numofitem :" + str(numofitem))
  
  for index in range(numofitem):
    try:
      #print(str(jsonDataStr["results"][index]["name"]))
      #print ("vicinity :" + str(jsonDataStr["results"][index]["vicinity"]))
      #myList.append("title: " + str(jsonDataStr["results"][index]["name"]))

      #print(index)
      myList.insert(index,{"title":jsonDataStr["results"][index]["name"],"subtitle":jsonDataStr["results"][index]["vicinity"]})
    except KeyError:
      #print ("Rating : Not Available")
      pass

  # Delete last item 
  myList.pop()
  
  #print(myList)
  return (myList)

if __name__ == '__main__':
    GooglePlace(-33.698421303985,150.9166456471,50000,"Dan Murphy")
    
