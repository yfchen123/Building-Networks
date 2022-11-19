# Include Python's Socket Library
from socket import *
from os import path

# Specify Server Port
serverPort = 8080

# Create TCP welcoming socket
serverSocket = socket(AF_INET,SOCK_STREAM)

#serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# Bind the server port to the socket
serverSocket.bind(("" ,serverPort))

# Server begins listerning foor incoming TCP connections
serverSocket.listen(1)
print ('The server is ready to receive')

while True: # Loop forever
    # Server waits on accept for incoming requests.
    # New socket created on return
    connectionSocket, addr = serverSocket.accept()

    # Read from socket (but not address as in UDP)
    page = connectionSocket.recv(1024).decode()
    filename = page.split(" ")[1]

    #for testing purposes
    #filename = "file.txt"

    #checking for the existence of the file
    '''if(not str(path.exists(filename))):
        connectionSocket.send(b'HTTP/1.0 404 Not Found\r\n\r\n')
        # Close connection as the file does not exist
        connectionSocket.close()'''
    
    try:
        file = open("." + filename)
        bytes = file.read()
        file.close()

        #Send one HTTP header line into socket
        connectionSocket.send(b'HTTP/1.0 200 OK\r\n\r\n')
        #Send the content of the requested file to the client
        for i in range(0, len(bytes)):
            connectionSocket.send(bytes[i].encode())

        # Close connectiion too client (but not welcoming socket)
        connectionSocket.close()
    except:
        connectionSocket.send(b'HTTP/1.0 400 BAD\r\n\r\n')

        # Close connectiion too client (but not welcoming socket)
        connectionSocket.close()