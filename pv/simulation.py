#!/usr/bin/env python3
from pv.data import PVData, PVWR
from time import time
from random import random


class PVSimulation:
    pvdata = PVData()

    def GetPVDataSimulation(self):

        if(len(self.pvdata.wr) < 2):
            self.pvdata.wr.clear()
            self.pvdata.wr.append(PVWR())
            self.pvdata.wr.append(PVWR())

        rnd = random() * 2 - 1  # rnd=(+-)1

        udc = round(rnd * 20 + self.pvdata.wr[0].UDC, 1)
        if(udc < 0):
            udc = 0
        elif(udc > 300):
            udc = 300

        idc = (udc / 15) + (rnd * 10)

        self.pvdata.wr[0].PDay = self.pvdata.wr[0].PDay + 10
        self.pvdata.wr[1].PDay = self.pvdata.wr[1].PDay + 10

        self.pvdata.wr[0].PNow = udc * idc * 0.86            # Wirkungsgrad = 0.86
        self.pvdata.wr[1].PNow = udc * idc * 0.86 * 0.75     # WR1/WR2 = 0.75

        self.pvdata.wr[0].UDC = udc
        self.pvdata.wr[1].UDC = udc * 0.75

        self.pvdata.wr[0].IDC = idc
        self.pvdata.wr[1].IDC = idc * 0.75

        self.pvdata.wr[0].UAC = rnd * 2 + 230                  # Immer ca. 230 V
        self.pvdata.wr[1].UAC = rnd * 2 + 230

        self.pvdata.wr[0].IAC = self.pvdata.wr[0].PNow / self.pvdata.wr[0].UAC
        self.pvdata.wr[1].IAC = self.pvdata.wr[0].PNow / self.pvdata.wr[0].UAC * 0.75

        self.pvdata.wr[0].FAC = rnd * 0.5 + 50                  # Immer ca. 49.5 - 50.5 Hz
        self.pvdata.wr[1].FAC = rnd * 0.5 + 50

        self.pvdata.PTotal = self.pvdata.wr[0].PNow + self.pvdata.wr[1].PNow
        self.pvdata.PDayTotal = self.pvdata.wr[0].PDay + self.pvdata.wr[1].PDay
        self.pvdata.Time = time()
        self.pvdata.Error = "OK"

        return self.pvdata


if __name__ == "__main__":
    pvsim = PVSimulation()
    print(pvsim.GetPVDataSimulation().toJson())
