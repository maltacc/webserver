import io
import socket 
import sys

"""
Usage: /Users/maggieguo/webserver/lsbaws/bin/python -u wsgi.py flaskapp:app
"""

class WSGIServer(object): 
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 1

    def __init__(self, server_address):
        # add socket
        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )
        # bind, set options, listen/accept for connection loop
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(server_address)
        listen_socket.listen(self.request_queue_size)

        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port

        # return headers set by web app
        self.headers_set = []
    
    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        while True:
            # new client conn
            self.client_connection, client_address = self.listen_socket.accept()
            # handle one request at a time
            self.handle_one_request()
            self.client_connection.close()
    
    def handle_one_request(self):
        # get request data with max size 1024 bytes
        self.request_data = self.client_connection.recv(1024)
        print(self.request_data.decode('utf-8'))

        self.parse_request(self.request_data)

        env = self.get_environ()

        # call app, get result for HTTP response body
        result = self.application(env, self.start_response)

        # construct HTTP response and send to client
        self.finish_response(result)
    
    def parse_request(self, text):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip(b'\r\n')
        (self.request_method,  # GET
         self.path,           # /hello
         self.request_version # HTTP/1.1
         ) = request_line.decode().split()
    
    def get_environ(self):
        env = {}
        env['wsgi.version']      = (1, 0)
        env['wsgi.url_scheme']   = 'http'
        env['wsgi.input']        = io.StringIO(self.request_data.decode('utf-8'))
        env['wsgi.errors']       = sys.stderr
        env['wsgi.multithread']  = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once']     = False
        env['REQUEST_METHOD']    = self.request_method
        env['PATH_INFO']         = self.path
        env['SERVER_NAME']       = self.server_name
        env['SERVER_PORT']       = str(self.server_port)
        return env
    
    def start_response(self, status, response_headers, exc_info=None):
        server_headers = [
            ('Date', 'Tue, 31 Mar 2020 12:54:48 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = f'HTTP/1.1 {status}\r\n'
            for header in response_headers:
                response += f'{header[0]}: {header[1]}\r\n'
            response += '\r\n'
            for data in result:
                response += data.decode('utf-8')
            print('Response data:\n', response)
            response_bytes = response.encode('utf-8')
            self.client_connection.sendall(response_bytes)
        finally:
            self.client_connection.close()

SERVER_ADDRESS = (HOST, PORT) = '', 8888

def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print(f'Serving HTTP on port {PORT} ...\n')
    httpd.serve_forever()

# server loads 'application' callable given by web framework/app 
# server reads req
# server parses req
# server creates env dict with request info
# server calls application callable, passing env and start_response callable, gets back response body
# server makes HTTP response using data returned by call to 'application' obj + status/response headers set by start_response
# send HTTP response back to client