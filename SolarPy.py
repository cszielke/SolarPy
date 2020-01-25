#!/usr/bin/env python3
import argparse
import configparser

import logging
import logging.handlers

import sys
import os.path
from time import sleep

from pv import FroniusIG
from pv import PVData
from pv import PVRestApi
from pv import PVSimulation
from pvmqtt import PVMqtt
from pvinflux import PVInflux
from pvmysql import PVMySQL
from pvhttpsrv import PVHttpSrv
from pvwebcam import PVWebCam
from pvweather import PVWeather

# region defaults
VERSION = "V0.1.1"

LOG_FILENAME = ""
LOG_BACKUP_COUNT = 3
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

CONFIG_FILENAME = "./solarpy.cfg"
DATASOURCE = 'simulation'

FRONIUSCOMPORT = ""

RESTHOST = "http://127.0.0.1"
RESTURL = "/rawdata.html"

# endregion defaults

config = configparser.ConfigParser()
pv = None
influxClient = PVInflux()
mysqlclient = PVMySQL()
mqttclient = PVMqtt()
httpsrv = PVHttpSrv()
webcam = PVWebCam()
pvweather = PVWeather()
pvdata = PVData()


def GetAllData():
    global pv
    global DATASOURCE
    global pvdata

    global RESTHOST
    global RESTURL

    print("GetAllData from {}".format(DATASOURCE))
    if(DATASOURCE == "ifcardeasy"):
        pv.GetAllData()
        pvdata = pv.pvdata
    elif(DATASOURCE == "restapi"):
        restapi = PVRestApi(host=RESTHOST, url=RESTURL)
        pvdata = restapi.GetPVDataRestApi()
    elif(DATASOURCE == "simulation"):
        sim = PVSimulation()
        pvdata = sim.GetPVDataSimulation()
    else:
        pvdata.Time = 0
        pvdata.Error = "Error: No valid datasource [ifcard,restapi,simulation]: (" + DATASOURCE + ")"
        print(pvdata.Error)
        exit(1)

    if(pvweather.enabled):
        pvweather.GetWeatherData()


def CheckArgsOrConfig(constantvar, argconfig, configsection, configtopic, type='str'):
    global config

    if(argconfig is not None):  # Argument has priority
        print("Var '{}.{}' from commandline set to {}".format(configsection, configtopic, argconfig))
        return argconfig
    else:
        # check for config
        if(config.has_option(configsection, configtopic)):
            if(type == 'str'):
                v = config.get(configsection, configtopic)
                print("Var '{}.{}' from config set to {} (str)".format(configsection, configtopic, v))
            elif(type == 'int'):
                v = config.getint(configsection, configtopic)
                print("Var '{}.{}' from config set to {} (int)".format(configsection, configtopic, v))
            else:
                print("Error CheckArgsOrConfig: unknown type")

            return v

    print("Var '{}.{}' from program default set to {} ".format(configsection, configtopic, constantvar))
    return constantvar


def OnDataRequest(self):
    global pvdata
    GetAllData()
    return pvdata, pvweather.weatherdata


def OnWebCamRequest(self, withdata=False):
    global webcam
    return webcam.GetWebCam(withdata)


def main():
    # region globals
    global CONFIG_FILENAME
    global LOG_FILENAME
    global LOG_BACKUP_COUNT
    global DATASOURCE

    global FRONIUSCOMPORT

    global RESTHOST
    global RESTURL

    global httpsrv
    global influxClient
    global mysqlclient
    global mqttclient
    global webcam
    global pvweather
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

    httpsrv.InitArguments(parser)
    influxClient.InitArguments(parser)
    mysqlclient.InitArguments(parser)
    mqttclient.InitArguments(parser)
    webcam.InitArguments(parser)
    pvweather.InitArguments(parser)

    args = parser.parse_args()
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
    if(LOG_FILENAME != ""):
        # Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
        # Give the logger a unique name (good practice)
        logger = logging.getLogger(__name__)
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
            islogging = False

            def __init__(self, logger, level, originalprint):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level
                self.originalprint = originalprint

            def write(self, message):
                if(self.islogging):
                    return
                self.islogging = True
                try:
                    # Only log if there is a message (not just a new line)
                    if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

                except BaseException as e:
                    backup = sys.stdout  # backup output
                    sys.stdout = self.originalprint  # set stdout to prevent recursion and stack overflow
                    print("LoggerError: {} Msg: {}".format(str(e), message.rstrip()))
                    sys.stdout = backup  # restore output
                    pass
                self.islogging = False

            def flush(self):
                # TODO: check if this is OK...
                pass

        # Replace stdout with logging to file at INFO level
        stdprintoriginal = sys.stdout
        sys.stdout = MyLogger(logger, logging.INFO, stdprintoriginal)
        # Replace stderr with logging to file at ERROR level
        stderroriginal = sys.stderr
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

    httpsrv.SetConfig(config, args)
    influxClient.SetConfig(config, args)
    mysqlclient.SetConfig(config, args)
    mqttclient.SetConfig(config, args)
    webcam.SetConfig(config, args)
    pvweather.SetConfig(config, args)
    # endregion default, configfile or commandline

    # region init datasources
    if(DATASOURCE == "ifcardeasy"):
        global pv
        # TODO: Anzahl WR automatisch ermitteln oder konfigurierbar machen
        pv = FroniusIG(2)
        pv.port = FRONIUSCOMPORT
        pv.open()
    elif(DATASOURCE == "restapi"):
        pass
    elif(DATASOURCE == "simulation"):
        pass
    else:
        print("Error: No valid datasource [ifcard,restapi,simulation]: (" + DATASOURCE + ")")
        exit(1)
    # endregion init datasources

    # region init destinations
    if(httpsrv.enabled):
        httpsrv.Connect(onDataRequest=OnDataRequest, onWebCamRequest=OnWebCamRequest)
        httpsrv.run()

    if(influxClient.enabled):
        influxClient.Connect()

    if(mysqlclient.enabled):
        mysqlclient.Connect()

    if(mqttclient.enabled):
        mqttclient.Connect(onDataRequest=OnDataRequest)

    if(webcam.enabled):
        webcam.Connect(onDataRequest=OnDataRequest)

    if(pvweather.enabled):
        pvweather.Connect()
    # endregion init destinations

    # region main loop
    try:
        print("Program is running...")
        mqttkacnt = mqttclient.keepalive
        mqttivalcnt = mqttclient.interval
        influxivalcnt = influxClient.interval
        mysqlivalcnt = mysqlclient.interval
        webcamcnt = webcam.interval
        while(True):
            sleep(1)
            mqttkacnt = mqttkacnt - 1
            mqttivalcnt = mqttivalcnt - 1
            influxivalcnt = influxivalcnt - 1
            mysqlivalcnt = mysqlivalcnt - 1
            webcamcnt = webcamcnt - 1
            # print("Counter: MQTT KeepAlive=",mqttkacnt,",MQTT interval=",mqttivalcnt,"InfluxDB Interval=",influxivalcnt,"\r", end = '')

            if(mqttclient.enabled):
                if(mqttivalcnt <= 0):
                    mqttivalcnt = mqttclient.interval
                    if(mqttclient.interval != 0):
                        print("Sending data via MQTT")
                        mqttclient.publishData()
                        mqttkacnt = 0  # do a keepalive!

                if(mqttkacnt <= 0):
                    mqttkacnt = mqttclient.keepalive
                    if(mqttclient.keepalive != 0):
                        print("Sending keepalive via MQTT")
                        mqttclient.publishKeepAlive()

            if(influxClient.enabled):
                if(influxivalcnt <= 0):
                    influxivalcnt = influxClient.interval
                    if(influxClient.interval != 0):
                        print("Saving to InfluxDB")
                        GetAllData()
                        influxClient.pvdata = pvdata
                        influxClient.SendData()

            if(mysqlclient.enabled):
                if(mysqlivalcnt <= 0):
                    mysqlivalcnt = mysqlclient.interval
                    if(mysqlclient.interval != 0):
                        print("Saving to MySQL")
                        GetAllData()
                        mysqlclient.pvdata = pvdata
                        mysqlclient.weatherdata = pvweather.weatherdata
                        mysqlclient.SendData()

            if(webcam.enabled):
                if(webcamcnt <= 0):
                    webcamcnt = webcam.interval
                    if(webcam.interval != 0):
                        print("Saving Webcam picture")
                        webcam.SaveWebCam()

    except KeyboardInterrupt:
        print("Key pressed! Exiting programm")
    # endregion main loop

    # region deinit destinations
    if(mqttclient.enabled):
        mqttclient.close()

    if(httpsrv.enabled):
        httpsrv.stop()

    # endregion deinit destinations

    # logger stop message
    print("SolarPy {} stopped.".format(VERSION))
    print("==================")
    return 0


if __name__ == "__main__":
    # execute only if run as a script
    sys.exit(main())
