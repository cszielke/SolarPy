#!/usr/bin/env python3

# Infos: https://medium.com/@andrewklatzke/creating-a-python3-webserver-from-the-ground-up-4ff8933ecb96
#
# Aditional Infos:
#        https://www.afternerd.com/blog/python-http-server/
#        https://daanlenaerts.com/blog/2015/06/03/create-a-simple-http-server-with-python-3/
#        https://stackabuse.com/serving-files-with-pythons-simplehttpserver-module/

from pv.data import PVData
from pvbasemodul import PVBaseModul
import threading
from http.server import HTTPServer
from pvhttpsrv.server import Server


class PVHttpSrv(PVBaseModul):
    pvdata = PVData()

    handler = None
    httpd = None

    enabled = False
    serveraddress = ""
    port = 8080
    directory = ""

    def __init__(self, serveraddress="", port=8080, directory="", onDataRequest=None, onWebCamRequest=None):
        super().__init__()

    def InitArguments(self, parser):
        super().InitArguments(parser)
        parser.add_argument('-hse', '--httpsrvenabled', help='http server enabled', required=False)
        parser.add_argument('-hsa', '--httpsrvaddress', help='http server address', required=False)
        parser.add_argument('-hsp', '--httpsrvport', help='http server port', required=False)
        parser.add_argument('-hsd', '--httpsrvdirectory', help='http server directory', required=False)

    def SetConfig(self, config, args):
        super().SetConfig(config, args)
        configsection = "httpserver"
        self.enabled = self.CheckArgsOrConfig(config, self.enabled, args.httpsrvenabled, configsection, "enabled", "bool")
        self.serveraddress = self.CheckArgsOrConfig(config, self.serveraddress, args.httpsrvaddress, configsection, "srvaddress")
        self.port = self.CheckArgsOrConfig(config, self.port, args.httpsrvport, configsection, "port", "int")
        self.directory = self.CheckArgsOrConfig(config, self.directory, args.httpsrvdirectory, configsection, "directory")

    def Connect(self, onDataRequest=None, onWebCamRequest=None):
        print("PVHttpSrv.Connect() called")
        super().Connect()
        self.onDataRequest = onDataRequest
        self.onWebCamRequest = onWebCamRequest

        self.handler = Server  # pvHttpRequestHandler
        self.handler.onDataRequest = onDataRequest
        self.handler.onWebCamRequest = onWebCamRequest
        self.handler.directory = self.directory

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
