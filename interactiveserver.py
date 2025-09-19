import socket
from time import time 

# process connections in parallel 

SERVER_ADDRESS = (HOST, PORT) = '', 8888
REQUEST_QUEUE_SIZE = 5

def handle_request(client_connection):
    """For now, always return the same response"""
    request_data = client_connection.recv(1024)
    print(request_data.decode('utf-8'))
    http_response = b"""\
HTTP/1.1 200 OK
Content-Type: text/plain

Hello World!
"""
    client_connection.sendall(http_response)
    time.sleep(60)

def serve_forever():
    # create looping connection
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)

    print(f'Serving HTTP on port {PORT} ...')
    while True:
        client_connection, client_address = listen_socket.accept()
        handle_request(client_connection)
        client_connection.close()

if __name__ == '__main__':
    serve_forever()