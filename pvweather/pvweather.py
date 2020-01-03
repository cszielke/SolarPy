#!/usr/bin/env python3
from pvweather import WeatherData
from pvbasemodul import PVBaseModul


class PVWeather(PVBaseModul):
    enabled = False
    url = "http://127.0.0.1/weatherdata.json"
    user = ""
    password = ""

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
        self.enabled = self.CheckArgsOrConfig(config, self.enabled, args.weatherenable, configsection, "enabled")
        self.url = self.CheckArgsOrConfig(config, self.enabled, args.weatherurl, configsection, "url")
        self.enabled = self.CheckArgsOrConfig(config, self.enabled, args.weatherenable, configsection, "user")
        self.enabled = self.CheckArgsOrConfig(config, self.enabled, args.weatherenable, configsection, "password")

    def GetWeatherData(self):
        return self.weatherdata.toJson()
