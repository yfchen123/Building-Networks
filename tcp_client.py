from socket import *

SERVER_HTTP_PROCTCOL = "http://"
SERVER_URL = "0.0.0.0"
SERVER_PORT = 8000
HTTP_REQUEST = """GET /test.html HTTP/1.1
                User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
                Host: www.tutorialspoint.com
                Accept-Language: en-us
                Accept-Encoding: gzip, deflate
                Connection: Keep-Alive
                """

with socket(AF_INET, SOCK_STREAM) as s:
    s.connect((SERVER_URL, SERVER_PORT))
    s.sendall(str.encode(HTTP_REQUEST))
    data = s.recv(1024)

print(f"Received \n{data!r}")