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
    EFF = 0
    # ATMP = -1
    # FAN0 = -1
    # FAN1 = -1
    # FAN2 = -1
    # FAN3 = -1
    # STATUS = -1
    OHTOT = 0
    OHYEAR = 0
    OHDAY = 0

    def Clear(self):

        self.DevType = 0
        self.PDay = 0
        self.PNow = 0
        self.UDC = 0
        self.IDC = 0
        self.UAC = 0
        self.IAC = 0
        self.FAC = 0
        self.EFF = 0
        # self.ATMP = -1
        # self.FAN0 = -1
        # self.FAN1 = -1
        # self.FAN2 = -1
        # self.FAN3 = -1
        # self.STATUS = -1
        self.OHTOT = 0
        self.OHYEAR = 0
        self.OHDAY = 0


@dataclass
class PVData:
    Error = "No Data"
    VersionIFC = 0
    # DevType = -1
    DevTime = -1
    ActiveInvCnt = 0
    ActiveSensorCardCnt = 0
    LocalNetStatus = -1
    Time = 0
    PTotal = 0
    PDayTotal = 0
    wr = [PVWR()]

    def toJson(self):
        jsondata = str(jsons.dump(self)).replace("'", '"')
        return jsondata

    def Clear(self):
        self.Error = "No Data"
        self.VersionIFC = 0
        # self.# DevType = -1
        self.DevTime = -1
        self.ActiveInvCnt = 0
        self.ActiveSensorCardCnt = 0
        self.LocalNetStatus = -1
        self.Time = 0
        self.PTotal = 0
        self.PDayTotal = 0

        for w in self.wr:
            w.Clear()


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
