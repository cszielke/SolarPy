#!/usr/bin/env python3
import jsons
from dataclasses import dataclass
import requests
import datetime
import pytz
from time import time, sleep

@dataclass
class WeatherData:
    DateTime = time()
    Tout = -257.2
    Tin = -257.2
    Hout = 0
    Hin = 0
    Rain1h = 0
    Rain24h = 0
    RainTotal = 0
    PressureAbs = 0
    PressureRel = 0
    Wind = 0
    WindAvg = 0
    WindGust = 0
    WindDir = 0
    Status = ""

    def toJson(self):
        jsondata = str(jsons.dump(self)).replace("'", '"')
        return jsondata
