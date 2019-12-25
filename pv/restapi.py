#!/usr/bin/env python3
from pv.data import PVData, PVWR
import requests
import datetime
import pytz

local = pytz.timezone("Europe/Berlin")


class PVRestApi:
    pvdata = PVData()

    host = "http://127.0.0.1"
    url = "/rawdata.html"

    def __init__(self, host="http://127.0.0.1", url="/rawdata.html"):
        self.host = host
        self.url = url

    def LocalToUTC(self, naive):
        try:
            pst_now = local.localize(naive, is_dst=None)
        except (pytz.NonExistentTimeError):
            pst_now = local.localize(naive, is_dst=True)
        except (pytz.AmbiguousTimeError):
            pst_now = local.localize(naive, is_dst=False)

        utc_now = pst_now.astimezone(pytz.utc)
        return utc_now

    def GetPVDataRestApi(self):
        IP = self.host + self.url  # "http://192.168.15.160/rawdata.html"

        if(len(self.pvdata.wr) < 2):
            self.pvdata.wr.clear()
            self.pvdata.wr.append(PVWR())
            self.pvdata.wr.append(PVWR())

        try:
            x = requests.get(IP)
            # print(x.text)
            if(x.status_code == 200):
                # print("received data")
                kvp = {}
                for line in x.iter_lines(decode_unicode=True):
                    if(line.find(':') != -1):
                        # print(str(line))
                        line = line.replace("&nbsp;", "").replace("<br>", "")
                        key = line.split(':', 1)[0].replace(" ", "_")
                        value = line.split(':', 1)[1].replace(",", ".")
                        # print("Key: "+str(key)+" Value: "+str(value) )
                        kvp[key] = value

                self.pvdata.PGesamt = float(kvp["Gesamtleistung_AC"])
                self.pvdata.PDayGesamt = float(kvp["Tagesenerie_AC"])
                self.pvdata.Time = self.LocalToUTC(datetime.datetime.strptime(kvp["Messzeit"], ' %d.%m.%Y %H:%M:%S')).timestamp()

                self.pvdata.wr[0].IAC = float(kvp["Strom_AC_WR_1"])
                self.pvdata.wr[0].UAC = float(kvp["Spannung_AC_WR_1"])
                self.pvdata.wr[0].FAC = float(kvp["Freq._AC_WR_1"])
                self.pvdata.wr[0].IDC = float(kvp["Strom_DC_WR_1"])
                self.pvdata.wr[0].UDC = float(kvp["Spannung_DC_WR_1"])
                self.pvdata.wr[0].PDay = float(kvp["Tagesenerie_WR_1"])
                self.pvdata.wr[0].PNow = float(kvp["Leistung_WR_1"])

                self.pvdata.wr[1].IAC = float(kvp["Strom_AC_WR_2"])
                self.pvdata.wr[1].UAC = float(kvp["Spannung_AC_WR_2"])
                self.pvdata.wr[1].FAC = float(kvp["Freq._AC_WR_2"])
                self.pvdata.wr[1].IDC = float(kvp["Strom_DC_WR_2"])
                self.pvdata.wr[1].UDC = float(kvp["Spannung_DC_WR_2"])
                self.pvdata.wr[1].PDay = float(kvp["Tagesenerie_WR_2"])
                self.pvdata.wr[1].PNow = float(kvp["Leistung_WR_2"])

                self.pvdata.Error = "OK"
            else:
                self.pvdata.Error = "Http Error: " + str(x.status_code)
        except Exception as e:
            print("Error: " + str(e))

        return self.pvdata
