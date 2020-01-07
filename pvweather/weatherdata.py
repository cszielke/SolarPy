#!/usr/bin/env python3
import jsons
from dataclasses import dataclass
from time import time

# http://192.168.15.252/webcam/currdat.php
# http://192.168.15.252/webcam/camstr.txt
# http://192.168.15.252/webcam/wsdata.txt
# http://192.168.15.252/webcam/data.json


@dataclass
class WeatherData:
    MeasureTime = time()
    Tout = -273.15
    Tin = -273.15
    Hout = 0.0
    Hin = 0.0
    Rain1h = 0.0
    Rain24h = 0.0
    RainTotal = 0.0
    PressureAbs = 0.0
    PressureRel = 0.0
    Wind = 0.0
    WindAvg = 0.0
    WindGust = 0.0
    WindDir = 0.0
    State = ""
    Error = ""
    # extra Values
    Tendency = ""
    Forecast = ""
    Storm = ""
    Drewpoint = 0.0
    Windchill = 0.0

    def toJson(self):
        jsondata = str(jsons.dump(self)).replace("'", '"')
        return jsondata
