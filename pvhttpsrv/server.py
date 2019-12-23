#!/usr/bin/env python3
import os
from http.server import BaseHTTPRequestHandler
#from pathlib import Path

#from urllib.parse import urlparse
#from urllib.parse import parse_qs
from pvhttpsrv.routes.main import routes

from pvhttpsrv.routes.response.dataRequestHandler import DataRequestHandler
from pvhttpsrv.routes.response.staticHandler import StaticHandler
from pvhttpsrv.routes.response.templateHandler import TemplateHandler
from pvhttpsrv.routes.response.badRequestHandler import BadRequestHandler


class Server(BaseHTTPRequestHandler):
    def do_HEAD(self):
        return

    def do_POST(self):
        return

    def do_GET(self):
        split_path = os.path.splitext(self.path)
        request_extension = split_path[1]

        if request_extension == "" or request_extension == ".html":
            if self.path in routes:
                handler = TemplateHandler()
                handler.find(routes[self.path])
            else:
                handler = BadRequestHandler()
        elif request_extension == ".py":
            handler = BadRequestHandler()
        elif request_extension == ".json":
            handler = DataRequestHandler()
            handler.onDataRequest = self.onDataRequest
        else:
            handler = StaticHandler()
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

        if isinstance( content, (bytes, bytearray) ):
            return content

        return bytes(content, 'UTF-8')

    def respond(self, opts):
        response = self.handle_http(opts['handler'])
        self.wfile.write(response)


