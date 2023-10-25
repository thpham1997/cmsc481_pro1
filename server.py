from socket import *
import time, json

ssock = None

def openConnection():
  serverName = "need to modify" # enter correct server address
  serverPort = 5856
  recvbufsize = 1024
  ssock = socket(AF_INET, SOCK_STREAM)
  ssock.connect((serverName, serverPort))
  ssock.setblocking(0)
  
  
def closeConnection():
  if ssock != None:
    try:
      ssock.close()
      ssock = None
    except Exception as e:
      print("ERROR: " + e)
      
      
      
def loginByID(id):
  status = "SUCCESS"
  token = "abc"
  
  return status, token