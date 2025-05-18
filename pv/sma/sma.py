#!/usr/bin/env python3
from datetime import datetime
from pv.data import PVData, PVWR
from time import time
from time import sleep
from .modbus import Modbus
# from .register import U32, U64, STR32, S32, Register  # , S16, U16
from .smareg import add_tripower_register, set_tripower_TAGLIST
import sys

import jsons
import requests


class SMA:
    ERRORSTRINGS = [
        "Error 0",
        "Unknown command",
        "Timeout",
        "Incorrect data structure",
        "Queue of commands awaiting execution is full",
        "Device or option not present",
        "No response from device or option",
        "Sensor error",
        "Sensor not active",
        "Incorrect command for device or option"
    ]

    ip = "127.0.0.1"
    port = 502
    pvdata = PVData()
    unit = 3
    wrmodbus = None
    PwrLastDayCounter = 0
    lastday = 0

    isreadingalready = False

    def __init__(self, wrcount=1):

        self.pvdata.wr.clear()
        for i in range(wrcount):
            self.pvdata.wr.append(PVWR())

    def open(self):
        print(f"Open SMA Modbus: Unit: {self.unit}, at {self.ip}:{self.port}")
        self.wrmodbus = Modbus(ipAdress=self.ip, ipPort=self.port, modbusUnit=self.unit)
        add_tripower_register(self.wrmodbus)
        set_tripower_TAGLIST()

        registers = [
            30001,  # 30001 SMA.Modbus.Profile (Versionsnummer SMA Modbus-Profil) 1304
            30053,  # 30053 Nameplate.Model (Gerätetyp) Unknown Value 19051
            30769,  # 30769 DcMs.Amp.MPPT1 (DC Strom Eingang MPPT1) 6.521 A
            30771,  # 30771 DcMs.Vol.MPPT1 (DC Spannung Eingang  MPPT1) 462.00 V
            30773,  # 30773 DcMs.Watt.MPPT1 (DC Leistung Eingang  MPPT1) 3 kW
            30775,  # 30775 GridMs.TotW (Leistung) 5 kW
            30795,  # 30795 GridMs.TotA (Netzstrom) 23.500 A
            30803,  # 30803 GridMs.Hz (Netzfrequenz) 49.97 Hz
            30957,  # 30957 DcMs.Amp.MPPT2 (DC Strom Eingang MPPT2) 9.340 A
            30959,  # 30959 DcMs.Vol.MPPT2 (DC Spannung Eingang MPPT2) 273.10 V
            30961,  # 30961 DcMs.Watt.MPPT2 (DC Leistung Eingang  MPPT2) 3 kW
            34113   # 34113 Coolsys.Cab.TmpVal (Innentemperatur) 49.6 °C
        ]

        for register in registers:
            self.wrmodbus.poll_register(register)
            print(f"Poll Register: {register}")
        
        # TODO Read self.PwrLastDayCounter from somewhere

    def close(self):
        print("Close SMA Modbus")
        # TODO Write self.PwrLastDayCounter somewhere

    def GetAllData(self):
        if(not self.isreadingalready):
            self.isreadingalready = True
            try:
                # self.pvdata = PVData()  # Clear everything

                self.pvdata.Clear()

                self.pvdata.Error = "unknown Error"  # we expect an Error
                self.pvdata.Time = time()

                result = self.wrmodbus.start()

                for reg in result:
                    print(f"Register: {reg}")

                for id in self.wrmodbus.registers:
                    print(f"{self.wrmodbus.available_registers[id].name} = {self.wrmodbus.available_registers[id].value}")

                self.pvdata.VersionIFC = [0, 0, 0, 0]  # Array of 4 bytes: IFC-Type, Maj, Min, Release

                timenow = datetime.now()

                self.pvdata.DevTime = "{:02}.{:02}.{:02}T{:02}:{:02}:{:02}".format(timenow.day, timenow.month, timenow.year, timenow.hour, timenow.minute, timenow.second)
                print(f"Time: {self.pvdata.DevTime}")

                # Read Total Power Counter from Webpage
                PwrDayTot = 0  # Preset with 0

                response = requests.get("https://192.168.15.165/dyn/getDashValues.json", verify=False)  # , auth=('user', 'password'))
                data = response.json()
                counter = data["result"]["01B8-xxxxx731"]["6400_0046C300"]["9"][0]["val"]

                if self.PwrLastDayCounter == 0:
                    # self.PwrLastDayTot was not set after program restart
                    # Try to estimate it
                    if timenow.hour < 3:
                        # It is still night time, so set actual counter to last counter
                        self.PwrLastDayCounter = counter
                    else:
                        # TODO: Read from Databse? Read from config?
                        # To Test it uncomment next lines
                        # self.PwrLastDayCounter = 170000
                        # self.lastday = timenow.day
                        pass
                else:
                    PwrDayTot = counter - self.PwrLastDayCounter
                    # Reset PwrDayTot if date changes (Time 00:00)
                    if timenow.day != self.lastday:
                        self.lastday = timenow.day
                        self.PwrLastDayCounter = counter
                print(f"Counter: {counter}, PwrLastDayCounter: {self.PwrLastDayCounter}, PwrDayTot: {PwrDayTot}")

                self.pvdata.ActiveInvCnt = 2  # Len = 0-Inverter count

                self.pvdata.ActiveSensorCardCnt = 1  # Len = 0 - Sensorcard Count

                self.pvdata.LocalNetStatus = 0  # 1 byte

                self.pvdata.PTotal = 0
                self.pvdata.PDayTotal = PwrDayTot

                # Nur wenn mindestens 1 Inverter aktiv ist
                if(self.pvdata.ActiveInvCnt > 0):

                    for i in range(len(self.pvdata.wr)):
                        self.pvdata.wr[i].DevType = 0  # 1 byte

                        self.pvdata.wr[i].PDay = 0.0

                        self.pvdata.wr[i].PNow = 0.0

                        self.pvdata.wr[i].UDC = 0.0

                        self.pvdata.wr[i].IDC = 0.0

                        self.pvdata.wr[i].UAC = 230.0

                        self.pvdata.wr[i].IAC = 0.0

                        self.pvdata.wr[i].FAC = 50.0

                        self.pvdata.wr[i].OHDAY = 0.0

                        self.pvdata.wr[i].OHYEAR = 0.0

                        self.pvdata.wr[i].OHTOT = 0.0
                        # self.pvdata.wr[i].ATMP = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_AMBIENT_TEMP)
                        # self.pvdata.wr[i].FAN0 = self.SendIG(Devices.DEV_INV, i, Commands.INV_FAN_SPEED_0)
                        # self.pvdata.wr[i].FAN1 = self.SendIG(Devices.DEV_INV, i, Commands.INV_FAN_SPEED_1)
                        # self.pvdata.wr[i].FAN2 = self.SendIG(Devices.DEV_INV, i, Commands.INV_FAN_SPEED_2)
                        # self.pvdata.wr[i].FAN3 = self.SendIG(Devices.DEV_INV, i, Commands.INV_FAN_SPEED_3)
                        # self.pvdata.wr[i].STATUS = self.SendIG(Devices.DEV_INV, i, Commands.INV_STATUS)

                        self.pvdata.PTotal = self.pvdata.PTotal + self.pvdata.wr[i].PNow
                        # self.pvdata.PDayTotal = self.pvdata.PDayTotal + self.pvdata.wr[i].PDay

                        pab = (self.pvdata.wr[i].UAC * self.pvdata.wr[i].IAC)
                        pzu = (self.pvdata.wr[i].UDC * self.pvdata.wr[i].IDC)
                        if(pzu == 0):
                            self.pvdata.wr[i].EFF = 0
                        else:
                            self.pvdata.wr[i].EFF = round(pab / pzu, 3)

                self.pvdata.wr[0].PNow = self.wrmodbus.available_registers[30773].value
                self.pvdata.wr[0].UDC = self.wrmodbus.available_registers[30771].value
                self.pvdata.wr[0].IDC = self.wrmodbus.available_registers[30769].value
                self.pvdata.wr[0].FAC = self.wrmodbus.available_registers[30803].value

                self.pvdata.wr[1].PNow = self.wrmodbus.available_registers[30961].value
                self.pvdata.wr[1].UDC = self.wrmodbus.available_registers[30959].value
                self.pvdata.wr[1].IDC = self.wrmodbus.available_registers[30957].value
                self.pvdata.wr[1].FAC = self.wrmodbus.available_registers[30803].value

                self.pvdata.PTotal = self.wrmodbus.available_registers[30775].value
                self.pvdata.Error = "OK"  # everything ok, if we reach this line

            except BaseException as e:
                self.pvdata.Error = "Error GetAllData:" + str(e)
                print(self.pvdata.Error, file=sys.stderr)
            finally:
                self.isreadingalready = False
        else:
            # Warte max. 10 Sek bis Daten gelesen wurden
            print("Wait for busy Fronius data ready")
            timeout = 100
            while(self.isreadingalready and timeout > 0):
                sleep(0.1)
                timeout = timeout - 1
            if(timeout <= 0):
                print("Timeout busy Fronius wait for data ready", file=sys.stderr)
            print("Data ready from busy Fronius")

        return self.pvdata


if __name__ == "__main__":
    fr = SMA(2)  # 2 MPP Tracker (A uns B)
    fr.port = 502
    fr.open()
    fr.GetAllData()
    print(jsons.dumps(fr.pvdata))
