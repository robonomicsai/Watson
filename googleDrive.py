from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def createFile(fileName,messageString):

        gauth = GoogleAuth()
        gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.

        drive = GoogleDrive(gauth)

        file1 = drive.CreateFile({'title': fileName})  # Create GoogleDriveFile instance with title 'Hello.txt'.
        file1.SetContentString(messageString) # Set content of the file from given string.
        file1.Upload()



if __name__ == '__main__':
    createFile("Test.txt","Content is written using Python and Google Drive API")
