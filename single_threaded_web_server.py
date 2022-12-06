from socket import *
import time
from os import path

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000
MAXIMUM_LISTEN = 5

RESPONSE_CODES = {
    "200": 'HTTP/1.0 200 OK\r\n\r\n',
    "304": 'HTTP/1.0 304 NOT MODIFIED',
    "400": 'HTTP/1.0 400 BAD REQUEST\r\n\r\n 400: Bad Request',
    "404": 'HTTP/1.0 404 NOT FOUND\r\n\r\n 404: File Not Found',
    "408": 'HTTP/1.0 408 REQUEST TIMED OUT\r\n\r\n 408: Request Timed Out'
}


def is_modified_since(headers, filepath):
    '''
    Check if http header has If-Modified-Since 
    and last changed file datetime is bigger than that
    '''
    for line in headers:
        if "If-Modified-Since:" in line:
            modified_time = time.strptime(line[19:48], '%a, %d %b %Y %H:%M:%S %Z')
            file_time = time.localtime(path.getmtime(filepath))
            return False if modified_time >= file_time else True
    return True


def handle_request(client_connection):
        
    start_time = time.time()
    request = client_connection.recv(1024).decode()
    end_time = time.time()
    
    # Parse HTTP header
    headers = request.split('\n')
    top_header = headers[0].split()
    filename = top_header[1]
    filepath = f".{filename}"
    
    # [408 response] Check if request took longer than 5 seconds.
    if end_time - start_time > 5:
        return RESPONSE_CODES["408"]

    # [404 response] Check if the requested file exists.
    if(not path.exists(filepath) or filepath == "./"):
        return RESPONSE_CODES["404"]

    # [304 response] Check if the requested file has been updated since "If-Modified-Since"
    if not is_modified_since(headers, filepath):
        date_string = time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.localtime())
        return f"{RESPONSE_CODES['304']}\r\nDate:{date_string}\r\n\r\n"
  
    # 400 TEST PURPOSE 
    # rename(filepath, "./return400error.html")
    
    # [200 response] 
    with open(filepath) as f:
        content = f.read()
        return f"{RESPONSE_CODES['200']}\r\n\r\n{content}"
        
        
def reply_to_client(connection_socket):
    try:
        response = handle_request(connection_socket)
    # [400 response] Check if anything goes wrong during handle_request()
    except:
        response = RESPONSE_CODES['400']
    connection_socket.sendall(response.encode())
    connection_socket.close()
    
    
def open_socket(host, port, max_connection):
    server_socket = socket(AF_INET, SOCK_STREAM)
    # This prevents a connection error when attempting to open port right after closing it
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(max_connection)
    print('Listening on port %s ...' % SERVER_PORT)
    return server_socket


def main():
    # Start the server
    server_socket = open_socket(SERVER_HOST, SERVER_PORT, MAXIMUM_LISTEN
)
    
    while True:
        # Wait for client connection and get the client request
        client_connection, client_address = server_socket.accept()
        reply_to_client(client_connection)

    # Close the Server
    server_socket.close()

if __name__ == "__main__":
    main()