import socket
import signal
import time
from threading import Thread
# import os
from select import select


shutdown_requested = False

def signal_handler(signum, frame):
    print(f"Requested exit")
    global shutdown_requested
    shutdown_requested = True

def http_processing(request: bytes):
    print(f"Received request:\n-----\n{request}\n-----")

    pattern = f"\r\n\r\n"
    end_of_header = request.find(pattern.encode('utf-8'))
    payload = request[end_of_header+4:]
    method = request.split(b" ")[0]
    endpoint = request.split(b" ")[1]
    print(f"{method} {endpoint} {payload}")
    pass

def handle_connection(sock, payload = 2048):
    # if select([sock], [], [], 1)[0]:
    try: 
        print("Waiting connection to accept")
        client, address = sock.accept()
        client.settimeout(1)
        print("Waiting data to be received")
        data = client.recv(payload)

        if data:
            http_processing(data)
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

def server(host : str = '0.0.0.0', port : int = 8000, payload : int = 2048):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(1.0)
    sock.setblocking(True)

    server_addr = (host, port)
    try:
        print(f"Starting server at {host}:{port}")
        sock.bind(server_addr)
        sock.listen(5)
    except:
        print(f"Error detected on sock.bind -> {Exception}")
        exit()
    
    i=0
    max_thread = 2
    print(f"Listening for connections")
    active_thread = []

    while not shutdown_requested:

        while (i<max_thread):
            current_thread = Thread(target=handle_connection, args=(sock, payload))
            current_thread.start()
            active_thread.append(current_thread)
            i+=1

        if i>=max_thread:
            for thread in active_thread:
                if (not thread.is_alive()):
                    print("killing_thread")
                    print(thread)
                    thread.join()
                    active_thread.remove(thread)
                    i-=1

            time.sleep(0.00000000000000000000000001)
    sock.close()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    server('0.0.0.0', 8000, 2048)