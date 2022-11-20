# Include Python's Socket Library
import os
from socket import *
from os import path
from datetime import datetime


# Specify Server Port
serverPort = 8080

# Create TCP welcoming socket
serverSocket = socket(AF_INET,SOCK_STREAM)

# Bind the server port to the socket
# NOTE: I have to put in my IP to get it to work on my device. If I just put '' it only works on other devices on my network.
serverSocket.bind(("" ,serverPort))

# Server begins listerning foor incoming TCP connections
serverSocket.listen(1)
print ('The server is ready to receive')

# Server waits on accept for incoming requests.
# New socket created on return
connectionSocket, addr = serverSocket.accept()

# Read from socket (but not address as in UDP)
page = connectionSocket.recv(1024).decode()
filename = "." + page.split(" ")[1]

while True: # Loop forever
    # Server waits on accept for incoming requests.
    # New socket created on return
    connectionSocket, addr = serverSocket.accept()

    # Read from socket (but not address as in UDP)
    page = connectionSocket.recv(1024).decode()
    print(page)
    

    try:
        filename = "." + page.split(" ")[1]

        #Checking for the existence of the file
        if(not path.exists(filename)):
            connectionSocket.send(b'HTTP/1.0 404 Not Found\r\n\r\n')
        else: 
            #Check if the file has been modified.
            lastModifiedTime = os.path.getmtime(filename)
            time = datetime.fromtimestamp(lastModifiedTime)
            #Get the current time
            currentTime = datetime.now()
            #If the difference between currentTime and lastModifiedTime 
            # is greater than 10 than send not modified message feel free to change this value.
            #currently does not work for some unknown reason.
            '''if currentTime - time > 10 :
                connectionSocket.send(b'HTTP/1.0 304 Not Modified\r\n\r\n')'''

            #open the file for reading
            file = open(filename)
            bytes = file.read()
            file.close()

            #Send one HTTP header line into socket
            connectionSocket.send(b'HTTP/1.0 200 OK\r\n\r\n')
            #Send the content of the requested file to the client
            for i in range(0, len(bytes)):
                connectionSocket.send(bytes[i].encode())
    except:
        connectionSocket.send(b'HTTP/1.0 400 Bad request\r\n\r\n')
    finally:
        
        # Close connection to client (but not welcoming socket)
        connectionSocket.close()