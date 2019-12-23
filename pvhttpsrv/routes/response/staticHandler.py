#!/usr/bin/env python3
import os
from pvhttpsrv.routes.response.requestHandler import RequestHandler


class StaticHandler(RequestHandler):
    def __init__(self):
        self.filetypes = {
            ".js": "text/javascript",
            ".css": "text/css",
            ".jpg": "image/jpeg",
            ".png": "image/png",
            "notfound": "text/plain"
        }

    def find(self, file_path):
        split_path = os.path.splitext(file_path)
        extension = split_path[1]

        try:
            print("./template/public{}".format(file_path))

            # TODO: avoid ".." in the path

            if extension in (".jpg", ".jpeg", ".png"):
                self.contents = open("./templates/public{}".format(file_path), 'rb')
            else:
                self.contents = open("./templates/public{}".format(file_path), 'r')

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
