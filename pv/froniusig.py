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

    def SendIG(self, dev, nr, cmd, val=bytearray(0)):
        try:
            length = len(val)

            if(length == 0):
                ba1 = pack(">BBBB", length, dev, nr + 1, cmd)
            else:
                ba1 = pack(">BBBB{}s".format(length), length, dev, nr + 1, cmd, val)

            # Checksumme berechnen
            chksum = 0  # Dummy checksum

            ba2 = pack(">BBB{}sB".format(len(ba1)), 0x80, 0x80, 0x80, ba1, chksum)

            ba = bytearray(ba2)
            # set correct checksum
            ba[len(ba) - 1] = self.CalcChkSum(ba)

            # Flush input Buffer
            self.ser.flushInput()

            # Send Command
            print("Send Device {}, Nr: {}, Command: {}, val: 0x{} ({})".format(dev, nr, cmd, val.hex(), ba2.hex()))
            self.ser.write_timeout = 0.5
            self.ser.write(ba)

        except BaseException as e:
            self.pvdata.Error = "Error SendIG:" + str(e)
            print(self.pvdata.Error, file=sys.stderr)

    def WaitForBytesAvail(self, cnt=1):
        timeout = 50  # Max 0,5 Sek auf min. cnt Zeichen warten
        while(self.ser.in_waiting < cnt and timeout > 0):
            sleep(0.01)
            timeout = timeout - 1

        if(timeout == 0):
            self.close()
            sleep(0.5)
            self.open()
            return False

        return True

    def CalcChkSum(self, ba):
        chksumcalced = 0
        for b in ba[3:len(ba) - 1]:
            chksumcalced = chksumcalced + b

        return chksumcalced & 0xff

    def CheckChkSum(self, chksum, ba):
        chksumcalced = self.CalcChkSum(ba)

        return chksum == chksumcalced

    def RecvIG(self):
        data = bytearray()
        try:
            ba = bytearray()
            if(not self.WaitForBytesAvail(cnt=7)):
                raise ValueError('Timeout receiving bytes')

            # Get available bytes
            ba += self.ser.read(size=7)

            # Check length again
            if(len(ba) < 7):
                raise ValueError('To less bytes received ({})'.format(len(ba)))

            # Startsequenz OK?
            if(ba[0] != 0x80 or ba[1] != 0x80 or ba[2] != 0x80):
                raise ValueError("Start sequence wrong")

            # get parameter
            datalength = ba[3]
            device = ba[4]
            number = ba[5]
            command = ba[6]

            # 3xStart + length + device + number + command + data[datalength] + checksum
            baLenNeeded = 3 + 1 + 1 + 1 + 1 + datalength + 1
            restbytescnt = baLenNeeded - len(ba)
            if(not self.WaitForBytesAvail(cnt=restbytescnt)):
                raise ValueError('Timeout receiving rest bytes')

            # Get available bytes
            ba += self.ser.read(size=restbytescnt)

            if(len(ba) < baLenNeeded):
                raise ValueError('To less rest bytes received ({})'.format(len(ba)))

            # we are here, so we have a complete sequence
            data += ba[7:(7 + datalength)]
            checksum = ba[baLenNeeded - 1]

            if(not self.CheckChkSum(checksum, ba)):
                raise ValueError('Checksum Error received')

            if(command == 0x0e):  # Error?
                c = data[0]
                nr = data[1]
                if(nr > 0 and nr < len(self.ERRORSTRINGS)):
                    print("Error Nr: " + str(nr) + "(" + self.ERRORSTRINGS[nr] + ") in cmd " + str(c))
                else:
                    print("Error Nr: " + str(nr))
                data = bytearray()  # clear Data

            elif(command == 0x0f):  # Status?
                c = data[0]
                nr = data[1]
                if(nr > 0 and nr < len(self.ERRORSTRINGS)):
                    print("Status Nr: " + str(nr) + "(" + self.ERRORSTRINGS[nr] + ") in cmd" + str(c))
                else:
                    print("Status Nr: " + str(nr))
                data = bytearray()  # clear Data

            # Check for another chunk of bytes available (Status or Error)
            if(self.ser.in_waiting > 0):
                self.RecvIG()  # recursive

        except BaseException as e:
            self.pvdata.Error = "Error SendIG:" + str(e)
            print(self.pvdata.Error, file=sys.stderr)

        print("Received Device {}, Number {}, Command {}, Length: {}, Value: {}, ({}) Incnt: {}".format(device, number, command, datalength, data, data.hex(), self.ser.in_waiting))

        return data

    def parseFloatValue(self, ba):
        val = 0
        if(len(ba) == 3):
            m, exp = unpack(">Hb", ba)
            val = round(m * pow(10, exp), 3)
        return val

    def GetAllData(self):
        if(not self.isreadingalready):
            self.isreadingalready = True
            try:
                # self.pvdata = PVData()  # Clear everything

                self.pvdata.Clear()

                self.pvdata.Error = "unknown Error"  # we expect an Error
                self.pvdata.Time = time()

                self.SendIG(Devices.DEV_IFCARD, 0, Commands.IFCCMD_GET_VERSION)
                self.pvdata.VersionIFC = self.RecvIG()  # Array of 4 bytes: IFC-Type, Maj, Min, Release

                # self.SendIG(Devices.DEV_IFCARD, 0, Commands.IFCCMD_GET_DEVTYP, val=b'\x02\x40')
                # self.pvdata.DevType = RecvIG()

                self.SendIG(Devices.DEV_IFCARD, 0, Commands.IFCCMD_GET_TIME)
                day, month, year, hour, minute, second = unpack(">BBBBBB", self.RecvIG())
                self.pvdata.DevTime = "{:02}.{:02}.{:02}T{:02}:{:02}:{:02}".format(day, month, year, hour, minute, second)

                self.SendIG(Devices.DEV_IFCARD, 0, Commands.IFCCMD_GET_ACTIVE_INVERTER_CNT)
                self.pvdata.ActiveInvCnt = self.RecvIG()  # Len = 0-Inverter count

                self.SendIG(Devices.DEV_IFCARD, 0, Commands.IFCCMD_GET_SENSOR_CARD_CNT)
                self.pvdata.ActiveSensorCardCnt = self.RecvIG()  # Len = 0 - Sensorcard Count

                self.SendIG(Devices.DEV_IFCARD, 0, Commands.IFCCMD_GET_LOCALNET_STATUS)
                val = self.RecvIG()
                if(len(val) > 0):
                    self.pvdata.LocalNetStatus = val[0]  # 1 byte

                self.pvdata.PTotal = 0
                self.pvdata.PDayTotal = 0

                # Nur wenn mindestens 1 Inverter aktiv ist
                if(len(self.pvdata.ActiveInvCnt) != 0):

                    for i in range(len(self.pvdata.wr)):
                        self.SendIG(Devices.DEV_INV, i, Commands.IFCCMD_GET_DEVTYP)
                        self.pvdata.wr[i].DevType = self.RecvIG()[0]  # 1 byte

                        self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_ENERGY_DAY)
                        self.pvdata.wr[i].PDay = self.parseFloatValue(self.RecvIG())

                        self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_POWER_NOW)
                        self.pvdata.wr[i].PNow = self.parseFloatValue(self.RecvIG())

                        self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_DC_VOLTAGE_NOW)
                        self.pvdata.wr[i].UDC = self.parseFloatValue(self.RecvIG())

                        self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_DC_CURRENT_NOW)
                        self.pvdata.wr[i].IDC = self.parseFloatValue(self.RecvIG())

                        self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_AC_VOLTAGE_NOW)
                        self.pvdata.wr[i].UAC = self.parseFloatValue(self.RecvIG())

                        self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_AC_CURRENT_NOW)
                        self.pvdata.wr[i].IAC = self.parseFloatValue(self.RecvIG())

                        self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_AC_FREQ_NOW)
                        self.pvdata.wr[i].FAC = self.parseFloatValue(self.RecvIG())

                        self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_OPERATING_HOURS_DAY)
                        self.pvdata.wr[i].OHDAY = self.parseFloatValue(self.RecvIG())

                        self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_OPERATING_HOURS_YEAR)
                        self.pvdata.wr[i].OHYEAR = self.parseFloatValue(self.RecvIG())

                        self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_OPERATING_HOURS_DAY)
                        self.pvdata.wr[i].OHTOT = self.parseFloatValue(self.RecvIG())
                        # self.pvdata.wr[i].ATMP = self.SendIG(Devices.DEV_INV, i, Commands.INV_GET_AMBIENT_TEMP)
                        # self.pvdata.wr[i].FAN0 = self.SendIG(Devices.DEV_INV, i, Commands.INV_FAN_SPEED_0)
                        # self.pvdata.wr[i].FAN1 = self.SendIG(Devices.DEV_INV, i, Commands.INV_FAN_SPEED_1)
                        # self.pvdata.wr[i].FAN2 = self.SendIG(Devices.DEV_INV, i, Commands.INV_FAN_SPEED_2)
                        # self.pvdata.wr[i].FAN3 = self.SendIG(Devices.DEV_INV, i, Commands.INV_FAN_SPEED_3)
                        # self.pvdata.wr[i].STATUS = self.SendIG(Devices.DEV_INV, i, Commands.INV_STATUS)

                        self.pvdata.PTotal = self.pvdata.PTotal + self.pvdata.wr[i].PNow
                        self.pvdata.PDayTotal = self.pvdata.PDayTotal + self.pvdata.wr[i].PDay

                        pab = (self.pvdata.wr[i].UAC * self.pvdata.wr[i].IAC)
                        pzu = (self.pvdata.wr[i].UDC * self.pvdata.wr[i].IDC)
                        if(pzu == 0):
                            self.pvdata.wr[i].EFF = 0
                        else:
                            self.pvdata.wr[i].EFF = round(pab / pzu, 3)

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
    fr = FroniusIG(2)  # 2 Wechselrichter
    fr.port = "COM9"
    fr.open()
    fr.GetAllData()
    print(jsons.dumps(fr.pvdata))
