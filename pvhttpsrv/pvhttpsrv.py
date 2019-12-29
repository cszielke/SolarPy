#!/usr/bin/env python3

# Infos: https://www.afternerd.com/blog/python-http-server/
#        https://daanlenaerts.com/blog/2015/06/03/create-a-simple-http-server-with-python-3/
#        https://stackabuse.com/serving-files-with-pythons-simplehttpserver-module/

from pv.data import PVData
import threading
from http.server import HTTPServer
from pvhttpsrv.server import Server


class PVHttpSrv:
    serveraddress = ""
    port = 8080
    directory = ""
    handler = None
    httpd = None

    pvdata = PVData()

    def __init__(self, serveraddress="", port=8080, directory="", onDataRequest=None, onWebCamRequest=None):
        self.port = port
        self.directory = directory
        self.serveraddress = serveraddress

        self.handler = Server  # pvHttpRequestHandler
        self.handler.onDataRequest = onDataRequest
        self.handler.onWebCamRequest = onWebCamRequest

        # Server settings
        # Choose port 8080, for port 80, which is normally used for a http server, you need root access
        server_address = (self.serveraddress, self.port)
        self.httpd = HTTPServer(server_address, self.handler)
        self.server_thread = threading.Thread(target=self.httpd.serve_forever)
        self.server_thread.daemon = True

    def run(self):
        print('starting http server...')
        self.server_thread.start()
        print('running http server...')

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        print("http server stopped")
