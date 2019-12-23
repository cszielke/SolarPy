#!/usr/bin/env python3
import argparse
from time import sleep
import time

import logging
import logging.handlers

import sys
import configparser
import os.path
import threading

from pv import FroniusIG
from pv import PVData
from pv import PVRestApi
from pv import PVSimulation
from pvinflux import PVInflux
from pvmysql import PVMySQL
from pvhttpsrv import PVHttpSrv
from pvmqtt import PVMqtt

#region defaults
VERSION = "V0.1.0"
LOG_FILENAME=""
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"
CONFIG_FILENAME = "./fronius.cfg"
DATASOURCE = 'simulation'

INFLUXENABLED = False
INFLUXHOST ='127.0.0.1'
INFLUXPORT = 3306
INFLUXUSERNAME = 'admin'
INFLUXPASSWORD = ''
INFLUXDATABASE = 'pvtest'
INFLUXINTERVAL = 0

MYSQLENABLED = False
MYSQLHOST="127.0.0.1"
MYSQLPORT=8086
MYSQLUSERNAME="admin"
MYSQLPASSWORD=""
MYSQLDATABASE="pvtest"
MYSQLTABLENAME="Data"
MYSQLINTERVAL = 0

MQTTENABLED = False
MQTTBROKER = "test.mosquitto.org"
MQTTPORT = 1880
MQTTSERVERCLIENTID="foniusiginterfaceeasy1"
MQTTUSER = ""
MQTTPASSWORD = ""
MQTTBASETOPIC = "fronius/"
MQTTINTERVAL = 0
MQTTKEEPALIVE = 0

FRONIUSCOMPORT = ""

RESTHOST = "http://127.0.0.1"
RESTURL = "/rawdata.html"

HTTPSRVENABLED = False
HTTPSRVADDRESS = ""
HTTPSRVPORT=8080
HTTPSRVDIRECTORY = "./htdocs"

#endregion defaults

config = configparser.ConfigParser()
pv = None
influxClient = None
mqttclient = None
httpsrv = None

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
        restapi = PVRestApi(host=RESTHOST,url=RESTURL)
        pvdata=restapi.GetPVDataRestApi()
    elif(DATASOURCE == "simulation"):
        sim = PVSimulation()
        pvdata = sim.GetPVDataSimulation()
    else:
        pvdata.Time = 0
        pvdata.Error = "Error: No valid datasource [ifcard,restapi,simulation]: ("+DATASOURCE+")"
        print(pvdata.Error)
        exit(1)
    
def CheckArgsOrConfig(constantvar,argconfig,configsection,configtopic,type='str'):
    global config

    if(argconfig != None): #Argument has priority 
        print("Var '{}.{}' from commandline set to {}".format(configsection,configtopic,argconfig))
        return argconfig
    else:
        #check for config 
        if(config.has_option(configsection,configtopic)):
            if(type=='str'):
                v = config.get(configsection,configtopic)
                print("Var '{}.{}' from config set to {} (str)".format(configsection,configtopic,v))
            elif(type=='int'):
                v = config.getint(configsection,configtopic)
                print("Var '{}.{}' from config set to {} (int)".format(configsection,configtopic,v))
            else:
                print("Error CheckArgsOrConfig: unknown type")
            
            return v

    print("Var '{}.{}' from program default set to {} ".format(configsection,configtopic,constantvar))
    return constantvar

def OnDataRequest(self):
    global pvdata
    GetAllData()
    return pvdata

def main():
    #region globals
    global CONFIG_FILENAME
    global LOG_FILENAME
    global DATASOURCE

    global INFLUXENABLED
    global INFLUXHOST
    global INFLUXPORT
    global INFLUXUSERNAME
    global INFLUXPASSWORD
    global INFLUXDATABASE
    global INFLUXINTERVAL

    global MYSQLENABLED
    global MYSQLHOST
    global MYSQLPORT
    global MYSQLUSERNAME
    global MYSQLPASSWORD
    global MYSQLDATABASE
    global MYSQLTABLENAME
    global MYSQLINTERVAL

    global MQTTENABLED
    global MQTTBROKER
    global MQTTPORT
    global MQTTSERVERCLIENTID
    global MQTTUSER
    global MQTTPASSWORD  
    global MQTTBASETOPIC
    global MQTTINTERVAL
    global MQTTKEEPALIVE

    global FRONIUSCOMPORT

    global RESTHOST
    global RESTURL

    global HTTPSRVENABLED
    global HTTPSRVADDRESS
    global HTTPSRVPORT
    global HTTPSRVDIRECTORY
    #endregion globals

    #region Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-cf','--configfile', help='Name and path for config file', required=False)
    parser.add_argument('-lf','--logfile', help='Name and path for log file', required=False)
    parser.add_argument('-ds','--datasource', help='How to get PV-Data [restapi, ifcardeasy, simulation]', required=False)

    parser.add_argument('-ixen','--influxenabled', help='influxdb enabled [True,False]', required=False)
    parser.add_argument('-ixh','--influxhost', help='influxdb url/hostname', required=False)
    parser.add_argument('-ixp','--influxport', help='influxdb port', required=False)
    parser.add_argument('-ixu','--influxuser', help='influxdb username', required=False)
    parser.add_argument('-ixpw','--influxpassword', help='influxdb password', required=False)
    parser.add_argument('-idb','--influxdatabase', help='influxdb database name', required=False)
    parser.add_argument('-ii','--influxinterval', help='influxdb data send interval', required=False)

    parser.add_argument('-mysen','--mysqlenabled', help='MySQL enabled [True, False]', required=False)
    parser.add_argument('-mysh','--mysqlhost', help='MySQL url/host', required=False)
    parser.add_argument('-mysp','--mysqlport', help='MySQL port', required=False)
    parser.add_argument('-mysu','--mysqluser', help='MySQL username', required=False)
    parser.add_argument('-myspw','--mysqlpassword', help='MySQL password', required=False)
    parser.add_argument('-mysdb','--mysqldatabase', help='MySQL database name', required=False)
    parser.add_argument('-myst','--mysqltablename', help= 'MySQL Table name', required=False)
    parser.add_argument('-mysi','--mysqlinterval', help='MySQL send interval', required=False)

    parser.add_argument('-men','--mqttenabled', help='mqtt enabled [True,False]', required=False)
    parser.add_argument('-mb','--mqttbroker', help='url for mqttbroker', required=False)
    parser.add_argument('-mp','--mqttport', help='port for mqttbroker', required=False)
    parser.add_argument('-mid','--mqttid', help='id for mqttbroker', required=False)
    parser.add_argument('-mu','--mqttuser', help='user for mqttbroker', required=False)
    parser.add_argument('-mpw','--mqttpassword', help='password for mqttbroker', required=False)
    parser.add_argument('-mbt','--mqttbasetopic', help='basetopic for mqtt', required=False)
    parser.add_argument('-mbi','--mqttinterval', help='data send interval for mqtt', required=False)
    parser.add_argument('-mka','--mqttkeepalive', help='keepalive time for mqtt', required=False)
    
    parser.add_argument('-c','--comport', help='On witch ComPort is the IFCard connected', required=False)

    parser.add_argument('-rh','--resthost', help='Host address for RESTApi', required=False)
    parser.add_argument('-ru','--resturl', help='URL for RESTApi', required=False)

    parser.add_argument('-hse','--httpsrvenabled', help='http server enabled', required=False)
    parser.add_argument('-hsa','--httpsrvaddress', help='http server address', required=False)
    parser.add_argument('-hsp','--httpsrvport', help='http server port', required=False)
    parser.add_argument('-hsd','--httpsrvdirectory', help='http server directory', required=False)

    args = parser.parse_args()
    #endregion Argument parser

    #region configuration file
    if args.configfile:
        CONFIG_FILENAME = args.configfile
        if os.path.isfile(CONFIG_FILENAME):
            print("Found config file at commandline specified position '" + CONFIG_FILENAME + "'")
        else:
            print("ERROR: config file at commandline specified position '" + CONFIG_FILENAME + "' not found")
            exit(1)

    #try to read the config file
    print("try to read config file '" + CONFIG_FILENAME + "'")
    if os.path.isfile(CONFIG_FILENAME) == False:
        print("\nERROR: could not read config from '" + CONFIG_FILENAME + "'\n")
        exit(1)
    config.read(CONFIG_FILENAME)
    print("config file '" + CONFIG_FILENAME + "'  readed.")
    #endregion configuration file

    #region Logging
    LOG_FILENAME = CheckArgsOrConfig(LOG_FILENAME,args.logfile,"program","logfile")
    if(LOG_FILENAME != ""):
        # Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
        # Give the logger a unique name (good practice)
        logger = logging.getLogger(__name__)
        # Set the log level to LOG_LEVEL
        logger.setLevel(LOG_LEVEL)
        # Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
        handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
        # Format each log message like this
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        # Attach the formatter to the handler
        handler.setFormatter(formatter)
        # Attach the handler to the logger
        logger.addHandler(handler)

        # Make a class we can use to capture stdout and sterr in the log
        class MyLogger(object):
                def __init__(self, logger, level):
                        """Needs a logger and a logger level."""
                        self.logger = logger
                        self.level = level

                def write(self, message):
                        # Only log if there is a message (not just a new line)
                        if message.rstrip() != "":
                                self.logger.log(self.level, message.rstrip())
                def flush(self):
                    #TODO: check if this is OK...
                    pass

        # Replace stdout with logging to file at INFO level
        sys.stdout = MyLogger(logger, logging.INFO)
        # Replace stderr with logging to file at ERROR level
        sys.stderr = MyLogger(logger, logging.ERROR)

    #logger start message
    print("fronius.py {} started.".format(VERSION) )
    print("==================")
    #endregion Logging

    #region default, configfile or commandline
    DATASOURCE = CheckArgsOrConfig(INFLUXHOST,args.datasource,"program","datasource")

    INFLUXENABLED = CheckArgsOrConfig(INFLUXENABLED,args.influxenabled,"influx","enabled")
    INFLUXHOST = CheckArgsOrConfig(INFLUXHOST,args.influxhost,"influx","host")
    INFLUXPORT = CheckArgsOrConfig(INFLUXPORT,args.influxport,"influx","port","int")
    INFLUXUSERNAME = CheckArgsOrConfig(INFLUXUSERNAME,args.influxuser,"influx","user")
    INFLUXPASSWORD = CheckArgsOrConfig(INFLUXPASSWORD,args.influxpassword,"influx","password")
    INFLUXDATABASE = CheckArgsOrConfig(INFLUXDATABASE,args.influxdatabase,"influx","database")
    INFLUXINTERVAL = CheckArgsOrConfig(INFLUXINTERVAL,args.influxinterval,"influx","interval","int")

    MYSQLENABLED = CheckArgsOrConfig(MYSQLENABLED,args.mysqlenabled,"mysql","enabled")
    MYSQLHOST = CheckArgsOrConfig(MYSQLHOST,args.mysqlhost,"mysql","host")
    MYSQLPORT = CheckArgsOrConfig(MYSQLPORT,args.mysqlport,"mysql","port","int")
    MYSQLUSERNAME = CheckArgsOrConfig(MYSQLUSERNAME,args.mysqluser,"mysql","user")
    MYSQLPASSWORD = CheckArgsOrConfig(MYSQLPASSWORD,args.mysqlpassword,"mysql","password")
    MYSQLDATABASE = CheckArgsOrConfig(MYSQLDATABASE,args.mysqldatabase,"mysql","database")
    MYSQLTABLENAME = CheckArgsOrConfig(MYSQLTABLENAME,args.mysqltablename,"mysql","tablename")
    MYSQLINTERVAL = CheckArgsOrConfig(MYSQLINTERVAL,args.mysqlinterval,"mysql","interval","int")

    MQTTENABLED = CheckArgsOrConfig(MQTTBROKER,args.mqttenabled,"mqtt","enabled")
    MQTTBROKER = CheckArgsOrConfig(MQTTBROKER,args.mqttbroker,"mqtt","broker")
    MQTTPORT = CheckArgsOrConfig(MQTTPORT,args.mqttport,"mqtt","port","int")
    MQTTSERVERCLIENTID = CheckArgsOrConfig(MQTTSERVERCLIENTID,args.mqttid,"mqtt","id")
    MQTTUSER = CheckArgsOrConfig(MQTTUSER,args.mqttuser,"mqtt","user")
    MQTTPASSWORD = CheckArgsOrConfig(MQTTPASSWORD,args.mqttpassword,"mqtt","password")
    MQTTBASETOPIC = CheckArgsOrConfig(MQTTBASETOPIC,args.mqttbasetopic,"mqtt","basetopic")
    MQTTINTERVAL = CheckArgsOrConfig(MQTTINTERVAL,args.mqttinterval,"mqtt","interval","int")
    MQTTKEEPALIVE = CheckArgsOrConfig(MQTTKEEPALIVE,args.mqttkeepalive,"mqtt","keepalive","int")

    FRONIUSCOMPORT = CheckArgsOrConfig(FRONIUSCOMPORT,args.comport,"fronius","comport")

    RESTHOST = CheckArgsOrConfig(RESTHOST,args.resthost,"restapi","host")
    RESTURL = CheckArgsOrConfig(RESTURL,args.resturl,"restapi","url")

    HTTPSRVENABLED = CheckArgsOrConfig(RESTURL,args.httpsrvenabled,"httpserver","enabled")
    HTTPSRVADDRESS = CheckArgsOrConfig(HTTPSRVADDRESS,args.httpsrvaddress,"httpserver","srvaddress")
    HTTPSRVPORT = CheckArgsOrConfig(RESTURL,args.httpsrvport,"httpserver","port","int")
    HTTPSRVDIRECTORY = CheckArgsOrConfig(RESTURL,args.httpsrvdirectory,"httpserver","directory")
    #endregion default, configfile or commandline

    #region init datasources
    if(DATASOURCE == "ifcardeasy"):
        global pv
        #TODO: Anzahl WR automatisch ermitteln oder konfigurierbar machen
        pv = FroniusIG(2)
        pv.port = FRONIUSCOMPORT
        pv.open()
    elif(DATASOURCE == "restapi"):
        pass
    elif(DATASOURCE == "simulation"):
        pass
    else:
        print("Error: No valid datasource [ifcard,restapi,simulation]: ("+DATASOURCE+")")
        exit(1)
    #endregion init datasources
    
    #region init destinations
    if(MQTTENABLED):
        mqttclient = PVMqtt(host=MQTTBROKER,id=MQTTSERVERCLIENTID,user=MQTTUSER,pw=MQTTPASSWORD,
            basetopic=MQTTBASETOPIC,onRequestData=OnDataRequest)

    if(INFLUXENABLED):
        influxClient = PVInflux(host=INFLUXHOST,port=INFLUXPORT,
            username=INFLUXUSERNAME,password=INFLUXPASSWORD,database=INFLUXDATABASE)

    if(HTTPSRVENABLED):
        httpsrv = PVHttpSrv(
            serveraddress=HTTPSRVADDRESS,
            port=HTTPSRVPORT,
            directory=HTTPSRVDIRECTORY,
            onDataRequest=OnDataRequest)
        httpsrv.run()

    if(MYSQLENABLED):
        mysqlclient = PVMySQL(
            host=MYSQLHOST, 
            username=MYSQLUSERNAME,
            password=MYSQLPASSWORD,
            database=MYSQLDATABASE,
            tablename=MYSQLTABLENAME)
    #endregion init destinations

    #region main loop
    try:
        print("Program is running...")
        mqttkacnt = MQTTKEEPALIVE
        mqttivalcnt = MQTTINTERVAL
        influxivalcnt = INFLUXINTERVAL
        mysqlivalcnt = MYSQLINTERVAL
        while(True):
            sleep(1)
            mqttkacnt = mqttkacnt - 1
            mqttivalcnt = mqttivalcnt - 1
            influxivalcnt = influxivalcnt - 1
            mysqlivalcnt = mysqlivalcnt -1
            #print("Counter: MQTT KeepAlive=",mqttkacnt,",MQTT interval=",mqttivalcnt,"InfluxDB Interval=",influxivalcnt,"\r", end = '')
            
            if(MQTTENABLED):
                if(mqttivalcnt <= 0):
                    mqttivalcnt = MQTTINTERVAL
                    if(MQTTINTERVAL != 0):
                        print("Sending data via MQTT")
                        mqttclient.publishData()
                        mqttkacnt = 0 #do a keepalive!

                if(mqttkacnt <= 0):
                    mqttkacnt = MQTTKEEPALIVE
                    if(MQTTKEEPALIVE != 0):
                        print("Sending keepalive via MQTT")
                        mqttclient.publishKeepAlive()

            if(INFLUXENABLED):
                if(influxivalcnt <= 0):
                    influxivalcnt = INFLUXINTERVAL
                    if(INFLUXINTERVAL != 0):
                        print("Saving to InfluxDB")
                        GetAllData()
                        influxClient.pvdata = pvdata
                        influxClient.SendData()
            if(MYSQLENABLED):
                if(mysqlivalcnt <= 0):
                    mysqlivalcnt = MYSQLINTERVAL
                    if(MYSQLINTERVAL != 0):
                        print("Saving to MySQL")
                        GetAllData()
                        mysqlclient.pvdata = pvdata
                        mysqlclient.SendData()
    except KeyboardInterrupt:
        print("Key pressed! Exiting programm")
    #endregion main loop

    #region deinit destinations
    if(MQTTENABLED):
        mqttclient.close()

    if(HTTPSRVENABLED):
        httpsrv.stop()

    #endregion deinit destinations

    #logger stop message
    print("fronius.py {} stopped.".format(VERSION) )
    print("==================")
    exit(0)


if __name__ == "__main__":
    # execute only if run as a script
    main()