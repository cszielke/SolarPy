#!/usr/bin/env python3
import jsons
from dataclasses import dataclass


@dataclass
class PVWR:
    DevType = 0
    PDay = 0
    PNow = 0
    UDC = 0
    IDC = 0
    UAC = 0
    IAC = 0
    FAC = 0
    # ATMP = -1
    # FAN0 = -1
    # FAN1 = -1
    # FAN2 = -1
    # FAN3 = -1
    # STATUS = -1
    OHTOT = 0
    OHYEAR = 0
    OHDAY = 0


@dataclass
class PVData:
    Error = "No Data"
    VersionIFC = -1
    # DevType = -1
    DevTime = -1
    ActiveInvCnt = 1
    ActiveSensorCardCnt = 0
    LocalNetStatus = -1
    Time = -1
    PTotal = -1
    PDayTotal = -1
    wr = [PVWR()]

    def toJson(self):
        jsondata = str(jsons.dump(self)).replace("'", '"')
        return jsondata


@dataclass
class OSData:
    PsUtilVersion = None
    Cpu = None
    CpuFreq = None
    Memory = None
    Network = None
    Temperatures = None
    BootTime = None

    def toJson(self):
        jsondata = str(jsons.dump(self)).replace("'", '"').replace('None', '"None"')
        return jsondata
