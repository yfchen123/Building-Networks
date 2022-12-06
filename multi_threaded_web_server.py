from socket import *
import os.path
import time
from _thread import *
from os import path
import threading 


SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000
MAXIMUM_LISTEN = 1000
WORK_PORT_POOL = [i for i in range(9000, 9200)]
IN_USE_PORT = []
LOCK = threading.Lock()
FIXED_PORT_LOCK = threading.Lock()

RESPONSE_CODES = {
    "200": 'HTTP/1.0 200 OK\r\n\r\n',
    "304": 'HTTP/1.0 304 NOT MODIFIED',
    "400": 'HTTP/1.0 400 BAD REQUEST\r\n\r\n 400: Bad Request',
    "404": 'HTTP/1.0 404 NOT FOUND\r\n\r\n 404: File Not Found',
    "408": 'HTTP/1.0 408 REQUEST TIMED OUT\r\n\r\n 408: Request Timed Out'
}


def is_modified_since(headers, filepath):
    for line in headers:
        if "If-Modified-Since:" in line:
            modified_time = time.strptime(line[19:48], '%a, %d %b %Y %H:%M:%S %Z')
            file_time = time.localtime(os.path.getmtime(filepath))
            if modified_time >= file_time:
                return False
            else:
                return True
    return True

def handle_request(request, start_time, end_time):
    
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
  
    # [200 response] 
    with open(filepath) as f:
        content = f.read()
        return f"{RESPONSE_CODES['200']}\r\n\r\n{content}"
        
def get_available_work_port():
    '''Pop a port from WORK_PORT_POOL and check if it is in use. Repeat the process until it finds a port'''

    port_found = False
    worker_port = 0
    LOCK.acquire()
    
    while not port_found:
        sock = socket(AF_INET, SOCK_STREAM)
        worker_port = WORK_PORT_POOL.pop() 
        try:
            sock.bind(("0.0.0.0", worker_port))
            port_found = True
            IN_USE_PORT.append(worker_port)
        except:
            print(f"{worker_port} is in use")
        sock.close()
        
    # If there is no available port in WORK_PORT_POOL, raise an error
    if not worker_port:
        raise Exception("No available port")
    
    LOCK.release()
    
    return worker_port
    
def return_port_number(port_number):
    # Acquire a lock to prevent race condition of port number
    LOCK.acquire()
    
    IN_USE_PORT.remove(port_number)
    WORK_PORT_POOL.insert(0, port_number)
    
    # Lock release to allow other thread to get a port number
    LOCK.release()
    
    
def tcp_server_thread(worker_port):
    # Open up a new socket for request handling
    worker_socket = open_socket(SERVER_HOST, worker_port, MAXIMUM_LISTEN)
    
    while True:
        worker_connection, worker_address = worker_socket.accept()
        start_time = time.time()
        request = worker_connection.recv(1024).decode()
        end_time = time.time()
        if not request:
            continue
        
        # Test purpose only
        # print(f"Thread ID: {threading.get_ident()}, Started at {worker_address}")
        
        try:
            response = handle_request(request, start_time, end_time)
        # [400 response] Check if anything goes wrong during handle_request()
        except:
            response = RESPONSE_CODES['400']
            
        # Test purpose only
        # time.sleep(5)
        # print(f"Thread ID: {threading.get_ident()}, Handled at {worker_address}")
        
        worker_connection.sendall(response.encode())
        worker_connection.close()
        return_port_number(worker_port)
        break
    
    
def open_socket(host, port, max_connection):
    server_socket = socket(AF_INET, SOCK_STREAM)
    # This prevents a connection error when attempting to open port right after closing it
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(max_connection)
    return server_socket
    

def is_server_running(host, port):
    is_read = False
    start = time.time()
    end = 0
    # Wait for the server for 5 seconds maximum
    while not is_read and (end - start) * 1000 < 5000 :
        end = time.time()
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((host, port))
            is_read = True
        except:
            pass
    return is_read


def tcp_client_thread(host, port, fixed_port_client_connection):
    if not is_server_running(host,port):
        print("Worker Thread Failed")
        return
    
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(fixed_port_client_connection.recv(1024))
        response = s.recv(1024)
    
    FIXED_PORT_LOCK.acquire()
    
    fixed_port_client_connection.sendall(response)
    fixed_port_client_connection.close()
    
    FIXED_PORT_LOCK.release()

def main():
    # Start the Server
    master_socket = open_socket(SERVER_HOST, SERVER_PORT, MAXIMUM_LISTEN)
    print("Fixed Server Started")
    while True:
        # Wait for client connection and get the client request
        client_connection, client_address = master_socket.accept()
        
        # Start a new server socket thread
        worker_port = get_available_work_port()
        start_new_thread(tcp_server_thread, (worker_port,))
        
        # Start a new client socket thread
        start_new_thread(tcp_client_thread, (SERVER_HOST, worker_port, client_connection))
 
    # Close the Server
    server_socket.close()


if __name__ == "__main__":
    main()