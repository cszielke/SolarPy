#!/usr/bin/env python3
# pyright: reportConstantRedefinition=false
import argparse
import configparser

import logging
import logging.handlers

import sys
import os.path
from time import sleep
from typing import Any, Optional, TextIO

from pv import FroniusIG
from pv import SMA
from pv import PVData
from pv import PVRestApi
from pv import PVSimulation
from pvmqtt import PVMqtt
from pvinflux import PVInflux
from pvinflux import PVInflux2
from pvmysql import PVMySQL
from pvhttpsrv import PVHttpSrv
from pvwebcam import PVWebCam
from pvweather import PVWeather

# region defaults
VERSION = "V0.2.1"

LOG_FILENAME: str = ""
LOG_BACKUP_COUNT = 3
LOG_LEVEL: int = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

CONFIG_FILENAME = "./solarpy.cfg"
DATASOURCE = 'simulation'

FRONIUSCOMPORT: str = ""

RESTHOST = "http://127.0.0.1"
RESTURL = "/rawdata.html"

SMAIP = "192.168.15.165"
SMAPORT = 502
SMAUNIT = 3
# endregion defaults

config: configparser.ConfigParser = configparser.ConfigParser()
pv: Any = None
influxClient: Any = PVInflux()
influx2Client: Any = PVInflux2()
mysqlclient: Any = PVMySQL()
mqttclient: Any = PVMqtt()
httpsrv: Any = PVHttpSrv()
webcam: Any = PVWebCam()
pvweather: Any = PVWeather()
pvdata: PVData = PVData()


def GetAllData() -> None:
    global pvdata

    print("GetAllData from {}".format(DATASOURCE))
    if DATASOURCE == "ifcardeasy":
        if pv is not None:
            pv.GetAllData()
            pvdata = pv.pvdata
    elif DATASOURCE == "sma":
        if pv is not None:
            pv.GetAllData()
            pvdata = pv.pvdata
    elif DATASOURCE == "restapi":
        restapi: PVRestApi = PVRestApi(host=RESTHOST, url=RESTURL)
        pvdata = restapi.GetPVDataRestApi()
    elif DATASOURCE == "simulation":
        sim: PVSimulation = PVSimulation()
        pvdata = sim.GetPVDataSimulation()
    else:
        pvdata.Time = 0
        pvdata.Error = "Error: No valid datasource [ifcard,restapi,simulation]: (" + DATASOURCE + ")"
        print(pvdata.Error)
        raise SystemExit(1)

    if pvweather.enabled:
        pvweather.GetWeatherData()


def CheckArgsOrConfig(constantvar: Any, argconfig: Optional[Any], configsection: str, configtopic: str, type: str = "str") -> Any:
    if argconfig is not None:
        print("Var '{}.{}' from commandline set to {}".format(configsection, configtopic, argconfig))
        return argconfig

    if config.has_option(configsection, configtopic):
        if type == 'str':
            v: Any = config.get(configsection, configtopic)
            print("Var '{}.{}' from config set to {} (str)".format(configsection, configtopic, v))
        elif type == 'int':
            v = config.getint(configsection, configtopic)
            print("Var '{}.{}' from config set to {} (int)".format(configsection, configtopic, v))
        else:
            print("Error CheckArgsOrConfig: unknown type")
            return constantvar
        return v

    print("Var '{}.{}' from program default set to {} ".format(configsection, configtopic, constantvar))
    return constantvar


def OnDataRequest(_self: Any) -> tuple[Any, Any]:
    del _self
    GetAllData()
    return pvdata, pvweather.weatherdata


def OnWebCamRequest(_self: Any, withdata: bool = False) -> Any:
    del _self
    return webcam.GetWebCam(withdata)


def main() -> int:
    # region globals
    global CONFIG_FILENAME
    global LOG_FILENAME
    global LOG_BACKUP_COUNT
    global DATASOURCE

    global FRONIUSCOMPORT

    global RESTHOST
    global RESTURL

    global SMAIP
    global SMAPORT
    global SMAUNIT

    # global httpsrv
    # global influxClient
    # global influx2Client
    # global mysqlclient
    # global mqttclient
    # global webcam
    # global pvweather
    # endregion globals

    # region Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-cf', '--configfile', help='Name and path for config file', required=False)
    parser.add_argument('-lf', '--logfile', help='Name and path for log file', required=False)
    parser.add_argument('-lbc', '--logbackupcount', help='How much logfiles to keep', required=False)

    parser.add_argument('-ds', '--datasource', help='How to get PV-Data [restapi, ifcardeasy, simulation]', required=False)

    parser.add_argument('-c', '--comport', help='On witch ComPort is the IFCard connected', required=False)

    parser.add_argument('-rh', '--resthost', help='Host address for RESTApi', required=False)
    parser.add_argument('-ru', '--resturl', help='URL for RESTApi', required=False)

    parser.add_argument('-sip', '--smaip', help='IP for SMA Inverter', required=False)
    parser.add_argument('-sp', '--smaport', help='Port for SMA Inverter', required=False)
    parser.add_argument('-su', '--smaunit', help='Unit for SMA Inverter', required=False)

    httpsrv.InitArguments(parser)
    influxClient.InitArguments(parser)
    influx2Client.InitArguments(parser)
    mysqlclient.InitArguments(parser)
    mqttclient.InitArguments(parser)
    webcam.InitArguments(parser)
    pvweather.InitArguments(parser)

    args: argparse.Namespace = parser.parse_args()
    # endregion Argument parser

    # region configuration file
    if args.configfile:
        CONFIG_FILENAME = args.configfile
        if os.path.isfile(CONFIG_FILENAME):
            print("Found config file at commandline specified position '" + CONFIG_FILENAME + "'")
        else:
            raise ValueError("ERROR: config file at commandline specified position '" + CONFIG_FILENAME + "' not found")

    # try to read the config file
    print("try to read config file '" + CONFIG_FILENAME + "'")
    if os.path.isfile(CONFIG_FILENAME) is False:
        print("\nERROR: could not read config from '" + CONFIG_FILENAME + "'\n")
        return 1
    config.read(CONFIG_FILENAME)
    print("config file '" + CONFIG_FILENAME + "'  readed.")
    # endregion configuration file

    # region Logging
    LOG_FILENAME = CheckArgsOrConfig(LOG_FILENAME, args.logfile, "program", "logfile")
    LOG_BACKUP_COUNT = CheckArgsOrConfig(LOG_BACKUP_COUNT, args.logbackupcount, "program", "logbackupcount", type='int')
    if (LOG_FILENAME != ""):
        # Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
        # Give the logger a unique name (good practice)
        logger: logging.Logger = logging.getLogger(__name__)
        # Set the log level to LOG_LEVEL
        logger.setLevel(LOG_LEVEL)
        # Make a handler that writes to a file, making a new file at midnight and keeping 3 (default) backups
        handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=LOG_BACKUP_COUNT)
        # Format each log message like this
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        # Attach the formatter to the handler
        handler.setFormatter(formatter)
        # Attach the handler to the logger
        logger.addHandler(handler)

        # Make a class we can use to capture stdout and sterr in the log
        class MyLogger(object):
            islogging: bool = False

            def __init__(self, logger: logging.Logger, level: int, originalprint: TextIO) -> None:
                """Needs a logger and a logger level."""
                self.logger: logging.Logger = logger
                self.level: int = level
                self.originalprint: TextIO = originalprint

            def write(self, message: str) -> None:
                if self.islogging:
                    return
                self.islogging = True
                try:
                    # Only log if there is a message (not just a new line)
                    if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

                except BaseException as e:
                    backup: TextIO = sys.stdout
                    sys.stdout = self.originalprint
                    print("LoggerError: {} Msg: {}".format(str(e), message.rstrip()))
                    sys.stdout = backup
                self.islogging = False

            def flush(self) -> None:
                # TODO: check if this is OK...
                pass

        # Replace stdout with logging to file at INFO level
        stdprintoriginal: TextIO = sys.stdout
        sys.stdout = MyLogger(logger, logging.INFO, stdprintoriginal)
        # Replace stderr with logging to file at ERROR level
        stderroriginal: TextIO = sys.stderr
        sys.stderr = MyLogger(logger, logging.ERROR, stderroriginal)

    # logger start message
    print("SolarPy {} started.".format(VERSION))
    print("press Ctrl-C to stop...")
    print("==================")
    # endregion Logging

    # region default, configfile or commandline
    DATASOURCE = CheckArgsOrConfig(DATASOURCE, args.datasource, "program", "datasource")

    FRONIUSCOMPORT = CheckArgsOrConfig(FRONIUSCOMPORT, args.comport, "fronius", "comport")

    RESTHOST = CheckArgsOrConfig(RESTHOST, args.resthost, "restapi", "host")
    RESTURL = CheckArgsOrConfig(RESTURL, args.resturl, "restapi", "url")

    SMAIP = CheckArgsOrConfig(SMAIP, args.smaip, "sma", "ip")
    SMAPORT = CheckArgsOrConfig(SMAPORT, args.smaport, "sma", "port", type='int')
    SMAUNIT = CheckArgsOrConfig(SMAUNIT, args.smaunit, "sma", "unit", type='int')

    httpsrv.SetConfig(config, args)
    influxClient.SetConfig(config, args)
    influx2Client.SetConfig(config, args)
    mysqlclient.SetConfig(config, args)
    mqttclient.SetConfig(config, args)
    webcam.SetConfig(config, args)
    pvweather.SetConfig(config, args)
    # endregion default, configfile or commandline

    global pv
    # region init datasources
    if (DATASOURCE == "ifcardeasy"):
        # global pv
        # TODO: Anzahl WR automatisch ermitteln oder konfigurierbar machen
        pv = FroniusIG(2)
        pv.port = FRONIUSCOMPORT
        pv.open()
    elif (DATASOURCE == "sma"):
        # global pv
        pv = SMA(2)
        pv.ip = SMAIP
        pv.unit = SMAUNIT
        pv.port = SMAPORT
        pv.open()
    elif (DATASOURCE == "restapi"):
        pass
    elif (DATASOURCE == "simulation"):
        pass
    else:
        print("Error: No valid datasource [ifcard,restapi,simulation,sma]: (" + DATASOURCE + ")")
        exit(1)
    # endregion init datasources

    # region init destinations
    if (httpsrv.enabled):
        httpsrv.Connect(onDataRequest=OnDataRequest, onWebCamRequest=OnWebCamRequest)
        httpsrv.run()

    if (influxClient.enabled):
        influxClient.Connect()

    if (influx2Client.enabled):
        influx2Client.Connect()

    if (mysqlclient.enabled):
        mysqlclient.Connect()

    if (mqttclient.enabled):
        mqttclient.Connect(onDataRequest=OnDataRequest)

    if (webcam.enabled):
        webcam.Connect(onDataRequest=OnDataRequest)

    if (pvweather.enabled):
        pvweather.Connect()
    # endregion init destinations

    # region main loop
    try:
        print("Program is running...")
        mqttkacnt = mqttclient.keepalive
        mqttivalcnt = mqttclient.interval
        influxivalcnt = influxClient.interval
        influx2ivalcnt = influx2Client.interval
        mysqlivalcnt = mysqlclient.interval
        webcamcnt = webcam.interval

        while (True):
            sleep(1)
            mqttkacnt = mqttkacnt - 1
            mqttivalcnt = mqttivalcnt - 1
            influxivalcnt = influxivalcnt - 1
            influx2ivalcnt = influx2ivalcnt - 1
            mysqlivalcnt = mysqlivalcnt - 1
            webcamcnt = webcamcnt - 1
            # print("Counter: MQTT KeepAlive=",mqttkacnt,",MQTT interval=",mqttivalcnt,"InfluxDB Interval=",influxivalcnt,"\r", end = '')

            if (mqttclient.enabled):
                if (mqttivalcnt <= 0):
                    mqttivalcnt = mqttclient.interval
                    if (mqttclient.interval != 0):
                        print("Sending data via MQTT")
                        mqttclient.publishData()
                        mqttkacnt = 0  # do a keepalive!

                if (mqttkacnt <= 0):
                    mqttkacnt = mqttclient.keepalive
                    if (mqttclient.keepalive != 0):
                        print("Sending keepalive via MQTT")
                        mqttclient.publishKeepAlive()

            if (influxClient.enabled):
                if (influxivalcnt <= 0):
                    influxivalcnt = influxClient.interval
                    if (influxClient.interval != 0):
                        print("Saving to InfluxDB")
                        GetAllData()
                        influxClient.pvdata = pvdata
                        influxClient.SendData()

            if (influx2Client.enabled):
                if (influx2ivalcnt <= 0):
                    influx2ivalcnt = influx2Client.interval
                    if (influx2Client.interval != 0):
                        print("Saving to InfluxDB2")
                        GetAllData()
                        influx2Client.pvdata = pvdata
                        influx2Client.SendData()

            if (mysqlclient.enabled):
                if (mysqlivalcnt <= 0):
                    mysqlivalcnt = mysqlclient.interval
                    if (mysqlclient.interval != 0):
                        print("Saving to MySQL")
                        GetAllData()
                        mysqlclient.pvdata = pvdata
                        mysqlclient.weatherdata = pvweather.weatherdata
                        mysqlclient.SendData()

            if (webcam.enabled):
                if (webcamcnt <= 0):
                    webcamcnt = webcam.interval
                    if (webcam.interval != 0):
                        print("Saving Webcam picture")
                        webcam.SaveWebCam()

    except KeyboardInterrupt:
        print("Key pressed! Exiting programm")
    # endregion main loop

    # region deinit destinations
    if (mqttclient.enabled):
        mqttclient.close()

    if (httpsrv.enabled):
        httpsrv.stop()

    # endregion deinit destinations

    # logger stop message
    print("SolarPy {} stopped.".format(VERSION))
    print("==================")
    return 0


if __name__ == "__main__":
    # execute only if run as a script
    sys.exit(main())
