#!/usr/bin/env python3

from pv.data import PVData


class PVWebCam:
    pvdata = PVData()
    url = ""
    username = ""
    password = ""
    savedirectory = "./htdocs/webcam"
    onDataRequest = None

    def __init__(self, url='', username='', password='', savedirectory="./htdocs/webcam", onDataRequest=None):
        self.url = url
        self.username = username
        self.password = password
        self.savedirectory = savedirectory
        self.onDataRequest = onDataRequest
        pass

    def GetWebCam(self, withdata=False):
        return bytearray()

    def SaveWebCam(self):
        print("Save Webcam picture to " + self.savedirectory)
        pass
