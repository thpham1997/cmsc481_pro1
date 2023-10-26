from socket import *
import time, json

# items for database are notes
# note includes: {id: unique number not null, noter_name: string not null, note: string not null, date_created: date not null}
# Socket sends end in with the token unless for login
ssock = None
tokens = None
dictionary = {"status":"", "token:":""}
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
  ssock.send('LOGIN'+ id)  # send a message to server with id
   #make sure the server sends the data in this order
  data = json.loads(dictionary)# make a json format from a dict
  data = ssock.recv(4096) # message contains token and status
  status = data["status"]  # extract status and token
  token = data["token"]
  # status, token = contact the server
  return status, token

# PHASE 2
def performAction(action, token):
  status = None
  message = None #response message
  ssock.send(action+" "+token)# send message with action, space used as delimiter
  return status,message # return status, message

def logout(token):
  status = None
  message = None
  ssock.send(ACTIONS[1]+" "+token)
  return status,message# return status, message
  
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
  ssock.send(ACTIONS[4]+" "+noteId+" "+token)# send a message to server to delete note
  # return status, message for that status
  



# the rest is the driver code client
  
  if __name__ == '__main__':
    try:
      openConnection()
    except socket.error:
      print("Hostname not resolved")
      exit()
    keyword= ''
    keyword = input("Enter ID") #PHASE 1
    status,tokens =  loginByID(keyword)
    if status != None:
      print("Login successful")
    while keyword.upper() != ACTIONS(1):#PHASE 2
      pass
    logout(tokens)  #PHASE 3
    closeConnection()