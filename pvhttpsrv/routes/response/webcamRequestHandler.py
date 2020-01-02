#!/usr/bin/env python3
from pvhttpsrv.routes.response.requestHandler import RequestHandler
from pv.data import PVData
import os


class WebCamRequestHandler(RequestHandler):
    pvdata = PVData()
    request_name = ""

    def __init__(self):
        super().__init__()
        self.contentType = 'image/jpeg'
        self.setStatus(200)

    def find(self, file_path):
        self.request_name = os.path.basename(file_path)
        return True

    def getContents(self):
        try:
            webc = bytearray()
            self.setStatus(404)

            if(self.request_name == "pvipcam.jpg"):
                if(self.onWebCamRequest is not None):
                    self.setStatus(200)
                    webc = self.onWebCamRequest(withdata=True)
            elif(self.request_name == "ipcam.jpg"):
                if(self.onWebCamRequest is not None):
                    self.setStatus(200)
                    webc = self.onWebCamRequest(withdata=False)
            else:
                raise ValueError('Error: Requested webcam file {} not defined'.format(self.request_name))

            return webc

        except Exception as e:
            print("Error WebCamRequestHandler getContents: ", str(e))
            self.setStatus(404)
            return False
