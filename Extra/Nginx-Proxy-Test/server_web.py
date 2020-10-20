#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
SERVER_IP = "0.0.0.0"
SERVER_PORT = 8080


class S(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        print("GET %s \n%s" %(str(self.path), str(self.headers)))
        # self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=S, ip="0.0.0.0", port=8080):
    server_address = (ip, port)
    httpd = server_class(server_address, handler_class)
    print('Starting HTTP server on %s port %d' %(ip, port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Stopping HTTP server...\n')

if __name__ == '__main__':
    from sys import argv
    run(ip=SERVER_IP, port=SERVER_PORT)

