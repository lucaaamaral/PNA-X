import socket
import time
from threading import Thread

class SimpleApi:

    shutdown_requested: bool = False

    max_connections : int
    sock : socket.socket
    host_addr : str
    port : int
    load_size : int

    POST_req = {}
    GET_req = {}

    method_map = {
        'GET': GET_req,
        'POST': POST_req
    }
    # TODO: HTTP resources as a class inside a class
    http_header = {
        '100': b'HTTP/1.1 100 Continue\r\nServer: SimpleApi\r\n\r\n',
        '200': b'HTTP/1.1 200 OK\r\nServer: SimpleApi\r\n',
        '404': b'HTTP/1.1 404 Not Found\r\nServer: SimpleApi\r\n\r\n',
        '405': b'HTTP/1.1 405 Method Not Allowed\r\nServer: SimpleApi\r\n\r\n',
        '405': b'HTTP/1.1 417 Expectation Failed\r\nServer: SimpleApi\r\n\r\n',
        '418': b"HTTP/1.1 418 I'm a teapot\r\nServer: SimpleApi\r\n\r\n",
        '400': b'HTTP/1.1 400 Bad Request\r\nServer: SimpleApi\r\n\r\n'
        }
    http_resource = {
        'html': http_header['200'] + b'Content-Type: text/html\r\n\r\n',
        'css': http_header['200'] + b'Content-Type: text/css\r\n\r\n',
        'png': http_header['200'] + b'Content-Type: image/png\r\n\r\n',
        'json': http_header['200'] + b'Content-Type: application/json\r\n\r\n',
    }

    def __init__(self, host_addr:str='0.0.0.0', 
                       port:int = 8000, 
                       load_size:int = 2048, 
                       max_connections:int = 2):

        self.max_connections = max_connections
        self.host_addr = host_addr
        self.port = port
        self.load_size = load_size
        self.setup_server()

    def setup_server(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1.0)
        self.sock.setblocking(True)
        print(f"Starting server at {self.host_addr}:{self.port}")
        server_addr = (self.host_addr, self.port)

        try:
            self.sock.bind(server_addr)
            self.sock.listen(self.max_connections)
        except Exception as e:
            print(f"Error detected on sock.bind -> {e}")
            raise Exception(e)

    def configure_endpoints(self, method:str, endpoint:str, function):
        if method in self.method_map.keys():
            self.method_map[method][endpoint] = function
        else:
            print(f"[WARNING] The method '{method}' provided is not yet implemented")
            raise Exception(f"The method '{method}' provided is not yet implemented")
    
    def begin_workers(self):
        
        self.thread = Thread(target=self.manage_workers)
        self.thread.start()


    def manage_workers(self):
        i=0
        active_thread = []

        while not SimpleApi.shutdown_requested:

            while (i<self.max_connections):
                current_thread = Thread(target=self.handle_connection)
                current_thread.start()
                active_thread.append(current_thread)
                i+=1

            if i>=self.max_connections:
                for thread in active_thread:
                    if (not thread.is_alive()):
                        print(f"killing_thread {thread}")
                        thread.join()
                        active_thread.remove(thread)
                        i-=1

                time.sleep(0.00000000000000000000000001)
        
        # self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("Closed socket")


    def handle_connection(self):
        try: 
            print("Waiting connection to accept")
            client, address = self.sock.accept()
            client.settimeout(1)

            self.http_processing(client) 
            # TODO: identify different protocols and handle them

            client.close()
            print("Connection closed")

        except socket.timeout:
            print(f"Error timed out: {socket.timeout}")
        except OSError:
            print(f'[WARNING] An attempt was made to deal with a non existent socket')
            # raise Exception("An attempt was made to deal with a non existent socket")
 
    def http_processing(self, client:socket.socket):

        print("Waiting data to be received")
        request = client.recv(self.load_size).decode('utf-8')

        if request:

            print(f"[DEBUG]: Received request:\n-----\n{request}\n-----")

            pattern = f"\r\n\r\n"

            end_of_header = request.find(pattern)
            payload = request[end_of_header+4:]
            method = request.split(' ')[0]
            endpoint = request.split(' ')[1]
            print(f"Processed: {method} {endpoint} {payload}")

            if not method in self.method_map:
                print(f'[WARNING] Method {method} not supported')
                # raise Exception(f'Method {method} not supported')
            
            if endpoint in self.method_map[method]:
                ans:bin = self.method_map[method][endpoint](payload)
                client.send(ans)

            else:
                client.send(self.http_header['404'])
                # raise Exception(f'Endpoint {endpoint} not supported')
            
        else:
            print(f"Something went wrong with the client {client}")
