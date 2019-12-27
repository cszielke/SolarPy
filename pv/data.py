#!/usr/bin/env python3
import jsons
from dataclasses import dataclass


@dataclass
class PVWR:
    DevType = -1
    PDay = -1
    PNow = -1
    UDC = -1
    IDC = -1
    UAC = -1
    IAC = -1
    FAC = -1
    # ATMP = -1
    # FAN0 = -1
    # FAN1 = -1
    # FAN2 = -1
    # FAN3 = -1
    # STATUS = -1
    OHTOT = -1
    OHYEAR = -1
    OHDAY = -1


@dataclass
class PVData:
    Error = "No Data"
    VersionIFC = -1
    # DevType = -1
    DevTime = -1
    ActiveInvCnt = 0
    ActiveSensorCardCnt = 0
    LocalNetStatus = -1
    Time = -1
    PGesamt = -1
    PDayGesamt = -1
    wr = [PVWR()]

    def toJson(self):
        jsondata = str(jsons.dump(self)).replace("'", '"')
        return jsondata
