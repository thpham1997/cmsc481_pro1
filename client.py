from socket import *
import time, json, errno

# items for database are notes
# note includes: {id: unique number not null, noter_name: string not null, note: string not null, date_created: date not null}
# Socket sends end in with the token unless for login
ssock = None
token = None
server_return = {"status":"status message", "token:":"client token","return":"value to return depending on action"}
action = {"action":"LOGIN or other ACTION","param":"userID/noteID/note dict","token":"if token"}
recvbufsize = 1024

ACTIONS = ['LOGIN', 'LOGOUT', 'ADD', 'RETRIEVE', 'DELETE']

def openConnection():
  global ssock
  try:
    ssock = socket(AF_INET, SOCK_STREAM)
    serverName = "127.0.0.1" # enter correct server address
    serverPort = 5856
    # connectedMessage = "Welcome to Note Server"
    ssock.connect((serverName, serverPort))
    ssock.setblocking(0)
  except Exception as e:
    print(e)
  
  
  
def closeConnection():
  global ssock
  global token
  try:
    ssock.close()
    ssock = None
    token = None
    print("\nConnection closed\n")
  except Exception as e:
    print("ERROR: " + e)
      
def receiveServerMessage():
  while True:
    try:
      message = ssock.recv(1024).decode('ascii')
      # print (message)
    except error as e:
      if e.errno == errno.EWOULDBLOCK:
      # all data received, send next data
        return message
      else: # some error occurred
        print("exit")
        ssock.close()
        return json.dumps({"status": "ERROR", "message": "Something went wrong"})

def isSessionExpired(status, message):
  if status == ERROR and message == SESSION_EXPIRED:
    return True
  return False
# PHASE 1
def loginByID(id):
  global token
  # status = None
  # token = None 
  message = {"action":"LOGIN","parameter":id, "token" : ""}
  ssock.send(json.dumps(message).encode())  # send a message to server with id
  time.sleep(0.1)
   #make sure the server sends the data in this order
  # server_return = ssock.recv(1024).decode('ascii') # message contains token and status
  time.sleep(0.1)
  server_return = receiveServerMessage()
  print(server_return)
  data = json.loads(server_return)# make a json format from a dict
  status = data["status"]  # extract status and token
  if status == "SUCCESS":
    token = data["message"] #token is sent as message param 
  message = data["message"]
  return status, message # status, token = contact the server

# PHASE 2


def logout(token):
  status = None
  message = {"action":"LOGOUT","parameter":"", "token" : token} # response message
  ssock.send(json.dumps(message).encode())
  time.sleep(0.1)
  server_return = receiveServerMessage()
  # print(server_return)
  data = json.loads(server_return)
  status = data["status"]  # extract status and token
  message = data["message"] #token is sent as message param 
  # if status == "SUCCESS":
  return status,message# return status, message
  
def retrieve(name, token):
  status = None
  message = {"action":"RETRIEVE","parameter":name, "token": token} # response message
  note = None # note to return, if any
  ssock.send(json.dumps(message).encode())# send a message to server to retrieve a note or a list of note
  # server_return = ssock.recv(1024).decode('ascii') # message contains token and status
  time.sleep(0.1)
  server_return = receiveServerMessage()
  # print(server_return)
  data = json.loads(server_return)# make a json format from a dict
  note = data["message"]
  status = data["status"]
  # return status, notes/note
  return status, note

def add(noteName, noteMessage, token):
  #note format: note1 = {"id": 1, "name": "note1", "note": "this is the note content 1"}
  note = {"name": noteName, "note": noteMessage}
  status = None
  message = {"action":"ADD","parameter": note, "token":token} # response message
  ssock.send(json.dumps(message).encode())# send a message to server to delete note
  # server_return = ssock.recv(1024).decode('ascii') # message contains token and status
  time.sleep(0.1)
  server_return = receiveServerMessage()
  # print(server_return)
  data = json.loads(server_return)# make a json format from a dict
  message = data["message"]
  status = data["status"]
  # send a message to server to add note
  # return status, message for that status
  return status,message
  
def delete(noteName, token):
  status = None
  message = {"action":"DELETE","parameter":noteName, "token":token} # response message
  ssock.send(json.dumps(message).encode())# send a message to server to delete note
  # server_return = ssock.recv(1024).decode('ascii') # message contains token and status
  time.sleep(0.1)
  server_return = receiveServerMessage()
  # print(server_return)
  data = json.loads(server_return)# make a json format from a dict
  message = data["message"]
  status = data["status"]
  return status,message # return status, message for that status
  



ERROR, SUCCESS = "ERROR", "SUCCESS"
CANCEL = 'CANCEL'
SESSION_EXPIRED = "SESSION EXPIRED"

def exitApplication():
  print("See you again")
  exit(0)


try:

  while True:
    # Before login, user can choose to connect to server or exit the application
    # phase 0: welcome and ask for other next step
    print("Welcome to the Note Server.")
    print("What do you want to do: ")
    accessInput = ''
    while accessInput not in ['1', '2']:
      print("1. Log in")
      print("2. Exit")
      accessInput = input("Enter your choice (1 or 2): ")
      # this code is at very bottom
      if accessInput == '2':
        exitApplication()
      
    # now we are in the application and want to log into the application
    # so we have to enter the identifer (limited by server)
    
    # now we can connect to server
    if ssock == None:
      openConnection()

    
    # Phase 1
    identifier = ''
    loginStatus = ''
    loginRcvMessage = ''
    # asking for Identifier or user cancel the action to go back to the application preface(above)
    while loginStatus != SUCCESS:
      loginInput = input("Indentifier or CANCEL(enter 0): ")
      if loginInput == '0':
        accessInput == ''
        closeConnection()
        break;
      identifier = loginInput
      loginStatus, loginRcvMessage = loginByID(identifier)
      if loginStatus == SUCCESS:
        print(loginStatus + ": Logged in, token saved.")
        token = loginRcvMessage
      else: 
        print(loginStatus + ": ", loginRcvMessage)  
    
    
    # now we are in phase 2
    action = ''
    actionStatus = ''
    actionRcvMessage = ''
    while token:
      print("What action do you want to perform: ")
      availableAction = ACTIONS[1:]
      # print out: 'LOGOUT', 'ADD', 'RETRIEVE', 'DELETE'
      action = ''
      for i in range(len(availableAction)):
        print(i, ".", availableAction[i])    
      while action not in availableAction:
        actionChoice = input("Enter your choice: ")
        if actionChoice.isnumeric() and int(actionChoice) in range(len(availableAction)):
          action = availableAction[int(actionChoice)]
        else:
          print("Not correct choice")
      
      match action:
        case 'LOGOUT':
          actionStatus, actionRcvMessage = logout(token)
          print(actionStatus, ":", actionRcvMessage)
          if isSessionExpired(actionStatus, actionRcvMessage):
            closeConnection()
            break
          if actionStatus == SUCCESS:
            closeConnection()
            break
          else:
            continue
            
          
        case 'RETRIEVE':
          retrieveInput = input("Please enter the note name for specific note or ALL for all notes: ")
          actionStatus, actionRcvMessage = retrieve(retrieveInput, token)
          print(actionStatus, ":", actionRcvMessage)
          if isSessionExpired(actionStatus, actionRcvMessage):
            closeConnection()
            print(SESSION_EXPIRED)
            break
          continue
        
        case 'ADD':
          noteName = input("Please enter note name: ")
          noteText = input("Please enter note: ")
          actionStatus, actionRcvMessage = add(noteName=noteName, noteMessage=noteText, token=token)
          print(actionStatus, ":", actionRcvMessage)
          if isSessionExpired(actionStatus, actionRcvMessage):
            closeConnection()
            print(SESSION_EXPIRED)
            break
          continue
        
        case 'DELETE':
          noteName = input("Please enter note name: ")
          actionStatus, actionRcvMessage = delete(noteName=noteName, token=token)
          print(actionStatus, ":", actionRcvMessage)
          if isSessionExpired(actionStatus, actionRcvMessage):
            closeConnection()
            print(SESSION_EXPIRED)
            break
          continue
        
      if actionStatus == ERROR and actionRcvMessage == SESSION_EXPIRED:
        token = None
        break
          
          
    
except KeyboardInterrupt as e:
  if token:
    status, logoutMessage = logout(token)
    print(status, ":", logoutMessage)
  if ssock:
    closeConnection()
  exitApplication()
except Exception as e:
  print("ERROR: ", e)
  exitApplication()
  
    
    
      
        
        
    
        
        
        
        
      
  