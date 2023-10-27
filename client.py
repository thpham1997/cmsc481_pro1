from socket import *
import time, json

# items for database are notes
# note includes: {id: unique number not null, noter_name: string not null, note: string not null, date_created: date not null}
# Socket sends end in with the token unless for login
ssock = socket(AF_INET, SOCK_STREAM)
tokens = None
server_return = {"status":"status message", "token:":"client token","return":"value to return depending on action"}
action = {"action":"LOGIN or other ACTION","param":"userID/noteID/note dict","token":"if token"}
recvbufsize = 1024

ACTIONS = ('LOGIN', 'LOGOUT', 'ADD', 'RETRIEVE', 'DELETE')

def openConnection():
  serverName = "need to modify" # enter correct server address
  serverPort = 5856
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
  message = {"action":"LOGIN","parameter":id}
  ssock.send(json.dumps(message).encode())  # send a message to server with id
   #make sure the server sends the data in this order
  data = json.loads(server_return)# make a json format from a dict
  data = ssock.recv(1024) # message contains token and status
  status = data["status"]  # extract status and token
  if status == "SUCCESS":
    token = data["message"] #token is sent as message param 
  else:
    return data["message"],token # should return error message instead
  return status, token # status, token = contact the server

# PHASE 2


def logout(token):
  status = None
  message = None
  ssock.send(ACTIONS[1]+" "+token)
  data = json.loads(server_return)
  data = ssock.recv(1024) 
  status = data["status"]  # extract status and token
  if status == "SUCCESS":
    message = data["message"] #token is sent as message param 
  return status,message# return status, message
  
def retrieve(noteId, token):
  status = None
  message = {"action":"RETRIEVE","parameter":noteId} # response message
  note = None # note to return, if any
  ssock.send(json.dumps(message).encode())# send a message to server to retrieve a note or a list of note
  data = json.loads(server_return)# make a json format from a dict
  data = ssock.recv(1024) # message contains token and status
  note = data["return"]
  status = data["status"]
  # return status, notes/note
  return status, note

def add(noteName, noteMessage, token):
  #note format: note1 = {"id": 1, "name": "note1", "note": "this is the note content 1"}
  status = None
  message = {"action":"ADD","parameter":noteId, "token":token} # response message
  ssock.send(json.dumps(message).encode())# send a message to server to delete note
  data = json.loads(server_return)# make a json format from a dict
  data = ssock.recv(1024) # message contains token and status
  note = data["return"]
  status = data["status"]
  # send a message to server to add note
  # return status, message for that status
  return status,message
  
def delete(noteId, token):
  status = None
  message = {"action":"DELETE","parameter":noteId, "token":token} # response message
  ssock.send(json.dumps(message).encode())# send a message to server to delete note
  data = json.loads(server_return)# make a json format from a dict
  data = ssock.recv(1024) # message contains token and status
  message = data["return"]
  status = data["status"]
  return status,message # return status, message for that status
  



# the rest is the driver code client
  
if __name__ == '__main__':
  try:
    openConnection()
  except error as e:
    print("Error: "+e)
    exit()
  user_input = ''
  status,tokens = None
  while status != "ERROR":
    user_input = input("Enter ID") #PHASE 1
    status,tokens =  loginByID(user_input)

  print("Login successful")

  while user_input.upper() != ACTIONS(1):#PHASE 2
    print("What would you like to do? Available actions are listed below")
    for action in ACTIONS:
      if action != ACTIONS[0]:
        print(action)
    while user_input not in ACTIONS and user_input != ACTIONS[0]:
      user_input = input("> ").upper()
    match action:
      case 'ADD':
        note_to_add = {"name": "note1", "note": ""}
        note_to_add["name"] = input("What do you want to call the note?\n> ")
        note_to_add["note"] = input("What do you want to write in the note?\n> ")
        add(note_to_add["name"], note_to_add["note"],tokens)
        break
      case 'RETRIEVE':
        note_to_print = ""
        noteId = input("Which note would you like to retrieve?\n> ")
        status, note_to_print = retrieve(noteId,tokens)
        if status == "SUCCESS" and note_to_print != None:
          print(note_to_print)
        else:
          print("Error: note does not exist")
        break
      case 'DELETE':
        note_to_delete = input("What is the name of the note you would like to delete?\n>")
        status, message = delete(note_to_delete,tokens)
        if status == "SUCCESS":
          print(note_to_delete+" successfully deleted")
        else:
          print("Note failed to delete")
        break
    #verify correct action and return result

  logout(tokens)  #PHASE 3
  closeConnection()