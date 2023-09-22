import socket
import signal
import time
from threading import Thread
# import os

shutdown_requested = False

def signal_handler(signum, frame):
    print(f"Requested exit")
    global shutdown_requested
    shutdown_requested = True

signal.signal(signal.SIGINT, signal_handler)

class SimpleApi:

    max_connections : int
    sock : socket.socket
    host_addr : str
    port : int
    load_size : int

    def __init__(self, host_addr:str='0.0.0.0', port:int = 8000, load_size:int = 2048, max_connections = 5):

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
            self.sock.listen(5)
        except Exception as e:
            print(f"Error detected on sock.bind -> {e}")
            raise Exception(e)

    def begin_workers(self):
        i=0
        active_thread = []
        while not shutdown_requested:

            while (i<self.max_connections):
                current_thread = Thread(target=self.handle_connection)
                current_thread.start()
                active_thread.append(current_thread)
                i+=1

            if i>=self.max_connections:
                for thread in active_thread:
                    if (not thread.is_alive()):
                        print("killing_thread")
                        print(thread)
                        thread.join()
                        active_thread.remove(thread)
                        i-=1

                time.sleep(0.00000000000000000000000001)
        self.sock.close()

    def handle_connection(self):
        try: 
            print("Waiting connection to accept")
            client, address = self.sock.accept()
            client.settimeout(1)
            print("Waiting data to be received")
            data = client.recv(self.load_size)

            if data:
                self.http_processing(data)
                response = "HTTP/1.0 404 Not Found\r\n\r\nNot Found "
                client.send(response.encode("utf-8"))
            else:
                print(f"Something went wrong with the client {client}")

            client.close()
            print("Connection closed")

        except socket.timeout:
            print(f"Error timed out: {socket.timeout}")
        except OSError:
            print(f"OSError: {OSError}")
        print("Exiting 'handle_connection()'")
 
    def http_processing(self, request: bytes):
        print(f"Received request:\n-----\n{request}\n-----")

        pattern = f"\r\n\r\n"
        end_of_header = request.find(pattern.encode('utf-8'))
        payload = request[end_of_header+4:]
        method = request.split(b" ")[0]
        endpoint = request.split(b" ")[1]
        print(f"{method} {endpoint} {payload}")

if __name__ == "__main__":
    server = SimpleApi()
    server.begin_workers()