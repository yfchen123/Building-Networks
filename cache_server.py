
"""
    Implements a simple cache proxy
"""

import socket
from urllib.request import Request, urlopen

SERVER_HTTP_PROCTCOL = "http://"
SERVER_URL = "0.0.0.0"
SERVER_PORT = 8000
PROXY_PORT = 8001

def main():
    # Define socket host and port

    # Initialize socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_URL, PROXY_PORT))
    server_socket.listen(1)

    print('Proxy is listening on port %s ...' % PROXY_PORT)

    while True:
        # Wait for client connection and get the client request
        connectionSocket, addr = server_socket.accept()
        request = connectionSocket.recv(1024).decode()
        
        # Parse HTTP header
        headers = request.split('\n')
        top_header = headers[0].split()
        method = top_header[0]
        filename = top_header[1]

        # Get the file
        content = fetch_file(filename)

        # If we have the file, return it, otherwise 404
        if content:
            response = 'HTTP/1.0 200 OK\r\n\r\n' + content
        else:
            response = 'HTTP/1.0 404 Not Found\r\n\r\nFile Not Found'

        # Send the response and close the connection
        connectionSocket.sendall(response.encode())
        connectionSocket.close()

    # Close socket
    server_socket.close()


def fetch_file(filename):
    # Let's try to read the file locally first
    file_from_cache = fetch_from_cache(filename)

    if file_from_cache:
        print('Fetched successfully from cache.')
        return file_from_cache
    else:
        print('Not in cache. Fetching from server.')
        file_from_server = fetch_from_server(filename)

        if file_from_server != 'HTTP/1.0 404 Not Found\r\n\r\nFile Not Found':
            save_in_cache(filename, file_from_server)
            return file_from_server
        else:
            return None


def fetch_from_cache(filename):
    try:
        # Check if we have this file locally
        with open(f"./cache/{filename}") as f:
            content = f.read()
        return content
    except IOError:
        return None


def fetch_from_server(filename):
    url = f"{SERVER_HTTP_PROCTCOL}{SERVER_URL}:{SERVER_PORT}{filename}"
    q = Request(url)

    response = urlopen(q)
    # Grab the header and content from the server req
    response_headers = response.info()
    content = response.read().decode('utf-8')
    return content


def save_in_cache(filename, content):
    print('Saving a copy of {} in the cache'.format(filename))
    with open('cache' + filename, 'w') as cached_file:
        cached_file.write(content)

if __name__ == '__main__':
    main()