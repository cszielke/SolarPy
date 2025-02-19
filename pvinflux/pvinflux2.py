#!/usr/bin/env python3
from pv.data import PVData
from pvbasemodul import PVBaseModul
# from influxdb import InfluxDBClient

# import influxdb_client
from influxdb_client import InfluxDBClient, Point  # , WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# import datetime
import pytz


class PVInflux2(PVBaseModul):
    local = pytz.timezone("Europe/Berlin")
    pvdata = PVData()

    client = None
    write_api = None
    enabled = False
    host = '127.0.0.1'
    port = 8086
    username = 'admin'
    password = ''
    # database = 'pvtest'
    interval = 300
    org = ""
    bucket = ""
    token = ""

    def __init__(self):
        super().__init__()

    def InitArguments(self, parser):
        super().InitArguments(parser)
        parser.add_argument('-ix2en', '--influx2enabled', help='influxdb enabled [True,False]', required=False)
        parser.add_argument('-ix2h', '--influx2host', help='influxdb url/hostname', required=False)
        parser.add_argument('-ix2p', '--influx2port', help='influxdb port', required=False)
        # parser.add_argument('-ix2u', '--influx2user', help='influxdb username', required=False)
        # parser.add_argument('-ix2pw', '--influx2password', help='influxdb password', required=False)
        parser.add_argument('-ix2org', '--influx2org', help='influxdb org', required=False)
        parser.add_argument('-ix2tok', '--influx2token', help='influxdb token', required=False)
        parser.add_argument('-i2buk', '--influx2bucket', help='influxdb bucket name', required=False)
        # parser.add_argument('-i2db', '--influx2database', help='influxdb database name', required=False)
        parser.add_argument('-i2i', '--influx2interval', help='influxdb data send interval', required=False)

    def SetConfig(self, config, args):
        super().SetConfig(config, args)
        configsection = "influx2"
        self.enabled = self.CheckArgsOrConfig(config, self.enabled, args.influx2enabled, configsection, "enabled", "bool")
        self.host = self.CheckArgsOrConfig(config, self.host, args.influx2host, configsection, "host")
        self.port = self.CheckArgsOrConfig(config, self.port, args.influx2port, configsection, "port", "int")
        # self.username = self.CheckArgsOrConfig(config, self.username, args.influx2user, configsection, "user")
        # self.password = self.CheckArgsOrConfig(config, self.password, args.influx2password, configsection, "password")
        self.org = self.CheckArgsOrConfig(config, self.org, args.influx2org, configsection, "org")
        self.token = self.CheckArgsOrConfig(config, self.token, args.influx2token, configsection, "token")
        self.bucket = self.CheckArgsOrConfig(config, self.bucket, args.influx2bucket, configsection, "bucket")
        # self.database = self.CheckArgsOrConfig(config, self.database, args.influx2database, configsection, "database")
        self.interval = self.CheckArgsOrConfig(config, self.interval, args.influx2interval, configsection, "interval", "int")

    def Connect(self):
        print("PVInflux2.Connect() called")
        super().Connect()

        # connect database
        self.client = InfluxDBClient(url=f'http://{self.host}:{self.port}', token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def SendData(self):
        try:
            # measurement=PVAnlage
            datapoint = (
                Point("PVAnlage")
                .tag("location", "zielke")
                .field("WR1WNow", float(self.pvdata.wr[0].PNow))
                .field("WR1DCVNow", float(self.pvdata.wr[0].UDC))
                .field("WR1DCANow", float(self.pvdata.wr[0].IDC))
                .field("WR1ACVNow", float(self.pvdata.wr[0].UAC))
                .field("WR1ACANow", float(self.pvdata.wr[0].IAC))
                .field("WR1ACHzNow", float(self.pvdata.wr[0].FAC))
                .field("WR1WDay", float(self.pvdata.wr[0].PDay))
                .field("WR2WNow", float(self.pvdata.wr[1].PNow))
                .field("WR2DCVNow", float(self.pvdata.wr[1].UDC))
                .field("WR2DCANow", float(self.pvdata.wr[1].IDC))
                .field("WR2ACVNow", float(self.pvdata.wr[1].UAC))
                .field("WR2ACANow", float(self.pvdata.wr[1].IAC))
                .field("WR2ACHzNow", float(self.pvdata.wr[1].FAC))
                .field("WR2WDay", float(self.pvdata.wr[1].PDay))
                .field("PNow", float(self.pvdata.PTotal))
                .field("PDay", float(self.pvdata.PDayTotal))
            )

            print(self.write_api.write(bucket=self.bucket, org=self.org, record=datapoint))

            print(datapoint)
            print("Inserted InfluxDB2 dataset")
        except Exception as e:
            print("Error: " + str(e))
