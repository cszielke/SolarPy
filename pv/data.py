#!/usr/bin/env python3
import jsons
from dataclasses import dataclass


@dataclass
class PVWR:
    PDay = 0
    PNow = 0
    UDC = 0
    IDC = 0
    UAC = 0
    IAC = 0
    FAC = 50
    ATMP = -1
    FAN0 = 0
    FAN1 = 0
    FAN2 = 0
    FAN3 = 0
    STATUS = 0
    OHTOT = 0
    OHYEAR = 0
    OHDAY = 0


@dataclass
class PVData:
    Error = "No Data"
    Time = 0
    PGesamt = 0
    PDayGesamt = 0
    wr = [PVWR()]

    def toJson(self):
        jsondata = str(jsons.dump(self)).replace("'", '"')
        return jsondata
