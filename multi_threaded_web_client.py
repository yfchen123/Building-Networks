from socket import *
import time
from _thread import *
from urllib.request import Request, urlopen

import concurrent.futures
import urllib.request


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


if __name__ == "__main__":
            
    url = f"{SERVER_HTTP_PROCTCOL}{SERVER_URL}:{SERVER_PORT}/test.html"
    is_success = True
    # We can use a with statement to ensure threads are cleaned up promptly
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(Request, url): i for i in range(100)}
        for future in concurrent.futures.as_completed(future_to_url):
            num = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                response = urlopen(data).read().decode('utf-8')
                if len(response) != 350:
                    is_success = False
                    print("Server Fail")
    end_time = time.time()
    print(end_time-start_time)
    print(is_success)

    