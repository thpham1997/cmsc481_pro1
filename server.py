from socket import *
import errno, time, json


ACTIONS = ('LOGIN', 'LOGOUT', 'ADD', 'RETRIEVE', 'DELETE', 'CANCEL')

serverSocket = None
recvbufsize = 1024

def openConnection():
  serverPort = 5856
  serverSocket = socket(AF_INET, SOCK_STREAM)
  serverSocket.bind(('', serverPort))
  serverSocket.listen(1)
  print ("The TCP server is ready to receive msgs on port", serverPort)
  


# pretty much same funtion as client but with more logics and database process



# driver for server
openConnection()
while True:
    # accept a new connetion.
  csock, caddr = serverSocket.accept()
  print("Accepted TCP request from: ", caddr)
  csock.setblocking(0)
  while True:
    try:
      rcvmsg = csock.recv(recvbufsize)
      rcvmsg = rcvmsg.decode('ascii')
      print(rcvmsg)
    except error as e:
      if e.errno == errno.EWOULDBLOCK:
         # no data received. wait a little and read again
        time.sleep(0.1)
        continue
      else:
        # error in processing. close this connection,
        break


csock.close()