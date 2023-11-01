from socket import *
import errno, time, json
import sqlite3, sys

note1 = {"id": 1, "name": "note1", "note": "this is the note content 1"}
note2 = {"id": 2, "name": "note2", "note": "this is the note content 2"}
note3 = {"id": 3, "name": "note3", "note": "this is the note content 3"}

database = []
database.append(note1)
database.append(note2)
database.append(note3)
# print(database)

# message_from_client = {"action": 'LOGIN', "parameter": userID/noteID/a note dict, "token": token/""}
# message_from_server = {"status": "SUCCESS/ERROR", "message": "depend on the phase and status, it can be a string or a dict"}


VALID_IDENTIFIER = ("tommy1", "hally2", "pattrick3")
ACTIONS = ('LOGIN', 'LOGOUT', 'ADD', 'RETRIEVE', 'DELETE')
MAX_SESSION_TIME = 1*60 #for now let it be 10 minutes
ERROR, SUCCESS = "ERROR", "SUCCESS"
tokens = []
cur_token = None
phase = 1

serverSocket = None
recvbufsize = 1024
session_start_time = None
ServerBuffer = ''
MAX_EMPTYMESSAGE_THRESHOLD = 10
current_empty_count = 0

def analyze_factorize_message(incoming_message):
  global ServerBuffer
  total = 0
  if len(incoming_message) != 0 and incoming_message[-1] == '\n':
    incoming_message = incoming_message[:-1]
  print("incoming_message ", incoming_message)
  print("ServerBuffer BEFORE: " + ServerBuffer)
  ServerBuffer += incoming_message
  print("ServerBuffer DURING: " + ServerBuffer)
  if len(ServerBuffer) == 0:
    ServerBuffer = ''
    print("ServerBuffer AFTER: " + ServerBuffer)
    return {"status":"ERROR", "message": "EMPTY MESSAGE"}
    
  if ServerBuffer[0] != '{':
    ServerBuffer = ''
    print("ServerBuffer AFTER: " + ServerBuffer)
    return {"status":"ERROR", "message": "INVALID PROTOCOL"}

  for i in range(len(ServerBuffer)):
    if ServerBuffer[i] == "{":
      total +=1
    if ServerBuffer[i] == "}":
      total -=1
    if total == 0:
      standardlizedish_message = ServerBuffer[0:i + 1]
      ServerBuffer = ServerBuffer[i+1:]
      print("ServerBuffer AFTER: " + ServerBuffer)
      return {"status":"SUCCESS", "message": standardlizedish_message}
    
  print("ServerBuffer AFTER: " + ServerBuffer)
  return {"status":"ERROR", "message": "NOT COMPLETE"}

def message_generator(status, message):
  return json.dumps({"status": status, "message": message})


  
def tokenize(identifier):
  return hash(identifier + str(time.time()))
  
def start_timer():
  return time.time()
  
def is_session_expired():
  global session_start_time
  if time.time() - session_start_time > MAX_SESSION_TIME:
    session_start_time = None
    return True
  return False

def expired_logout(token):
  return logout(token)

def logout(token):
  global cur_token
  global phase
  global session_start_time
  # print(token)
  # print(cur_token)
  # print(phase)
  # print(session_start_time)
  if cur_token and token == cur_token:
    cur_token = None
    phase = 1
    session_start_time = None
    return True
  return False
# pretty much same funtion as client but with more logics and database process

# database initiate
con = sqlite3.connect("database.db")
cur = con.cursor()
createTableQuery = "create table if not exists notes (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, note TEXT)"
try:
  cur.execute(createTableQuery)
  con.commit()
except sqlite3.Error as er:
  print('SQLite error: %s' % (' '.join(er.args)))
  print("Exception class is: ", er.__class__)
  
# add some data
addDataQuery = "INSERT INTO notes (name, note) values(?, ?)"
try:
  for note in database:
    cur.execute(addDataQuery, (note['name'], note['note']))
    con.commit()
except sqlite3.Error as er:
  print('SQLite error: %s' % (' '.join(er.args)))
  print("Exception class is: ", er.__class__)


retrieveAllQuery = "SELECT * FROM notes"

try:
  res = cur.execute(retrieveAllQuery)
  data = res.fetchall()
  for d in data:
    print(d)
except sqlite3.Error as er:
  print('SQLite error: %s' % (' '.join(er.args)))
  print("Exception class is: ", er.__class__)

con.close()

def addNote_toDB(noteName, note):
  conn = sqlite3.connect("database.db")
  cur = conn.cursor()
  query = "INSERT INTO notes (name, note) values (?, ?)"
  try:
    result = cur.execute(query, (noteName, note,))
    conn.commit()
    return True
  except sqlite3.Error as e:
    print('SQLite error: %s' % (' '.join(e.args)))
    conn.close()
    return False
  
  
def retrieveNote_byName(noteName):
  conn = sqlite3.connect("database.db")
  cur = conn.cursor()
  query = "SELECT * FROM notes WHERE name = ?"
  try:
    result = cur.execute(query, (noteName, ))
    data = result.fetchone()
    if data:
      note = {"id": data[0], "name": data[1], "note": data[2]}
      # print(data)
      # print(note)
      conn.close()
      return note
    return {}
  except sqlite3.Error as e:
    print('SQLite error: %s' % (' '.join(e.args)))
    conn.close()
    return {}
  
def retrieveNote_ALL():
  conn = sqlite3.connect("database.db")
  cur = conn.cursor()
  query = "SELECT * FROM notes"
  try:
    result = cur.execute(query)
    data = result.fetchall()
    # print("retrievALL", data)
    note_list = []
    for d in data:
      note = {"id": d[0], "name": d[1], "note": d[2]}
      note_list.append(note)
    conn.close()
    # print("retrievALL", note_list)
    return note_list
  except sqlite3.Error as e:
    print('SQLite error: %s' % (' '.join(e.args)))
    conn.close()
    return []
  
def deleteNote_byName(noteName):
  conn = sqlite3.connect("database.db")
  cur = conn.cursor()
  query = "DELETE FROM notes WHERE name = ?"
  try:
    result = cur.execute(query, (noteName, ))
    conn.commit()
    conn.close()
    return True
  except sqlite3.Error as e:
    print('SQLite error: %s' % (' '.join(e.args)))
    conn.close()
    return False
    
  

# driver for server
serverPort = 5856
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print ("The TCP server is ready to receive msgs on port", serverPort)
try:
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
        print("message: " + rcv_msg)
        afm_result = analyze_factorize_message(rcv_msg)
        if afm_result['status'] == ERROR:
          if afm_result['message'] == "EMPTY MESSAGE":
            print(afm_result['message'])
            current_empty_count +=1
            if current_empty_count >= MAX_EMPTYMESSAGE_THRESHOLD:
              print(message_generator(ERROR, 'INVALID PROTOCOL'))
              csock.send(message_generator(ERROR, 'INVALID PROTOCOL').encode())
              if cur_token:
                is_loggedout = logout(cur_token)
                if is_loggedout:
                  print(message_generator(ERROR, 'USER LOGGED OUT'))
                  csock.send(message_generator(ERROR, 'USER LOGGED OUT').encode())
              csock.close()
              current_empty_count = 0
              
              break
            
            continue
          if afm_result['message'] == "INVALID PROTOCOL":
            print(message_generator(ERROR, 'INVALID PROTOCOL'))
            csock.send(message_generator(ERROR, 'INVALID PROTOCOL').encode())
            continue
          if afm_result['message'] == "NOT COMPLETE":
            print(afm_result['message'])
            continue
        
        standardlized_message = afm_result['message']
        
        # when client close connection, it send empty message
        if standardlized_message == '':
          print("EMPTY MESSAGE-CONNECTION LOST")
          logout(cur_token)
          # if csock:
          #   csock.close()
          break
        rcv_msg_dict = {}
        try:
          rcv_msg_dict = json.loads(standardlized_message)
        except Exception as e:
          print(message_generator(ERROR, 'INVALID PROTOCOL'))
          csock.send(message_generator(ERROR, 'INVALID PROTOCOL').encode())
          continue
        # print("message DICT: " + str(rcv_msg_dict))
        # filter out the invalid format message first
        if len(rcv_msg_dict) < 3 or 'action' not in rcv_msg_dict.keys() or rcv_msg_dict['action'] not in ACTIONS or 'parameter' not in rcv_msg_dict.keys() or 'token' not in rcv_msg_dict.keys():
          print(message_generator(ERROR, 'INVALID PROTOCOL'))
          csock.send(message_generator(ERROR, 'INVALID PROTOCOL').encode())
          continue
        
        
        match phase:
          case 1:
            print("Phase1")
            if rcv_msg_dict['action'] != 'LOGIN':
              print(message_generator(ERROR, 'INVALID ACTION'))
              csock.send(message_generator(ERROR, 'INVALID ACTION').encode())
              continue
            # parapemeter should be identifier
            if rcv_msg_dict['parameter'] not in VALID_IDENTIFIER:
              print(message_generator(ERROR, 'INVALID IDENTIFIER'))
              csock.send(message_generator(ERROR, 'INVALID IDENTIFIER').encode())
              continue
            
            generized_token = tokenize(rcv_msg_dict['parameter'])
            if cur_token == generized_token:
              print(message_generator(ERROR, 'IDENTIFIER IN USE'))
              csock.send(message_generator(ERROR, 'IDENTIFIER IN USE').encode())
              continue
            
            print(message_generator(SUCCESS, generized_token))
            csock.send(message_generator(SUCCESS, generized_token).encode())
            phase = 2
            session_start_time = start_timer()
            cur_token = generized_token
            continue
          
          case 2:
            print("Phase2")
            if is_session_expired():
              is_loggedout = expired_logout(cur_token)
              if is_loggedout:
                print(message_generator(ERROR, "SESSION EXPIRED"))
                csock.send(message_generator(ERROR, "SESSION EXPIRED").encode())
                # csock.close()
                break
            
            session_start_time = start_timer()
            print("Reset timer")
            
            if rcv_msg_dict['action'] == 'LOGIN':
              print(message_generator(ERROR, 'INVALID ACTION'))
              csock.send(message_generator(ERROR, 'INVALID ACTION').encode())
              continue
            
            if rcv_msg_dict['action'] == 'LOGOUT':
              client_token = rcv_msg_dict['token']
              is_loggedout = logout(client_token)
              if is_loggedout:
                print(message_generator(SUCCESS, 'USER LOGGED OUT'))
                csock.send(message_generator(SUCCESS, 'USER LOGGED OUT').encode())
                # csock.close()
                break
              else:
                print(message_generator(ERROR, 'OPERATION FAILED'))
                csock.send(message_generator(ERROR, 'OPERATION FAILED').encode())
                continue
              
            if rcv_msg_dict['action'] == 'ADD':
              note = rcv_msg_dict['parameter']
              client_token = rcv_msg_dict['token']
              if len(note) != 2:
                print(message_generator(ERROR, 'INVALID DATA'))
                csock.send(message_generator(ERROR, 'INVALID DATA').encode())
                continue
              if client_token != cur_token:
                print(message_generator(ERROR, 'INVALID TOKEN'))
                csock.send(message_generator(ERROR, 'INVALID TOKEN').encode())
                continue
              
              isAdded = addNote_toDB(note['name'], note['note'])
              if isAdded:
                print(message_generator(SUCCESS, 'NOTE ADDED'))
                csock.send(message_generator(SUCCESS, 'NOTE ADDED').encode())
              else:
                print(message_generator(ERROR, 'OPERATION FAILED'))
                csock.send(message_generator(ERROR, 'OPERATION FAILED').encode())
              continue
            
            
            if rcv_msg_dict['action'] == 'RETRIEVE':
              client_token = rcv_msg_dict['token']
              if client_token != cur_token:
                print(message_generator(ERROR, 'INVALID TOKEN'))
                csock.send(message_generator(ERROR, 'INVALID TOKEN').encode())
                continue
              
              note_name = rcv_msg_dict['parameter']
              if len(note) == 0:
                print(message_generator(ERROR, 'INVALID DATA'))
                csock.send(message_generator(ERROR, 'INVALID DATA').encode())
                continue
              
              if note_name == "ALL":
                data_all = retrieveNote_ALL()
                if len(data_all) == 0:
                  print(message_generator(ERROR, "EMPTY"))
                  csock.send(message_generator(ERROR, "EMPTY").encode())
                else:  
                  print(message_generator(SUCCESS, data_all))
                  csock.send(message_generator(SUCCESS, data_all).encode())
                continue
              
              retrieved_note = retrieveNote_byName(note_name)
              if len(retrieved_note) == 0:
                print(message_generator(ERROR, "EMPTY"))
                csock.send(message_generator(ERROR, "EMPTY").encode())
              else:
                print(message_generator(SUCCESS, retrieved_note))
                csock.send(message_generator(SUCCESS, retrieved_note).encode())
              continue
            
            if rcv_msg_dict['action'] == 'DELETE':
              client_token = rcv_msg_dict['token']
              if client_token != cur_token:
                print(message_generator(ERROR, 'INVALID TOKEN'))
                csock.send(message_generator(ERROR, 'INVALID TOKEN').encode())
                continue
              
              note_name = rcv_msg_dict['parameter']
              if len(note) == 0:
                print(message_generator(ERROR, 'INVALID DATA'))
                csock.send(message_generator(ERROR, 'INVALID DATA').encode())
                continue
              
              isDeleted = deleteNote_byName(note_name)
              if isDeleted:
                print(message_generator(SUCCESS, "NOTE DELETED"))
                csock.send(message_generator(SUCCESS, "NOTE DELETED").encode())
                continue
              else:
                print(message_generator(ERROR, "OPERATION FAILED"))
                csock.send(message_generator(ERROR, "OPERATION FAILED").encode())
                continue
          case _:
            print(message_generator(ERROR, "SERVER ERROR"))
            csock.send(message_generator(ERROR, "SERVER ERROR").encode())
            continue
          
        
        
        
      except error as e:
        if e.errno == errno.EWOULDBLOCK:
          # no data received. wait a little and read again
          time.sleep(0.1)
          continue
        else:
          # error in processing. close this connection,
          print("ERROR: " + e.strerror)
          is_loggedout = logout(cur_token)
          if is_loggedout:
            print(message_generator(ERROR, "SESSION ERROR"))
          break
except KeyboardInterrupt as e:
  print("\nBYE, SERVER IS DOWN", e)
  if serverSocket:
    serverSocket.close()
  exit(0)
except error as e:
  print("\nBYE, SERVER IS DOWN", e)
  if serverSocket:
    serverSocket.close()
  exit(0)
