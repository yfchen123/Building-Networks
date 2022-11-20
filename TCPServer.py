# Include Python's Socket Library
from socket import *
from os import path

# Specify Server Port
serverPort = 8080

# Create TCP welcoming socket
serverSocket = socket(AF_INET,SOCK_STREAM)

# Bind the server port to the socket
# NOTE: I have to put in my IP to get it to work on my device. If I just put '' it onyl works on other devices on my network.
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
    
    #for testing purposes
    #filename = "file.txt"

    try:
        filename = "." + page.split(" ")[1]

        #Checking for the existence of the file
        if(not path.exists(filename)):
            connectionSocket.send(b'HTTP/1.0 404 Not Found\r\n\r\n')
        else: 
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