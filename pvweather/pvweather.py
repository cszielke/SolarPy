#!/usr/bin/env python3
from pvweather import WeatherData
from pvbasemodul import PVBaseModul
import datetime
import pytz
import sys
import requests
import math

local = pytz.timezone("Europe/Berlin")


class PVWeather(PVBaseModul):
    enabled = False
    url = "http://127.0.0.1/weatherdata.json"
    user = ""
    password = ""
    wsheight = 0

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
        parser.add_argument('-wtheight', '--weatherstationheight', help='Height of the weatherstation over NN', required=False)

    def SetConfig(self, config, args):
        super().SetConfig(config, args)
        configsection = "weather"
        self.enabled = self.CheckArgsOrConfig(config, self.enabled, args.weatherenable, configsection, "enabled", "bool")
        self.url = self.CheckArgsOrConfig(config, self.url, args.weatherurl, configsection, "url")
        self.user = self.CheckArgsOrConfig(config, self.user, args.weatherenable, configsection, "user")
        self.password = self.CheckArgsOrConfig(config, self.password, args.weatherenable, configsection, "password")
        self.wsheight = self.CheckArgsOrConfig(config, self.wsheight, args.weatherenable, configsection, "wsheight", "int")

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
                self.weatherdata.State = kvp["state"]

                # Berechnete Werte
                self.weatherdata.PressureAbs = self.GetAbsolutPressure(self.weatherdata.PressureRel, self.wsheight)
                self.weatherdata.Drewpoint = self.GetDrewPoint(self.weatherdata.Tout, self.weatherdata.Hout)
                self.weatherdata.Windchill = self.GetWindChill(self.weatherdata.Tout, self.weatherdata.Wind)
                self.weatherdata.WindDirName = self.GetWindDirName(self.weatherdata.WindDir)
                self.weatherdata.Tendency = "notvalid"
                self.weatherdata.Forecast = "notvalid"
                self.weatherdata.Storm = "notvalid"

                self.weatherdata.Error = "OK"
            else:
                self.weatherdata.Error = "Http Error: " + str(x.status_code)
                print(self.weatherdata.Error, file=sys.stderr)

        except Exception as e:
            self.weatherdata.Error = "Error:" + str(e)
            print(self.weatherdata.Error, file=sys.stderr)

        return self.weatherdata

    def GetWindDirName(self, degree):
        # Info von http://climate.umn.edu/snow_fence/Components/winddirectionanddegreeswithouttable3.htm
        if(degree <   0): return "Deg. negativ"  # noqa
        if(degree > 360): return "Deg > 360"  # noqa

        if((degree > 348.75) or (degree <=  11.25) ): return "N"  # noqa
        if((degree >  11.25) and (degree <=  33.75)): return "NNE"  # noqa
        if((degree >  33.75) and (degree <=  56.25)): return "NE"  # noqa
        if((degree >  56.25) and (degree <=  78.75)): return "ENE"  # noqa
        if((degree >  78.75) and (degree <= 101.25)): return "E"  # noqa
        if((degree > 101.25) and (degree <= 123.75)): return "ESE"  # noqa
        if((degree > 123.75) and (degree <= 146.25)): return "SE"  # noqa
        if((degree > 146.25) and (degree <= 168.75)): return "SSE"  # noqa
        if((degree > 168.75) and (degree <= 191.25)): return "S"  # noqa
        if((degree > 191.25) and (degree <= 213.75)): return "SSW"  # noqa
        if((degree > 213.75) and (degree <= 236.25)): return "SW"  # noqa
        if((degree > 236.25) and (degree <= 258.75)): return "WSW"  # noqa
        if((degree > 258.75) and (degree <= 281.25)): return "W"  # noqa
        if((degree > 281.25) and (degree <= 303.75)): return "WNW"  # noqa
        if((degree > 303.75) and (degree <= 326.25)): return "NW"  # noqa
        if((degree > 326.25) and (degree <= 348.75)): return "NNW"  # noqa

    def GetWindChill(self, temp, wind):
        # Calc Windchill (http://de.wikipedia.org/wiki/Windchill
        if (wind >= 5):
            windchill = round(13.12 + 0.6215 * temp - 11.37 * pow(wind, 0.16) + 0.3965 * temp * pow(wind, 0.16), 1)
        else:
            windchill = temp

        return windchill

    def GetDrewPoint(self, temp, humidity):
        # R = 287  # Gaskonstante Luft

        # Sättingungsdampfdruck in Abhängigkeit von der Temperatur

        if(temp >= 0):   # Sättigungsdampfdruck über Wasser
            a = 7.5
            b = 237.3
        else:
            a = 7.6
            b = 240.7

        sdd = 6.1078 * pow(10, ((a * temp) / (b + temp)))

        # Dampfdruck in Abhängigkeit von der Temperatur und der relativen Feuchte
        dd = humidity / 100 * sdd
        if(temp >= 0):
            a = 7.5
            b = 237.3
        else:
            a = 7.6
            b = 240.7

        c = math.log10(dd / 6.1078)

        drewpoint = round((b * c) / (a - c), 1)

        return drewpoint

    def GetAbsolutPressure(self, relpress, height):
        return round(((relpress * 100) / pow(1.0 - height / 44330.0, 5.255)) / 100, 1)
