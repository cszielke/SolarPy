#!/usr/bin/env python3
from pvhttpsrv.routes.response.requestHandler import RequestHandler
from pv.data import PVData


class WebCamRequestHandler(RequestHandler):
    pvdata = PVData()

    def __init__(self):
        super().__init__()
        self.contentType = 'image/jpeg'
        self.setStatus(200)

    def getContents(self):
        try:
            webc = bytearray()
            self.setStatus(200)
            if(self.onWebCamRequest is not None):
                webc = self.onWebCamRequest(withdata=True)
            return webc

        except Exception as e:
            print("Error WebCamRequestHandler getContents: ", str(e))
            self.setStatus(404)
            return False
