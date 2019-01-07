from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading

from urllib.parse import urlparse, parse_qs
from random import random
from time import sleep


SERVICE_PORT = 80

MEDIUM_WAIT = 0.5
SLOW_WAIT   = 1.0
POST_WAIT   = 2.0

SERVER_LOAD_LIMIT = 0.95

class MyHander(BaseHTTPRequestHandler):
    def do_POST(self):
        url_obj = urlparse(self.path)

        query_string = self.rfile.read(int(self.headers['Content-Length']))
        post_data = dict(parse_qs(query_string))
        name_len =  len(post_data[b'name'][0])
        data_len =  len(post_data[b'data'][0])

        if (self.check_path(url_obj) is False):
            return

        if (name_len >= 10 or data_len >= 10):
            self.send_response(500, message="Internal Server Error")
            self.end_headers()
            return

        self.wait_response(base_wait=POST_WAIT)

        self.send_response(200, message="OK")
        self.end_headers()
        self.wfile.write(b'Post Succeed.\r\n')


    def do_GET(self):
        url_obj = urlparse(self.path)

        if (self.check_path(url_obj) is False):
            return

        if (url_obj.path == '/fast'):
            pass
        elif (url_obj.path == '/medium'):
            self.wait_response(base_wait=MEDIUM_WAIT)
        elif (url_obj.path == '/slow'):
            self.wait_response(base_wait=SLOW_WAIT)

        self.service_unavailable()

        self.send_response(200, message="OK")
        self.end_headers()
        self.wfile.write(b'Access Succeed.\r\n')

    def check_path(self, url_obj):
        urls = ('/fast', '/medium', '/slow')
        if (url_obj.path not in urls):
            self.send_response(404, message="Not found")
            self.end_headers()
            return False
        return True

    def service_unavailable(self):
        pseudo_server_load = random()
        if (pseudo_server_load > SERVER_LOAD_LIMIT):
            self.send_response(503, message="Service Temporarily Unavailable")
            self.end_headers()
            return

    def wait_response(self, base_wait):
        sleep(random() + base_wait)



class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def run(server_class=ThreadedHTTPServer, handler_class=MyHander):
    server_address = ('', SERVICE_PORT)
    server = server_class(server_address, handler_class)
    server.serve_forever()

def main():
    run()

if __name__ == '__main__':
    main()