#!/usr/bin/env python3
# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
import jsons
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class PVWR:
    DevType: int = 0
    PDay: float = 0.0
    PNow: float = 0.0
    UDC: float = 0.0
    IDC: float = 0.0
    UAC: float = 0.0
    IAC: float = 0.0
    FAC: float = 0.0
    EFF: float = 0.0
    OHTOT: float = 0.0
    OHYEAR: float = 0.0
    OHDAY: float = 0.0

    def Clear(self) -> None:
        self.DevType = 0
        self.PDay = 0.0
        self.PNow = 0.0
        self.UDC = 0.0
        self.IDC = 0.0
        self.UAC = 0.0
        self.IAC = 0.0
        self.FAC = 0.0
        self.EFF = 0.0
        self.OHTOT = 0.0
        self.OHYEAR = 0.0
        self.OHDAY = 0.0


@dataclass
class PVBAT:
    BatAmp: float = 0.0
    BatVol: float = 0.0
    BatChaStt: float = 0.0
    BatTmpVal: float = 0.0
    BatChrg: float = 0.0
    BatDsch: float = 0.0
    BatOpState: int = 0
    BatOpStt: str = "Unknown"

    def Clear(self) -> None:
        self.BatAmp = 0.0
        self.BatVol = 0.0
        self.BatChaStt = 0.0
        self.BatTmpVal = 0.0
        self.BatChrg = 0.0
        self.BatDsch = 0.0
        self.BatOpState = 0
        self.BatOpStt = "Information liegt nicht vor (NaNStt)"


@dataclass
class PVData:
    Error: str = "No Data"
    VersionIFC: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    DevTime: str = ""
    ActiveInvCnt: int = 0
    ActiveSensorCardCnt: int = 0
    ActiveBattCnt: int = 0
    LocalNetStatus: int = -1
    Time: float = 0.0
    PTotal: float = 0.0
    PDayTotal: float = 0.0
    wr: List[PVWR] = field(default_factory=lambda: [PVWR()])
    bat: List[PVBAT] = field(default_factory=lambda: [PVBAT()])

    def toJson(self) -> str:
        jsondata = str(jsons.dump(self)).replace("'", '"')
        return jsondata

    def Clear(self) -> None:
        self.Error = "No Data"
        self.VersionIFC = 0
        self.DevTime = -1
        self.ActiveInvCnt = 0
        self.ActiveSensorCardCnt = 0
        self.ActiveBattCnt = 0
        self.LocalNetStatus = -1
        self.Time = 0.0
        self.PTotal = 0.0
        self.PDayTotal = 0.0

        for w in self.wr:
            w.Clear()
        for b in self.bat:
            b.Clear()


@dataclass
class OSData:
    PsUtilVersion: Optional[Any] = None
    Cpu: Optional[Any] = None
    CpuFreq: Optional[Any] = None
    Memory: Optional[Any] = None
    Network: Optional[Any] = None
    Temperatures: Optional[Any] = None
    BootTime: Optional[Any] = None

    def toJson(self) -> str:
        jsondata = str(jsons.dump(self)).replace("'", '"').replace('None', '"None"')
        return jsondata
