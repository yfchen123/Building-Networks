# Include Python's Socket Library
from socket import *

# Specify Server Port
serverPort = 8080

#ip = '192.168.1.90'

filename = './test.html'

# Create TCP welcoming socket
serverSocket = socket(AF_INET,SOCK_STREAM)

#serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# Bind the server port to the socket
serverSocket.bind(("" ,serverPort))

# Server begins listerning foor incoming TCP connections
serverSocket.listen(1)
print ('The server is ready to receive')

while 1: # Loop forever
     # Server waits on accept for incoming requests.
     # New socket created on return
     connectionSocket, addr = serverSocket.accept()
     #cfile = connectionSocket.makefile('rw', 5)
     #line = cfile.readline().strip()

     #connectionSocket.send(b'HTTP/1.0 200 OK\n\n')

     #message = connectionSocket.recv(1024)
     #filename = message.split()[1]
     f = open(filename)
     outputdata = f.read()
     f.close()
     #Send one HTTP header line into socket
     connectionSocket.send(b'HTTP/1.0 200 OK\r\n\r\n')
     #Send the content of the requested file to the client
     for i in range(0, len(outputdata)):
         connectionSocket.send(outputdata[i].encode())
     connectionSocket.close()
     
     # Read from socket (but not address as in UDP)
     #sentence = connectionSocket.recv(1024).decode()
     
     # Send the reply
     #capitalizedSentence = sentence.upper()
     #connectionSocket.send(capitalizedSentence.encode())
     
     # Close connectiion too client (but not welcoming socket)
     #connectionSocket.close()
