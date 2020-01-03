#!/usr/bin/env python3
from pvhttpsrv.routes.response.requestHandler import RequestHandler
import os


class TemplateHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.contentType = 'text/html'

    def find(self, routeData):
        try:
            basedir = os.path.abspath(self.directory)

            filename = routeData['template']
            while(os.path.isabs(filename) and len(filename) > 0):  # begins with a "/"?
                filename = filename[1:]
            filename = os.path.join(basedir, filename.replace("..", ""))

            template_file = open(filename)
            self.contents = template_file
            self.setStatus(200)
            return True
        except Exception as e:
            print("Error TemplateHandler: " + str(e))
            self.setStatus(404)
            return False
