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
  try:
    ssock.close()
    ssock = None
    print("\nConnection closed\n")
  except Exception as e:
    print("ERROR: " + e)
      
def receiveServerMessage():
  while True:
    try:
      message= ssock.recv(1024).decode('ascii')
      print (message)
    except error as e:
      if e.errno == errno.EWOULDBLOCK:
      # all data received, send next data
        return message
      else: # some error occurred
        print("exit")
        ssock.close()
        return json.dumps({"status": "ERROR", "message": "Something went wrong"})
      
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
  print(server_return)
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
  print(server_return)
  data = json.loads(server_return)# make a json format from a dict
  note = data["message"]
  status = data["status"]
  # return status, notes/note
  return status, note

def add(noteId, noteName, noteMessage, token):
  #note format: note1 = {"id": 1, "name": "note1", "note": "this is the note content 1"}
  note = {"id": noteId, "name": noteName, "note": noteMessage}
  status = None
  message = {"action":"ADD","parameter": note, "token":token} # response message
  ssock.send(json.dumps(message).encode())# send a message to server to delete note
  # server_return = ssock.recv(1024).decode('ascii') # message contains token and status
  time.sleep(0.1)
  server_return = receiveServerMessage()
  print(server_return)
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
  print(server_return)
  data = json.loads(server_return)# make a json format from a dict
  message = data["message"]
  status = data["status"]
  return status,message # return status, message for that status
  



# the rest is the driver code client
  
# if __name__ == '__main__':
#   try:
#     openConnection()
#   except error as e:
#     print("An error has occurred in the connection")
#     exit()
#   user_input = ''
#   status, message, tokens = None, None, None
#   # ask the user to login first
#   while status != "SUCCESS":
    
#     print(status, tokens)
#     user_input = input("Enter ID: ") #PHASE 1
#     status,tokens =  loginByID(user_input)

#   print("Login successful")

#   while user_input.upper() != ACTIONS[1]:#PHASE 2
#     print("What would you like to do? Available actions are listed below")
#     for action in ACTIONS:
#       if action != ACTIONS[0]:
#         print(action)
#     while user_input not in ACTIONS and user_input != ACTIONS[0]:
#       user_input = input("> ").upper()
#     match user_input: #verify correct action and return result
#       case 'ADD':
#         note_to_add = {"name": "note1", "note": ""}
#         note_to_add["name"] = input("What do you want to call the note?\n> ")
#         note_to_add["note"] = input("What do you want to write in the note?\n> ")
#         status,message = add(note_to_add["name"], note_to_add["note"],tokens)
#         if status == "SUCCESS":
#           print(note_to_add["name"]+" was successfully added.")
#         else:
#           print("Error: "+status["message"])
#         continue  

#       case 'RETRIEVE':
#         note_to_print = ""
#         noteId = input("Which note would you like to retrieve?\n> ")
#         status, note_to_print = retrieve(noteId,tokens)
#         if status == "SUCCESS" and note_to_print != None:
#           print(note_to_print)
#         else:
#           print("Error: ")#note does not exist
#         continue
#       case 'DELETE':
#         note_to_delete = input("What is the name of the note you would like to delete?\n>")
#         status, message = delete(note_to_delete,tokens)
#         if status == "SUCCESS":
#           print(note_to_delete+" successfully deleted")
#         else:
#           print("Note failed to delete")
#         continue
#       case 'LOGOUT':
#         status, message = logout(tokens)
#         print(status, message)
#         continue
      
    

#   logout(tokens)  #PHASE 3
#   closeConnection()

ERROR, SUCCESS = "ERROR", "SUCCESS"
CANCEL = 'CANCEL'
SESSION_EXPIRED = "SESSION EXPIRED"

def exitApplication():
  print("See you again")
  exit(0)



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
      print(loginStatus + ": logged in, token saved.")
      token = loginRcvMessage
    else: 
      print(loginStatus + ": ", loginRcvMessage)  
  
  
  # now we are in phase 2
  action = ''
  actionStatus = ''
  actionRcvMessage = ''
  while action != 'LOGOUT' and token:
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
        continue
        
      case 'RETRIEVE':
        retrieveInput = input("Please enter the note name for specific note or ALL for all notes: ")
        actionStatus, actionRcvMessage = retrieve(retrieveInput, token)
        print(actionStatus, ":", actionRcvMessage)
        continue
      
      case 'ADD':
        # @TODO: will discard id input
        noteId = int(input("Please enter note ID: "))
        noteName = input("Please enter note name: ")
        noteText = input("Please enter note: ")
        actionStatus, actionRcvMessage = add(noteId=noteId, noteName=noteName, noteMessage=noteText, token=token)
        print(actionStatus, ":", actionRcvMessage)
        continue
      
      case 'DELETE':
        noteName = input("Please enter note name: ")
        actionStatus, actionRcvMessage = delete(noteName=noteName, token=token)
        print(actionStatus, ":", actionRcvMessage)
        continue
        
        
    # logout successfully
    # clear token and go back to login (phase 0)
    if action == "LOGOUT" and actionStatus == SUCCESS:
      ssock.close()
      ssock = None
      token = None
      break
    
    
      
        
        
    
        
        
        
        
      
  