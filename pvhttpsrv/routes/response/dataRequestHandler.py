#!/usr/bin/env python3
from pvhttpsrv.routes.response.requestHandler import RequestHandler
from pv.data import PVData


class DataRequestHandler(RequestHandler):
    pvdata = PVData()

    def __init__(self):
        super().__init__()
        self.contentType = 'application/json'
        self.setStatus(200)

    def getContents(self):
        try:
            self.setStatus(200)
            if(self.onDataRequest is not None):
                self.pvdata = self.onDataRequest()
            return self.pvdata.toJson()

        except Exception as e:
            print("Error DataRequestHandler getContents: ", str(e))
            self.setStatus(404)
            return False
