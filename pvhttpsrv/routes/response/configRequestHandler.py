#!/usr/bin/env python3
from pvhttpsrv.routes.response.requestHandler import RequestHandler


class ConfigRequestHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.contentType = 'application/json'
        self.setStatus(200)

    def find(self, file_path):
        self.request_name = os.path.basename(file_path)

        try:
            print("ConfigRequestHandler Find: '" + self.request_name + "'")
            if(self.request_name == "pvdata.json"):
                self.setStatus(200)
                if(self.onDataRequest is not None):
                    self.pvdata, self.weatherdata = self.onDataRequest()
                self.jsondata = self.pvdata.toJson()

            elif(self.request_name == "osdata.json"):
                data = OSData()
                data.PsUtilVersion = psutil.version_info
                data.Cpu = psutil.cpu_percent(interval=1)
                data.CpuFreq = psutil.cpu_freq()
                data.Memory = psutil.virtual_memory()
                data.Network = psutil.net_io_counters()
                if(psutil.LINUX):
                    data.Temperatures = psutil.sensors_temperatures()
                else:
                    data.Temperatures = 0

                data.BootTime = psutil.boot_time()

                self.jsondata = data.toJson()
            elif(self.request_name == "wsdata.json"):
                self.setStatus(200)
                if(self.onDataRequest is not None):
                    self.pvdata, self.weatherdata = self.onDataRequest()
                self.jsondata = self.weatherdata.toJson()
            else:
                raise ValueError('Error: Requested data file {} not defined'.format(self.request_name))

            return True
        except Exception as e:
            print("Warning DataRequestHandler find: " + str(e))
            self.setContentType('notfound')
            self.setStatus(404)
            return False

    def getContents(self):
        try:
            if(self.jsondata is None or self.jsondata == ""):
                raise ValueError('Error JsonData is empty ({})'.format(self.jsondata))

            self.setStatus(200)
            return self.jsondata

        except Exception as e:
            print("Error DataRequestHandler getContents: ", str(e))
            self.setStatus(404)
            return False