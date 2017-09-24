import ffmpy
import urllib
import os
import requests

def ffmpegconvert(AVFileLocation,outputExtn):
    InputFileName=AVFileLocation.split("?")[0].split("/")[6] # Split and get FileName from URL
    outputFileName=InputFileName.split(".")[0] + "." + outputExtn # Output is different extension
    
    try:
        urllib.request.urlretrieve(AVFileLocation,InputFileName)
        print("File Downloaded")
    except:
        print("Error in File Download")
        return "Not Ok"

    try:
        ff = ffmpy.FFmpeg(inputs={InputFileName: None},outputs={outputFileName: None},global_options={'-y'})    
        ff.run()
        return outputFileName
    except:
        print("Error in File Conversion in Convert")
        return "Not Ok"


if __name__ == '__main__':
    AVFileLocation='https://cdn.fbsbx.com/v/t59.3654-21/20688808_1497728923604198_4861713064208105472_n.aac/audioclip-1502410742229-2938.aac?oh=b23000ee3d0691c53c62ee513a48f725&oe=598F6510'
    returnMsg = ffmpegconvert(AVFileLocation,'wav')
    print(returnMsg)
