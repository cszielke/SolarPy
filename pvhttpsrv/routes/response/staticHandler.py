#!/usr/bin/env python3
import os
from pvhttpsrv.routes.response.requestHandler import RequestHandler


class StaticHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.filetypes = {
            ".js": "text/javascript",
            ".css": "text/css",
            ".jpg": "image/jpeg",
            ".png": "image/png",
            ".ico": "image/x-icon",
            ".svg": "image/svg+xml",
            "notfound": "text/plain"
        }

    def find(self, file_path):
        split_path = os.path.splitext(file_path)
        extension = split_path[1]

        try:
            basedir = os.path.join(os.path.abspath(self.directory), "public")

            filename = file_path
            while(os.path.isabs(filename) and len(filename) > 0):  # begins with a "/"?
                filename = filename[1:]
            filename = os.path.join(basedir, filename.replace("..", ""))

            print("StaticHandler: '" + filename + "'")

            if extension in (".jpg", ".jpeg", ".png", ".ico"):
                self.contents = open(filename, 'rb')
            else:
                self.contents = open(filename, 'r')

            self.setContentType(extension)
            self.setStatus(200)
            return True
        except Exception as e:
            print("Warning StaticHandler: File not found. " + str(e))
            self.setContentType('notfound')
            self.setStatus(404)
            return False

    def setContentType(self, ext):
        self.contentType = self.filetypes[ext]
