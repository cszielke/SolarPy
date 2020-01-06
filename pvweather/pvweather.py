#!/usr/bin/env python3
from pvweather import WeatherData
from pvbasemodul import PVBaseModul
import datetime
import pytz
import sys
import requests

local = pytz.timezone("Europe/Berlin")

class PVWeather(PVBaseModul):
    enabled = False
    url = "http://127.0.0.1/weatherdata.json"
    user = ""
    password = ""
    weatherdata = WeatherData()

    def __init__(self):
        super().__init__()
        self.weatherdata = WeatherData()
        pass

    def InitArguments(self, parser):
        super().InitArguments(parser)
        parser.add_argument('-wten', '--weatherenable', help='Get weather enabled', required=False)
        parser.add_argument('-wturl', '--weatherurl', help='Get weather data url', required=False)
        parser.add_argument('-wtuser', '--weatheruser', help='Get weather username', required=False)
        parser.add_argument('-wtpw', '--weatherpassword', help='Get weather password', required=False)

    def SetConfig(self, config, args):
        super().SetConfig(config, args)
        configsection = "weather"
        self.enabled = self.CheckArgsOrConfig(config, self.enabled, args.weatherenable, configsection, "enabled", "bool")
        self.url = self.CheckArgsOrConfig(config, self.enabled, args.weatherurl, configsection, "url")
        self.user = self.CheckArgsOrConfig(config, self.enabled, args.weatherenable, configsection, "user")
        self.password = self.CheckArgsOrConfig(config, self.enabled, args.weatherenable, configsection, "password")

    def LocalToUTC(self, naive):
        try:
            pst_now = local.localize(naive, is_dst=None)
        except (pytz.NonExistentTimeError):
            pst_now = local.localize(naive, is_dst=True)
        except (pytz.AmbiguousTimeError):
            pst_now = local.localize(naive, is_dst=False)

        utc_now = pst_now.astimezone(pytz.utc)
        return utc_now

    def GetWeatherData(self):
        IP = self.url  # "http://192.168.15.252/webcam/wsdata.txt"

        try:
            x = requests.get(IP)
            # print(x.text)
            if(x.status_code == 200):
                # print("received data")
                kvp = {}
                for line in x.iter_lines(decode_unicode=True):
                    if(line.find(' ') != -1):
                        # print(str(line))
                        key = line.split(' ', 1)[0]
                        value = line.split(' ', 1)[1].replace(",", ".")
                        # print("Key: "+str(key)+" Value: "+str(value) )
                        kvp[key] = value

                self.weatherdata.MeasureTime = self.LocalToUTC(datetime.datetime.strptime(kvp["DTime"], '%Y-%m-%d %H:%M:%S')).timestamp()
                self.weatherdata.Tout = float(kvp["To"])
                self.weatherdata.Tin = float(kvp["Ti"])
                self.weatherdata.Hout = float(kvp["RHo"])
                self.weatherdata.Hin = float(kvp["RHi"])
                self.weatherdata.Rain1h = float(kvp["R1H"])
                self.weatherdata.Rain24h = float(kvp["R24"])
                self.weatherdata.RainTotal = float(kvp["Rtot"])
                self.weatherdata.PressureAbs = float(kvp["RP"])
                self.weatherdata.PressureRel = float(kvp["RP"])
                self.weatherdata.Wind = float(kvp["WS"])
                self.weatherdata.WindGust = float(kvp["WG"])
                self.weatherdata.WindDir = float(kvp["DIR"])
                # self.weatherdata. = float(kvp["WDT"])
                self.weatherdata.State = float(kvp["state"])

                self.weatherdata.Error = "OK"
            else:
                self.weatherdata.Error = "Http Error: " + str(x.status_code)
                print(self.weatherdata.Error, file=sys.stderr)

        except Exception as e:
            self.weatherdata.Error = "Error:" + str(e)
            print(self.weatherdata.Error, file=sys.stderr)

        return self.weatherdata  # .toJson()
