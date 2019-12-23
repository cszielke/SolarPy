#!/usr/bin/env python3
from pv.data import PVData
from influxdb import InfluxDBClient
import datetime
import pytz


class PVInflux:
    local = pytz.timezone("Europe/Berlin")
    pvdata = PVData()

    client = None

    host = '127.0.0.1'
    port = 8086
    username = 'admin'
    password = ''
    database = 'pvtest'

    def __init__(self, host='127.0.0.1', port=8086, username='admin', password='', database='pvtest'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

        # connect database
        self.client = InfluxDBClient(host=self.host, port=self.port, username=self.username, password=self.password)
        self.client.switch_database(self.database)

    def SendData(self):
        try:
            datapoint = [{
                "measurement": "PVAnlage",
                "time": datetime.datetime.utcfromtimestamp(self.pvdata.Time),
                "fields": {
                    "WR1WNow": float(self.pvdata.wr[0]["PNow"]),
                    "WR1DCVNow": float(self.pvdata.wr[0]["UDC"]),
                    "WR1DCANow": float(self.pvdata.wr[0]["IDC"]),
                    "WR1ACVNow": float(self.pvdata.wr[0]["UAC"]),
                    "WR1ACANow": float(self.pvdata.wr[0]["IAC"]),
                    "WR1ACHzNow": float(self.pvdata.wr[0]["FAC"]),
                    "WR1WDay": float(self.pvdata.wr[0]["PDay"]),
                    "WR2WNow": float(self.pvdata.wr[1]["PNow"]),
                    "WR2DCVNow": float(self.pvdata.wr[1]["UDC"]),
                    "WR2DCANow": float(self.pvdata.wr[1]["IDC"]),
                    "WR2ACVNow": float(self.pvdata.wr[1]["UAC"]),
                    "WR2ACANow": float(self.pvdata.wr[1]["IAC"]),
                    "WR2ACHzNow": float(self.pvdata.wr[1]["FAC"]),
                    "WR2WDay": float(self.pvdata.wr[1]["PDay"]),
                    "PNow": float(self.pvdata.PGesamt),
                    "PDay": float(self.pvdata.PDayGesamt)
                }
            }]

            print(self.client.write_points(datapoint))
            print(datapoint)
            print("Inserted InfluxDB dataset")
        except Exception as e:
            print("Error: "+str(e))
