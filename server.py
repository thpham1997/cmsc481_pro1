from socket import *
import errno, time, json

note1 = {"id": 1, "name": "note1", "note": "this is the note content 1"}
note2 = {"id": 2, "name": "note2", "note": "this is the note content 2"}
note3 = {"id": 3, "name": "note3", "note": "this is the note content 3"}

database = []
database.append(note1)
database.append(note2)
database.append(note3)
print(database)

# message_from_client = {"action": 'LOGIN', "parameter": userID/noteID/a note dict}
# message_from_server = {"status": "SUCCESS/ERROR", "message": "depend on the phase and status, it can be a string or a dict"}


VALID_IDENTIFIER = ("tommy1", "hally2", "pattrick3")
ACTIONS = ('LOGIN', 'LOGOUT', 'ADD', 'RETRIEVE', 'DELETE')
MAX_SESSION_TIME = 10*60 #for now let it be 10 minutes
ERROR, SUCCESS = "ERROR", "SUCCESS"
tokens = []
cur_token = None
phase = 1

serverSocket = None
recvbufsize = 1024
session_start_time = None

def message_generator(status, message):
  return json.dumps({"status": status, "message": message})


  
def tokenize(identifier):
  return hash(identifier + str(time.time()))

def getNote_byName(name):
  for note in database:
    if note['name'] == name:
      return note
  return {}
def deleteNote_byName(name):
  delete_note = None
  for note in database:
    if note['name'] == name:
      delete_note = note
  if delete_note:
    database.remove(delete_note)
    return True
  return False
  
    
def start_timer():
  session_start_time = time.time()
  
def is_session_expired():
  if time.time() - session_start_time > MAX_SESSION_TIME:
    session_start_time = None
    return True
  return False

def expired_logout():
  return logout(cur_token)

def logout(token):
  if token == cur_token:
    cur_token = None
    phase = 1
    session_start_time = None
    return True
  return False
# pretty much same funtion as client but with more logics and database process



# driver for server
serverPort = 5856
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print ("The TCP server is ready to receive msgs on port", serverPort)
while True:
    # accept a new connetion.
  csock, caddr = serverSocket.accept()
  print("Accepted TCP request from: ", caddr)
  csock.setblocking(0)
  while True:
    try:
      rcv_msg = csock.recv(recvbufsize)
      rcv_msg = rcv_msg.decode('ascii')
      # convert json string into dict
      rcv_msg_dict = json.loads(rcv_msg)
      # filter out the invalid format message first
      if len(rcv_msg_dict) < 2 or 'action' not in rcv_msg_dict.keys() or rcv_msg_dict['action'] not in ACTIONS:
        csock.send(message_generator(ERROR, 'INVALID FORMAT').encode())
        continue
      
      match phase:
        case 1:
          if rcv_msg_dict['action'] != 'LOGIN':
            csock.send(message_generator(ERROR, 'INVALID ACTION').encode())
            continue
          # parapemeter should be identifier
          if rcv_msg_dict['parameter'] not in VALID_IDENTIFIER:
            csock.send(message_generator(ERROR, 'INVALID IDENTIFIER').encode())
            continue
          
          cur_token = tokenize(rcv_msg_dict['parameter'])
          if cur_token in tokens:
            csock.send(message_generator(ERROR, 'IDENTIFIER IN USE').encode())
            continue
          
          
          csock.send(message_generator(SUCCESS, cur_token).encode())
          phase = 2
          start_timer()
          continue
        case 2:
          if is_session_expired():
            is_loggedout = expired_logout()
            if is_loggedout:
              csock.send(message_generator(ERROR, "SESSION EXPIRED").encode())
              continue
            
          if rcv_msg_dict['action'] == 'LOGIN':
            csock.send(message_generator(ERROR, 'INVALID ACTION').encode())
            continue
          
          if rcv_msg_dict['action'] == 'LOGOUT':
            client_token = rcv_msg_dict['token']
            is_loggedout = logout(client_token)
            if is_loggedout:
              csock.send(message_generator(SUCCESS, 'USER LOGGED OUT').encode())
              continue
            else:
              csock.send(message_generator(ERROR, 'LOGGING OUT FAIL').encode())
              continue
            
          if rcv_msg_dict['action'] == 'ADD':
            # @TODO: add mechanism to generate unique ID, for now, just add them first
            note = rcv_msg_dict['parameter']
            client_token = rcv_msg_dict['token']
            if len(note) != 3:
              csock.send(message_generator(ERROR, 'INVALID DATA').encode())
              continue
            if client_token != cur_token:
              csock.send(message_generator(ERROR, 'INVALID TOKEN').encode())
              continue
            
            database.append(note)
            csock.send(message_generator(SUCCESS, 'NOTE ADDED').encode())
            continue
          if rcv_msg_dict['action'] == 'RETRIEVE':
            # @TODO: add mechanism to generate unique ID, for now, just add them first
            client_token = rcv_msg_dict['token']
            if client_token != cur_token:
              csock.send(message_generator(ERROR, 'INVALID TOKEN').encode())
              continue
            
            note_name = rcv_msg_dict['parameter']
            if len(note) == 0:
              csock.send(message_generator(ERROR, 'INVALID DATA').encode())
              continue
            if note_name == "ALL":
              csock.send(message_generator(SUCCESS, database).encode())
              continue
            
            retrieved_note = getNote_byName(note_name)
            csock.send(message_generator(SUCCESS, retrieved_note).encode())
            continue
          
          if rcv_msg_dict['action'] == 'DELETE':
            # @TODO: add mechanism to generate unique ID, for now, just add them first
            client_token = rcv_msg_dict['token']
            if client_token != cur_token:
              csock.send(message_generator(ERROR, 'INVALID TOKEN').encode())
              continue
            
            note_name = rcv_msg_dict['parameter']
            if len(note) == 0:
              csock.send(message_generator(ERROR, 'INVALID DATA').encode())
              continue
            
            isDeleted = deleteNote_byName(note_name)
            if isDeleted:
              csock.send(message_generator(SUCCESS, "NOTE DELETED").encode())
              continue
            else:
              csock.send(message_generator(ERROR, "NOTE NOT EXIST").encode())
              continue
        case _:
          csock.send(message_generator(ERROR, "SERVER ERROR").encode())
          continue
        
      
      
      
    except error as e:
      if e.errno == errno.EWOULDBLOCK:
         # no data received. wait a little and read again
        time.sleep(0.1)
        continue
      else:
        # error in processing. close this connection,
        break


csock.close()