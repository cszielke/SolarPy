#!/usr/bin/env python3
from pv.data import PVData
from struct import pack, unpack
from time import time
from time import sleep
import serial
import sys

import jsons


class Devices():
    DEV_IFCARD = 0x00
    DEV_INV = 0x01
    DEV_SENSOR = 0x02


class Commands():
    IFCCMD_GET_VERSION = 0x01
    IFCCMD_GET_DEVTYP = 0x02
    IFCCMD_GET_TIME = 0x03
    IFCCMD_GET_ACTIVE_INVERTER_CNT = 0x04
    IFCCMD_GET_SENSOR_CARD_CNT = 0x05
    IFCCMD_GET_LOCALNET_STATUS = 0x06

    INV_GET_POWER_NOW = 0x10
    INV_GET_ENERGY_TOTAL = 0x11
    INV_GET_ENERGY_DAY = 0x12
    INV_GET_ENERGY_YEAR = 0x13
    INV_GET_AC_CURRENT_NOW = 0x14
    INV_GET_AC_VOLTAGE_NOW = 0x15
    INV_GET_AC_FREQ_NOW = 0x16
    INV_GET_DC_CURRENT_NOW = 0x17
    INV_GET_DC_VOLTAGE_NOW = 0x18

    INV_GET_YIELD_DAY = 0x19

    INV_GET_MAX_POWER_DAY = 0x1a
    INV_GET_MAX_AC_VOLTAGE_DAY = 0x1b
    INV_GET_MIN_AC_VOLTAGE_DAY = 0x1c
    INV_GET_MAX_DC_VOLTAGE_DAY = 0x1d

    INV_GET_OPERATING_HOURS_DAY = 0x1e  # Tages-Betriebszeit

    INV_GET_YIELD_YEAR = 0x1f

    INV_GET_MAX_POWER_YEAR = 0x20
    INV_GET_MAX_AC_VOLTAGE_YEAR = 0x21
    INV_GET_MIN_AC_VOLTAGE_YEAR = 0x22
    INV_GET_MAX_DC_VOLTAGE_YEAR = 0x23

    INV_GET_OPERATING_HOURS_DAY = 0x24  # Jahres-Betriebszeit

    INV_GET_YIELD_TOTAL = 0x25

    INV_GET_MAX_POWER_TOTAL = 0x26
    INV_GET_MAX_AC_VOLTAGE_TOTAL = 0x27
    INV_GET_MIN_AC_VOLTAGE_TOTAL = 0x28
    INV_GET_MAX_DC_VOLTAGE_TOTAL = 0x29

    INV_GET_OPERATING_HOURS_TOTAL = 0x24  # Jahres-Betriebszeit

    # 0x2b - 0x35 3 PHase Inverter

    # 0xe0 - 0xf9 Sensor-Card


class FroniusIG:
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

    port = None
    baudrate = 19200
    bytesize = serial.EIGHTBITS
    parity = serial.PARITY_NONE
    stopbits = serial.STOPBITS_ONE
    timeout = None
    xonxoff = False
    rtscts = False
    write_timeout = None
    dsrdtr = False
    inter_byte_timeout = None

    ser = serial.Serial()
    isreadingalready = False
    pvdata = PVData()

    def __init__(
            self,
            wrcount,
            port=None,
            baudrate=19200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=None,
            xonxoff=False,
            rtscts=False,
            write_timeout=None,
            dsrdtr=False,
            inter_byte_timeout=None):

        self.ser = None

        self.pvdata.wr.clear()
        for i in range(wrcount):
            self.pvdata.wr.append({"PDay": 0, "PNow": 0, "UDC": 0, "IDC": 0, "UAC": 0, "IAC": 0, "FAC": 50})

    def open(self):
        if(self.ser is None):
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout,
                xonxoff=self.xonxoff,
                rtscts=self.rtscts,
                write_timeout=self.write_timeout,
                dsrdtr=self.dsrdtr,
                inter_byte_timeout=self.inter_byte_timeout)  # open COM-Port

    def close(self):
        if(self.ser is not None):
            self.ser.close()
            self.ser = None

    def SendIG(self, dev, nr, cmd, val):
        ret = -1
        if(self.ser is not None and self.ser.is_open):
            length = 0  # len(val)
            if(length == 0):
                ba1 = pack(">BBBB", length, dev, nr + 1, cmd)
            else:
                ba1 = pack(">BBBB{}B".format(length), length, dev, nr + 1, cmd, val)

            # Checksumme berechnen
            chksum = 0
            for b in ba1:
                chksum = chksum + b

            ba2 = pack(">BBB{}sB".format(len(ba1)), 0x80, 0x80, 0x80, ba1, chksum)
            self.ser.write_timeout = 1
            self.ser.write(ba2)

            sleep(0.02)
            try:
                ba = bytearray()
                while(self.ser.in_waiting != 0):
                    ba.append(self.ser.read()[0])
                    if(self.ser.in_waiting == 0):
                        sleep(0.02)

                print(ba.hex())

                rest = bytearray()
                if(len(ba) > 6):
                    start1, start2, start3, length, device, number, command, rest = unpack(">BBBBBBB{}s".format(len(ba)-7), ba)

                if(start1 != 0x80 or start2 != 0x80 or start3 != 0x80):
                    print("Error: Start sequence wrong")
                elif(command == 0x0e):
                    if(number > 0 and number < len(self.ERRORSTRINGS)):
                        print("Error Nr: ", str(number), "(", self.ERRORSTRINGS[number], ")")
                    else:
                        print("Error Nr: ", str(number))
                else:
                    if(length == 0):
                        ret = -1
                    elif(length == 1):
                        val, checksum = unpack(">BB", rest)
                        ret = val
                    elif(length == 3):
                        msb, lsb, exp, checksum = unpack(">BBbB", rest)
                        ret = (msb*256+lsb) * pow(10, exp)

            except BaseException as e:
                self.pvdata.Error = "Error SendIG:"+str(e)
                print(self.pvdata.Error, file=sys.stderr)

        return ret

    def SendCommand(self, dev, nr, cmd):
        # TODO: IG Interface Easy abfragen
        ret = None
        if(dev == Devices.DEV_IFCARD):
            ret = self.SendIG(dev, nr, cmd, 0)
        elif(dev == Devices.DEV_INV):
            ret = self.SendIG(dev, nr, cmd, 0)
        elif(dev == Devices.DEV_SENSOR):
            ret = self.SendIG(dev, nr, cmd, 0)
        return ret

    def GetData(self, valuestr, wrnr):
        value = 0
        if(valuestr == "PDay"):
            value = self.SendCommand(Devices.DEV_INV, wrnr, Commands.INV_GET_ENERGY_DAY)
        elif(valuestr == "PNow"):
            value = self.SendCommand(Devices.DEV_INV, wrnr, Commands.INV_GET_POWER_NOW)
        elif(valuestr == "UDC"):
            value = self.SendCommand(Devices.DEV_INV, wrnr, Commands.INV_GET_DC_VOLTAGE_NOW)
        elif(valuestr == "IDC"):
            value = self.SendCommand(Devices.DEV_INV, wrnr, Commands.INV_GET_DC_CURRENT_NOW)
        elif(valuestr == "UAC"):
            value = self.SendCommand(Devices.DEV_INV, wrnr, Commands.INV_GET_AC_VOLTAGE_NOW)
        elif(valuestr == "IAC"):
            value = self.SendCommand(Devices.DEV_INV, wrnr, Commands.INV_GET_AC_CURRENT_NOW)
        elif(valuestr == "FAC"):
            value = self.SendCommand(Devices.DEV_INV, wrnr, Commands.INV_GET_AC_FREQ_NOW)
        else:
            self.pvdata.Error = "Wrong valuestr '{}'".format(valuestr)
            print(self.pvdata.Error, file=sys.stderr)
            value = -1

        return value

    def GetAllData(self):
        if(not self.isreadingalready):
            self.isreadingalready = True
            try:
                self.pvdata.Error = "OK"  # we expect everything to be ok
                for i in range(len(self.pvdata.wr)):
                    self.pvdata.wr[i]["PDay"] = self.GetData("PDay", i)
                    self.pvdata.wr[i]["PNow"] = self.GetData("PNow", i)
                    self.pvdata.wr[i]["UDC"] = self.GetData("UDC", i)
                    self.pvdata.wr[i]["IDC"] = self.GetData("IDC", i)
                    self.pvdata.wr[i]["UAC"] = self.GetData("UAC", i)
                    self.pvdata.wr[i]["IAC"] = self.GetData("IAC", i)
                    self.pvdata.wr[i]["FAC"] = self.GetData("FAC", i)

                    self.pvdata.PGesamt = self.pvdata.PGesamt + self.pvdata.wr[i]["PNow"]
                    self.pvdata.PDayGesamt = self.pvdata.PDayGesamt + self.pvdata.wr[i]["PDay"]

                self.pvdata.Time = time()

            except BaseException as e:
                self.pvdata.Error = "Error:"+str(e)
            finally:
                self.isreadingalready = False

        return self.pvdata


if __name__ == "__main__":
    fr = FroniusIG(2)  # 2 Wechselrichter
    fr.port = "COM9"
    fr.open()
    fr.GetAllData()
    print(jsons.dumps(fr.pvdata))
