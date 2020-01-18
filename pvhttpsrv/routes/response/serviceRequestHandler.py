#!/usr/bin/env python3
from pvhttpsrv.routes.response.requestHandler import RequestHandler
import os


class ServiceRequestHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.contentType = 'application/json'
        self.setStatus(200)
        self.returncontent = ""

    def processPost(self, file_path, post_data):
        self.request_name = os.path.basename(file_path)

        try:
            print("ServiceRequestHandler processPost: '" + self.request_name + "'")

            if(not(None is post_data or len(post_data) == 0)):
                print("POST request,\nPath: '{}' Body:\n{}\n".format(
                    str(file_path), post_data.decode('utf-8')))

                # TODO: Do something with service data here

                self.setStatus(200)
                self.returncontent = '{"result":"OK"}'

            else:
                raise ValueError('Error: Content is empty:')

            return True
        except Exception as e:
            print("Warning ServiceRequestHandler processPost: " + str(e))
            self.setContentType('notfound')
            self.setStatus(404)
            return False

    def getContents(self):
        try:
            return self.returncontent

        except Exception as e:
            print("Error DataRequestHandler getContents: ", str(e))
            self.setStatus(404)
            return False
