#!/usr/bin/env python3
from pv.data import PVData, PVWR
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

    INV_GET_OPERATING_HOURS_YEAR = 0x24  # Jahres-Betriebszeit

    INV_GET_YIELD_TOTAL = 0x25

    INV_GET_MAX_POWER_TOTAL = 0x26
    INV_GET_MAX_AC_VOLTAGE_TOTAL = 0x27
    INV_GET_MIN_AC_VOLTAGE_TOTAL = 0x28
    INV_GET_MAX_DC_VOLTAGE_TOTAL = 0x29

    INV_GET_OPERATING_HOURS_TOTAL = 0x2a  # Gesamt-Betriebszeit

    # 0x2b - 0x31 3 PHase Inverter

    INV_GET_AMBIENT_TEMP = 0x31
    INV_FAN_SPEED_0 = 0x32
    INV_FAN_SPEED_1 = 0x33
    INV_FAN_SPEED_2 = 0x34
    INV_FAN_SPEED_3 = 0x35
    INV_STATUS = 0x37

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
            self.pvdata.wr.append(PVWR())

    def open(self):
        print("Open COM-Port")
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
        print("Close COM-Port")
        if(self.ser is not None):
            self.ser.close()
            self.ser = None

    def _parseReceived(self, ba):
        try:
            ret = 0
            rest = bytearray()
            length = -1
            command = -1

            if(len(ba) > 6):
                start1, start2, start3, length, device, number, command, rest = unpack(">BBBBBBB{}s".format(len(ba) - 7), ba)
            else:
                raise ValueError('Error: To less bytes received ({})'.format(len(ba)))

            if(start1 != 0x80 or start2 != 0x80 or start3 != 0x80 or length > len(ba)):
                raise ValueError("Error: Start sequence wrong")

            if(command == 0x0e):
                c = rest[0]
                nr = rest[1]
                if(nr > 0 and nr < len(self.ERRORSTRINGS)):
                    print("Error Nr: " + str(nr) + "(" + self.ERRORSTRINGS[nr] + ") in cmd " + str(c))
                else:
                    print("Error Nr: " + str(nr))
                rest = rest[(length + 1):]
            elif(command == 0x0f):
                c = rest[0]
                nr = rest[1]
                if(nr > 0 and nr < len(self.ERRORSTRINGS)):
                    print("Status Nr: " + str(nr) + "(" + self.ERRORSTRINGS[nr] + ") in cmd" + str(c))
                else:
                    print("Status Nr: " + str(nr))
                rest = rest[(length + 1):]
            else:
                if(length == 0):
                    ret = 0
                    checksum, rest = unpack(">B{}s".format(len(rest) - 1), rest)
                elif(length == 1):
                    val, checksum, rest = unpack(">BB{}s".format(len(rest) - 2), rest)
                    ret = val
                elif(length == 2):
                    valh, vall, checksum, rest = unpack(">BBB{}s".format(len(rest) - 3), rest)
                    ret = valh * 256 + vall
                elif(length == 3):
                    msb, lsb, exp, checksum, rest = unpack(">BBbB{}s".format(len(rest) - 4), rest)
                    ret = round((msb * 256 + lsb) * pow(10, exp),3)
                elif(length == 6):  # IFC_GetTime!
                    day, month, year, hour, minute, second, checksum, rest = unpack(">BBBBBBB{}s".format(len(rest) - 7), rest)
                    ret = "{}.{}.{}T{}:{}:{}".format(day, month, year, hour, minute, second)
                else:
                    baval = bytearray()
                    for i in range(length):
                        baval.append(rest[i])
                    ret = baval
                    rest = rest[(length + 1):]

        except BaseException as e:
            self.pvdata.Error = "Error _parseReceived:" + str(e)
            # ba = bytearray()
            print(self.pvdata.Error, file=sys.stderr)

        print("Received Command {}, Length: {}, Value: {}, ({}) Restlength: {}".format(command, length, ret, ba.hex(), len(rest)))

        return ret, rest

    def SendIG(self, dev, nr, cmd, val=bytearray(0)):
        ret = 0
        try:
            length = len(val)

            if(length == 0):
                ba1 = pack(">BBBB", length, dev, nr + 1, cmd)
            else:
                ba1 = pack(">BBBB{}s".format(length), length, dev, nr + 1, cmd, val)

            # Checksumme berechnen
            chksum = 0
            for b in ba1:
                chksum = chksum + b

            ba2 = pack(">BBB{}sB".format(len(ba1)), 0x80, 0x80, 0x80, ba1, chksum)

            # Flush input Buffer
            self.ser.flushInput()

            # Send Command
            print("Send Device {}, Nr: {}, Command: {}, val: 0x{} ({})".format(dev, nr, cmd, val.hex(), ba2.hex()))
            self.ser.write_timeout = 0.5
            self.ser.write(ba2)

            ba = bytearray()
            timeout = 100  # Max 1 Sek auf min. erste 7 Zeichen warten
            while(self.ser.in_waiting < 7 and timeout > 0):
                sleep(0.01)
                timeout = timeout - 1

            if(timeout == 0):
                self.close()
                sleep(0.5)
                self.open()
                raise ValueError('Error: Timeout receiving bytes')

            while(self.ser.in_waiting > 0):
                ba.append(self.ser.read(size=1)[0])
                if(self.ser.in_waiting == 0):
                    sleep(0.01)

            while(len(ba) > 0):
                ret, ba = self._parseReceived(ba)

        except BaseException as e:
            self.pvdata.Error = "Error SendIG:" + str(e)
            print(self.pvdata.Error, file=sys.stderr)

        return ret

    def GetAllData(self):
        if(not self.isreadingalready):
            self.isreadingalready = True
            try:
                self.pvdata.Error = "OK"  # we expect everything to be ok
                self.pvdata.Time = time()

                self.pvdata.VersionIFC = self.SendIG(Devices.DEV_IFCARD, 0, Commands.IFCCMD_GET_VERSION)
                # self.pvdata.DevType = self.SendIG(Devices.DEV_IFCARD, 0, Commands.IFCCMD_GET_DEVTYP, val=b'\x02\x40')
                self.pvdata.DevTime = self.SendIG(Devices.DEV_IFCARD, 0, Commands.IFCCMD_GET_TIME)
                self.pvdata.ActiveInvCnt = self.SendIG(Devices.DEV_IFCARD, 0, Commands.IFCCMD_GET_ACTIVE_INVERTER_CNT)
                self.pvdata.ActiveSensorCardCnt = self.SendIG(Devices.DEV_IFCARD, 0, Commands.IFCCMD_GET_SENSOR_CARD_CNT)
                self.pvdata.LocalNetStatus = self.SendIG(Devices.DEV_IFCARD, 0, Commands.IFCCMD_GET_LOCALNET_STATUS)

                # Nur wenn mindestens 1 Inverter aktiv ist 
                if(self.pvdata.ActiveInvCnt != 0):

                    self.pvdata.PTotal = 0
                    self.pvdata.PDayTotal = 0

                    for i in range(len(self.pvdata.wr)):
                        self.pvdata.wr[i].DevType = self.SendIG(Devices.DEV_INV, i, Commands.IFCCMD_GET_DEVTYP)
                        self.pvdata.wr[i].PDay = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_ENERGY_DAY)
                        self.pvdata.wr[i].PNow = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_POWER_NOW)
                        self.pvdata.wr[i].UDC = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_DC_VOLTAGE_NOW)
                        self.pvdata.wr[i].IDC = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_DC_CURRENT_NOW)
                        self.pvdata.wr[i].UAC = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_AC_VOLTAGE_NOW)
                        self.pvdata.wr[i].IAC = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_AC_CURRENT_NOW)
                        self.pvdata.wr[i].FAC = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_AC_FREQ_NOW)
                        # self.pvdata.wr[i].ATMP = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_AMBIENT_TEMP)
                        # self.pvdata.wr[i].FAN0 = self.SendIG(Devices.DEV_INV, i, Commands.INV_FAN_SPEED_0)
                        # self.pvdata.wr[i].FAN1 = self.SendIG(Devices.DEV_INV, i, Commands.INV_FAN_SPEED_1)
                        # self.pvdata.wr[i].FAN2 = self.SendIG(Devices.DEV_INV, i, Commands.INV_FAN_SPEED_2)
                        # self.pvdata.wr[i].FAN3 = self.SendIG(Devices.DEV_INV, i, Commands.INV_FAN_SPEED_3)
                        # self.pvdata.wr[i].STATUS = self.SendIG(Devices.DEV_INV, i, Commands.INV_STATUS)
                        self.pvdata.wr[i].OHDAY = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_OPERATING_HOURS_DAY)
                        self.pvdata.wr[i].OHYEAR = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_OPERATING_HOURS_YEAR)
                        self.pvdata.wr[i].OHTOT = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_OPERATING_HOURS_DAY)

                        self.pvdata.PTotal = self.pvdata.PTotal + self.pvdata.wr[i].PNow
                        self.pvdata.PDayTotal = self.pvdata.PDayTotal + self.pvdata.wr[i].PDay
                        self.pvdata.wr[i].EFF = (self.pvdata.wr[i].UAC * self.pvdata.wr[i].IAC)/(self.pvdata.wr[i].UDC * self.pvdata.wr[i].IDC)

                    

            except BaseException as e:
                self.pvdata.Error = "Error GetAllData:" + str(e)
                print(self.pvdata.Error, file=sys.stderr)
            finally:
                self.isreadingalready = False

        return self.pvdata


if __name__ == "__main__":
    fr = FroniusIG(2)  # 2 Wechselrichter
    fr.port = "COM9"
    fr.open()
    fr.GetAllData()
    print(jsons.dumps(fr.pvdata))
