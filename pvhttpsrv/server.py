#!/usr/bin/env python3
import os
from http.server import BaseHTTPRequestHandler
from pvhttpsrv.routes.main import routes

from pvhttpsrv.routes.response.dataRequestHandler import DataRequestHandler
from pvhttpsrv.routes.response.webcamRequestHandler import WebCamRequestHandler
from pvhttpsrv.routes.response.staticHandler import StaticHandler
from pvhttpsrv.routes.response.templateHandler import TemplateHandler
from pvhttpsrv.routes.response.badRequestHandler import BadRequestHandler


class Server(BaseHTTPRequestHandler):
    def do_HEAD(self):
        return

    def do_POST(self):
        request_name = os.path.basename(self.path)
        if request_name == "config":
            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself
            print("POST request,\nPath: {}\nHeaders:\n{}\n\nBody:\n{}\n".format(
                str(self.path), str(self.headers), post_data.decode('utf-8')))

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("404 Not Found {}".format(self.path).encode('utf-8'))
        return

    def do_GET(self):
        split_path = os.path.splitext(self.path)
        request_extension = split_path[1]
        request_name = os.path.basename(self.path)

        if request_extension == "" or request_extension == ".html" or request_extension == ".txt":
            if self.path in routes:
                handler = TemplateHandler()
                handler.onDataRequest = self.onDataRequest
                handler.directory = self.directory
                handler.find(routes[self.path])
            else:
                handler = BadRequestHandler()
        elif request_extension == ".py":
            handler = BadRequestHandler()
        elif request_extension == ".json":
            handler = DataRequestHandler()
            handler.onDataRequest = self.onDataRequest
            handler.find(self.path)
        elif (request_name == 'ipcam.jpg' or request_name == 'pvipcam.jpg'):
            handler = WebCamRequestHandler()
            handler.onWebCamRequest = self.onWebCamRequest
            handler.find(self.path)
        else:
            handler = StaticHandler()
            handler.directory = self.directory
            handler.find(self.path)

        self.respond({
            'handler': handler
        })

    def handle_http(self, handler):
        status_code = handler.getStatus()

        self.send_response(status_code)

        if status_code == 200:
            content = handler.getContents()
            self.send_header('Content-type', handler.getContentType())
        else:
            content = "404 Not Found"

        self.end_headers()

        if isinstance(content, (bytes, bytearray)):
            return content

        return bytes(content, 'UTF-8')

    def respond(self, opts):
        response = self.handle_http(opts['handler'])
        self.wfile.write(response)

    def log_message(self, format, *args):
        print("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))
