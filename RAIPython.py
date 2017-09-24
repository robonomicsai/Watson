import string
from base64 import b64encode
from os import makedirs
from os.path import join, basename
from sys import argv
import json
import urllib
import requests


from stop_words import get_stop_words
 

def word_tokenize(myText):
    mywordList=myText.split()
    return mywordList

def extractIntent(myText):
    mywordList = word_tokenize(myText)

    stop_words = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although",
                  "always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around",
                  "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides",
                  "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe",
                  "detail", "do", "done", "down", "due", "during", "each", "eg", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever",
                  "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "fire", "first", "for", "former", "formerly",
                  "forty", "found", "from", "front", "full", "further", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
                  "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest",
                  "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill",
                  "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next",
                  "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "only", "onto", "or", "other",
                  "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem",
                  "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "sixty", "so", "some", "somehow", "someone",
                  "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "than", "that", "the", "their", "them", "themselves", "then",
                  "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though",
                  "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "un", "under", "until",
                  "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby",
                  "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within",
                  "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]

    #stop_words = get_stop_words('en')
    newstop_words = []
    for stop_word in stop_words:
        newstop_words.append(stop_word.upper())

    #print(newstop_words)
    wordsFiltered = []

    for w in mywordList:
        if w.upper() not in newstop_words:
            wordsFiltered.append(w)
 
    returnString=" ".join(wordsFiltered)
    #print(returnString)
    return returnString


def removePunctuation(myText):
    translator = str.maketrans('', '', string.punctuation)
    myText=myText.translate(translator)
    return myText

    
def similarIntent(myText):
    myText=removePunctuation(myText)
    myword = extractIntent(myText)
    myIntentList = [
            ['Check ABN', 'Find ABN', 'Get ABN Details'],
            ['Check MCA', 'Find Company', 'Get Company Details','Check Company Details','Find Company details','Company Details'],
            ['Nearby', 'Closeby','nearby places','Next door','find nearby places','find nearby'],
            ['Thank You', 'Great Job', 'Great', 'Thank','Thanks','Thank U','Awesome'],
            ['OCR','Text Extract','Extract Text','Scan Text','Text Scan','scan text image','extract information image']
            ]
    
    foundFlag="N"
    returnString=myword # Return original string if not found
    for item in myIntentList:
        for itemList in item:
            if itemList.upper() == myword.upper():
                print ('Available')
                returnString = item[0].upper()
                print(returnString)
                foundFlag="Y"

            if foundFlag=="Y":
                break

    return returnString

def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

#print(text2int("seven billion one hundred million thirty one thousand three hundred thirty seven"))

def searchIntentInList(inputText):
    knownIntentList = ['Check ABN','Check MCA','Nearby','OCR','Thank You']
    foundFlag="N"
    returnString=""
    
    for itemList in knownIntentList:
        if inputText.upper() == itemList.upper():
            returnString = inputText.upper()
            foundFlag="Y"

        if foundFlag=="Y":
            break
        
    return returnString

def downloadFile(ImageFileLocation):
    InputFileName=ImageFileLocation.split("?")[0].split("/")[5] # Split and get FileName from URL

    try:
        urllib.request.urlretrieve(ImageFileLocation,InputFileName)
        print("File Downloaded")
    except:
        print("Error in File Download")
        InputFileName=""
        return "Not Ok"

    return InputFileName

def parseArrayOCR(myArray,returnString):
    if (myArray[0].upper()=='DRIVER LICENCE' and myArray[1].upper()=='NEW SOUTH WALES, AUSTRALIA' and len(myArray) >= 15):
        Name=myArray[2]
        Address=myArray[5]+ " " + myArray[6]
        LicenseNo=myArray[8]
        DateOfBirth=myArray[13]
        LicenseExpiryDate=myArray[15]
        return "1",Name,Address,LicenseNo,LicenseExpiryDate,returnString  # Return Tupple Object
    elif (myArray[0].upper()=='FORM - 7' and len(myArray) >= 17):
        Name=myArray[2]
        Address=myArray[17]
        LicenseNo=myArray[1]
        DateOfBirth=myArray[13]
        LicenseExpiryDate=myArray[8]
        #print(myArray[13])
        return "1",Name,Address,LicenseNo,LicenseExpiryDate,returnString # Return Tupple Object
    else:
        return "2","","","","",returnString

    
if __name__ == '__main__':
    inputString = "CHECK BAN"
    print(searchStringInList(inputString))
