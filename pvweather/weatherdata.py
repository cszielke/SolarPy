#!/usr/bin/env python3
# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
import jsons
from dataclasses import dataclass
from time import time

# http://192.168.15.252/webcam/currdat.php
# http://192.168.15.252/webcam/camstr.txt
# http://192.168.15.252/webcam/wsdata.txt
# http://192.168.15.252/webcam/data.json


@dataclass
class WeatherData:
    MeasureTime: float = time()
    Tout: float = -273.15
    Tin: float = -273.15
    Hout: float = 0.0
    Hin: float = 0.0
    Rain1h: float = 0.0
    Rain24h: float = 0.0
    RainTotal: float = 0.0
    PressureRel: float = 0.0
    PressureAbs: float = 0.0
    Wind: float = 0.0
    WindAvg: float = 0.0
    WindGust: float = 0.0
    WindDir: float = 0.0
    State: str = ""
    Error: str = ""
    Tendency: str = "notvalid"
    Forecast: str = "notvalid"
    Storm: str = "notvalid"
    Drewpoint: float = 0.0
    Windchill: float = 0.0
    WindDirName: str = ""

    def toJson(self) -> str:
        jsondata = str(jsons.dump(self)).replace("'", '"')
        return jsondata
