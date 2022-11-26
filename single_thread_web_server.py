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
    print(page)

    #Get the current time
    currentTime = datetime.now()

    try:
        filename = "." + page.split(" ")[1]

        #Checking for the existence of the file
        if(not path.exists(filename)):
            connectionSocket.send(b'HTTP/1.0 404 Not Found\r\n\r\n')
        else: 
            #Check if the file has been modified.
            lastModifiedTime = os.path.getmtime(filename)
            time = datetime.fromtimestamp(lastModifiedTime)

            #If the difference between currentTime and lastModifiedTime 
            # is greater than 600 seconds than send not modified message feel free to change this value.
            #currently does not work for some unknown reason.
            '''timeDiff = currentTime - time
            if(timeDiff.total_seconds() > 600):
                connectionSocket.send(b'HTTP/1.0 304 Not Modified\r\n\r\n')'''         
            
            #open the file for reading
            file = open(filename)
            contents = file.read()
            file.close()

            #Find duration of request
            endTime = datetime.now()
            timeout = endTime - currentTime

            #Check if request took longer than 5 seconds. If so send 408 response.
            if(timeout.total_seconds() > 5):
                connectionSocket.send(b'HTTP/1.0 408 Request Timed Out\r\n\r\n')
            else:
                #Send one HTTP header line into socket
                connectionSocket.send(b'HTTP/1.0 200 OK\r\n\r\n')

                #Send the content of the requested file to the client
                connectionSocket.sendall(contents.encode())
    except:
        connectionSocket.send(b'HTTP/1.0 400 Bad request\r\n\r\n')
    finally: 
        # Close connection to client (but not welcoming socket)
        connectionSocket.close()