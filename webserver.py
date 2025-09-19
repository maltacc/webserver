import socket 

# web server is a networking server on top of a physical one 
# it listens for client requests, generates responses, and returns 
# the response to teh client 
# cients and servers communicate using the HTTP protocol

HOST, PORT = '', 8888

# a socket is an endpoint for sending or receiving data across a network
# it's like a pipe that provides communication

# steps to establishing a socket for web server: create scoket -> bind -> listen -> accept connections in a loop
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print(f'Serving HTTP on port {PORT} ...')

while True:
    # browser must establish tcp connection to server and wait for server to 
    # send a response back. Then we can send the server an HTTP request over TCP
    (client_conn, client_addr) = listen_socket.accept()

    # receive data from socket, max amount of data to receive at a time is the arg
    request_data = client_conn.recv(1024)

    # decode bytes representing the returned data
    print(request_data.decode('utf-8'))

    # construct a simple HTTP response at
    # http:// (HTTP protocol) 
    # localhost: (host name)
    # 8888 (port number)
    # /hello (path to resource on server)

    # HTTP/1.1 (HTTP version) 200 OK (status code) && Hello World (HTTP response body)
    http_response = b"""\
HTTP/1.1 200 OK

Hello, World!
"""
    client_conn.sendall(http_response)
    client_conn.close()

# we can simulate browsers using telnet 
# run telnet localhost 8888 and type the request "GET /hello HTTP/1.1"
# GET (HTTP Method)
# /hello (path to resource on server)
# HTTP/1.1 (HTTP version)

# how can we ensure the web server works with different web frameworks? 
# we can use WSGI (Web Server Gateway Interface)