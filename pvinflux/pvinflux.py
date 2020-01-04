#!/usr/bin/env python3
from pv.data import PVData
from pvbasemodul import PVBaseModul
from influxdb import InfluxDBClient
import datetime
import pytz


class PVInflux(PVBaseModul):
    local = pytz.timezone("Europe/Berlin")
    pvdata = PVData()

    client = None
    enabled = False
    host = '127.0.0.1'
    port = 8086
    username = 'admin'
    password = ''
    database = 'pvtest'
    interval = 300

    def __init__(self):
        super().__init__()

    def InitArguments(self, parser):
        super().InitArguments(parser)
        parser.add_argument('-ixen', '--influxenabled', help='influxdb enabled [True,False]', required=False)
        parser.add_argument('-ixh', '--influxhost', help='influxdb url/hostname', required=False)
        parser.add_argument('-ixp', '--influxport', help='influxdb port', required=False)
        parser.add_argument('-ixu', '--influxuser', help='influxdb username', required=False)
        parser.add_argument('-ixpw', '--influxpassword', help='influxdb password', required=False)
        parser.add_argument('-idb', '--influxdatabase', help='influxdb database name', required=False)
        parser.add_argument('-ii', '--influxinterval', help='influxdb data send interval', required=False)

    def SetConfig(self, config, args):
        super().SetConfig(config, args)
        configsection = "influx"
        self.enabled = self.CheckArgsOrConfig(config, self.enabled, args.influxenabled, configsection, "enabled", "bool")
        self.host = self.CheckArgsOrConfig(config, self.host, args.influxhost, configsection, "host")
        self.port = self.CheckArgsOrConfig(config, self.port, args.influxport, configsection, "port", "int")
        self.username = self.CheckArgsOrConfig(config, self.username, args.influxuser, configsection, "user")
        self.password = self.CheckArgsOrConfig(config, self.password, args.influxpassword, configsection, "password")
        self.database = self.CheckArgsOrConfig(config, self.database, args.influxdatabase, configsection, "database")
        self.interval = self.CheckArgsOrConfig(config, self.interval, args.influxinterval, configsection, "interval", "int")

    def Connect(self):
        print("PVInflux.Connect() called")
        super().Connect()
        # connect database
        self.client = InfluxDBClient(host=self.host, port=self.port, username=self.username, password=self.password)
        self.client.switch_database(self.database)

    def SendData(self):
        try:
            datapoint = [{
                "measurement": "PVAnlage",
                "time": datetime.datetime.utcfromtimestamp(self.pvdata.Time),
                "fields": {
                    "WR1WNow": float(self.pvdata.wr[0].PNow),
                    "WR1DCVNow": float(self.pvdata.wr[0].UDC),
                    "WR1DCANow": float(self.pvdata.wr[0].IDC),
                    "WR1ACVNow": float(self.pvdata.wr[0].UAC),
                    "WR1ACANow": float(self.pvdata.wr[0].IAC),
                    "WR1ACHzNow": float(self.pvdata.wr[0].FAC),
                    "WR1WDay": float(self.pvdata.wr[0].PDay),
                    "WR2WNow": float(self.pvdata.wr[1].PNow),
                    "WR2DCVNow": float(self.pvdata.wr[1].UDC),
                    "WR2DCANow": float(self.pvdata.wr[1].IDC),
                    "WR2ACVNow": float(self.pvdata.wr[1].UAC),
                    "WR2ACANow": float(self.pvdata.wr[1].IAC),
                    "WR2ACHzNow": float(self.pvdata.wr[1].FAC),
                    "WR2WDay": float(self.pvdata.wr[1].PDay),
                    "PNow": float(self.pvdata.PGesamt),
                    "PDay": float(self.pvdata.PDayGesamt)
                }
            }]

            print(self.client.write_points(datapoint))
            print(datapoint)
            print("Inserted InfluxDB dataset")
        except Exception as e:
            print("Error: " + str(e))
