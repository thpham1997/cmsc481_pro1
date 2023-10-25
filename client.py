from socket import *
import time, json

# items for database are notes
# note includes: {id: unique number not null, noter_name: string not null, note: string not null, date_created: date not null}

ssock = None
tokens = None

recvbufsize = 1024

ACTIONS = ('LOGIN', 'LOGOUT', 'ADD', 'RETRIEVE', 'DELETE', 'CANCEL')

def openConnection():
  serverName = "need to modify" # enter correct server address
  serverPort = 5856
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
      
      
# PHASE 1
def loginByID(id):
  status = None
  token = None 
  # send a message to server with id
  # make a json format from a dict
  # message contains token and status
  # extract status and token
  # status, token = contact the server
  return status, token

# PHASE 2
def performAction(action, token):
  status = None
  message = None #response message
  # send message with action
  # return status, message
def logout(token):
  status = None
  message = None
  # return status, message
  
def retrieve(noteId, token):
  status = None
  message = None # response message
  # send a message to server to retrieve a note or a list of note
  # return status, notes/note
  
def add(noteName, noteMessage, token):
  status = None
  message = None # response message
  # send a message to server to add note
  # return status, message for that status
  
def delete(noteId, token):
  status = None
  message = None # response message
  # send a message to server to delete note
  # return status, message for that status
  



# the rest is the driver code client
  
  