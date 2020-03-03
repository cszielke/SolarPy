# Konfiguration

SolarPy kann umfangreich konfiguriert werden. Alle möglichen Parameter sind sowohl als Commandline Argument, als auch in der Konfigurationsdatei einstellbar.

## Commandline Arguments

```sh
>python ./SolarPy.py --help

usage: SolarPy.py [-h] [-cf CONFIGFILE] [-lf LOGFILE] [-lbc LOGBACKUPCOUNT]
                  [-ds DATASOURCE] [-c COMPORT] [-rh RESTHOST] [-ru RESTURL]
                  [-hse HTTPSRVENABLED] [-hsa HTTPSRVADDRESS]
                  [-hsp HTTPSRVPORT] [-hsd HTTPSRVDIRECTORY]
                  [-ixen INFLUXENABLED] [-ixh INFLUXHOST] [-ixp INFLUXPORT]
                  [-ixu INFLUXUSER] [-ixpw INFLUXPASSWORD]
                  [-idb INFLUXDATABASE] [-ii INFLUXINTERVAL]
                  [-mysen MYSQLENABLED] [-mysh MYSQLHOST] [-mysp MYSQLPORT]
                  [-mysu MYSQLUSER] [-myspw MYSQLPASSWORD]
                  [-mysdb MYSQLDATABASE] [-myst MYSQLTABLENAME]
                  [-mysi MYSQLINTERVAL] [-men MQTTENABLED] [-mb MQTTBROKER]
                  [-mp MQTTPORT] [-mid MQTTID] [-mu MQTTUSER]
                  [-mpw MQTTPASSWORD] [-mbt MQTTBASETOPIC] [-mbi MQTTINTERVAL]
                  [-mka MQTTKEEPALIVE] [-wcen WEBCAMENABLED]
                  [-wcurl WEBCAMURL] [-wcu WEBCAMUSERNAME]
                  [-wcpw WEBCAMPASSWORD] [-wci WEBCAMSAVEINTERVAL]
                  [-wct WEBCAMTTFFILE] [-wcsd WEBCAMSAVEDIRECTORY]
                  [-wten WEATHERENABLE] [-wturl WEATHERURL]
                  [-wtuser WEATHERUSER] [-wtpw WEATHERPASSWORD]
                  [-wtheight WEATHERSTATIONHEIGHT]

optional arguments:
  -h, --help            show this help message and exit
  -cf CONFIGFILE, --configfile CONFIGFILE
                        Name and path for config file
  -lf LOGFILE, --logfile LOGFILE
                        Name and path for log file
  -lbc LOGBACKUPCOUNT, --logbackupcount LOGBACKUPCOUNT
                        How much logfiles to keep
  -ds DATASOURCE, --datasource DATASOURCE
                        How to get PV-Data [restapi, ifcardeasy, simulation]
  -c COMPORT, --comport COMPORT
                        On witch ComPort is the IFCard connected
  -rh RESTHOST, --resthost RESTHOST
                        Host address for RESTApi
  -ru RESTURL, --resturl RESTURL
                        URL for RESTApi
  -hse HTTPSRVENABLED, --httpsrvenabled HTTPSRVENABLED
                        http server enabled
  -hsa HTTPSRVADDRESS, --httpsrvaddress HTTPSRVADDRESS
                        http server address
  -hsp HTTPSRVPORT, --httpsrvport HTTPSRVPORT
                        http server port
  -hsd HTTPSRVDIRECTORY, --httpsrvdirectory HTTPSRVDIRECTORY
                        http server directory
  -ixen INFLUXENABLED, --influxenabled INFLUXENABLED
                        influxdb enabled [True,False]
  -ixh INFLUXHOST, --influxhost INFLUXHOST
                        influxdb url/hostname
  -ixp INFLUXPORT, --influxport INFLUXPORT
                        influxdb port
  -ixu INFLUXUSER, --influxuser INFLUXUSER
                        influxdb username
  -ixpw INFLUXPASSWORD, --influxpassword INFLUXPASSWORD
                        influxdb password
  -idb INFLUXDATABASE, --influxdatabase INFLUXDATABASE
                        influxdb database name
  -ii INFLUXINTERVAL, --influxinterval INFLUXINTERVAL
                        influxdb data send interval
  -mysen MYSQLENABLED, --mysqlenabled MYSQLENABLED
                        MySQL enabled [True, False]
  -mysh MYSQLHOST, --mysqlhost MYSQLHOST
                        MySQL url/host
  -mysp MYSQLPORT, --mysqlport MYSQLPORT
                        MySQL port
  -mysu MYSQLUSER, --mysqluser MYSQLUSER
                        MySQL username
  -myspw MYSQLPASSWORD, --mysqlpassword MYSQLPASSWORD
                        MySQL password
  -mysdb MYSQLDATABASE, --mysqldatabase MYSQLDATABASE
                        MySQL database name
  -myst MYSQLTABLENAME, --mysqltablename MYSQLTABLENAME
                        MySQL Table name
  -mysi MYSQLINTERVAL, --mysqlinterval MYSQLINTERVAL
                        MySQL send interval
  -men MQTTENABLED, --mqttenabled MQTTENABLED
                        mqtt enabled [True,False]
  -mb MQTTBROKER, --mqttbroker MQTTBROKER
                        url for mqttbroker
  -mp MQTTPORT, --mqttport MQTTPORT
                        port for mqttbroker
  -mid MQTTID, --mqttid MQTTID
                        id for mqttbroker
  -mu MQTTUSER, --mqttuser MQTTUSER
                        user for mqttbroker
  -mpw MQTTPASSWORD, --mqttpassword MQTTPASSWORD
                        password for mqttbroker
  -mbt MQTTBASETOPIC, --mqttbasetopic MQTTBASETOPIC
                        basetopic for mqtt
  -mbi MQTTINTERVAL, --mqttinterval MQTTINTERVAL
                        data send interval for mqtt
  -mka MQTTKEEPALIVE, --mqttkeepalive MQTTKEEPALIVE
                        keepalive time for mqtt
  -wcen WEBCAMENABLED, --webcamenabled WEBCAMENABLED
                        webcam processing enabled
  -wcurl WEBCAMURL, --webcamurl WEBCAMURL
                        webcam URL
  -wcu WEBCAMUSERNAME, --webcamusername WEBCAMUSERNAME
                        webcam username
  -wcpw WEBCAMPASSWORD, --webcampassword WEBCAMPASSWORD
                        webcam password
  -wci WEBCAMSAVEINTERVAL, --webcamsaveinterval WEBCAMSAVEINTERVAL
                        webcam interval to save pictures
  -wct WEBCAMTTFFILE, --webcamttffile WEBCAMTTFFILE
                        webcam True-Type font file
  -wcsd WEBCAMSAVEDIRECTORY, --webcamsavedirectory WEBCAMSAVEDIRECTORY
                        webcam directory for saved pictures
  -wten WEATHERENABLE, --weatherenable WEATHERENABLE
                        Get weather enabled
  -wturl WEATHERURL, --weatherurl WEATHERURL
                        Get weather data url
  -wtuser WEATHERUSER, --weatheruser WEATHERUSER
                        Get weather username
  -wtpw WEATHERPASSWORD, --weatherpassword WEATHERPASSWORD
                        Get weather password
  -wtheight WEATHERSTATIONHEIGHT, --weatherstationheight WEATHERSTATIONHEIGHT
                        Height of the weatherstation over NN

```

## Konfigurationsdatei

Als Standard Name für die Konfigurationsdatei wird "solarpy.cfg" im gleichen Verzeichnis wie die Programmdatei verwendet. Per Kommandozeile kann dieser jedoch geändert werden.

### Beispiel

Im Basisverzeichnis befindet sich eine Datei namens "solarpy-default.cfg". Sie kann als Basis für eine eigene Konfigurationsdatei dienen.

```ini
[program]
#If no logfile is given, logging to stdout and stderror
#logfile=./solarpy.log
#logbackupcount=3

#How to get PV-Data: restapi, ifcardeasy, simulation
#datasource=ifcardeasy
#datasource=restapi
datasource=simulation

[fronius]
comport=COM3
baudrate=19200

[restapi]
host=http://127.0.0.1
url=/rawdata.html

[weather]
#set to False to switch weather feature off
enabled=False
url=http://127.0.0.1/weatherdata.txt
user=user
password=<secret>
#the height of the weatherstation in meter
wsheight=222

[influx]
#set to False to switch influxdb feature off
enabled=True
host=127.0.0.1
port=8086
user=admin
password=secret
database=pvtest
#Intervall for saving data in seconds. Set to 0 to turn off saving in intervalls.
interval=120

[mysql]
enabled = True
host=127.0.0.1
port=3306
user=user
password=secret
database=pvtest
tablename=Data
#Intervall for saving data in seconds. Set to 0 to turn off saving in intervalls.
interval=120

[mqtt]
#set to False to switch mqtt feature off
enabled=True
broker=test.mosquitto.org
id=SolarPyDefault1
port=1880
user=user
password=secret
#Intervall for saving data in seconds. Set to 0 to turn off saving in intervalls.
interval=120
keepalive=60

basetopic=solarpy/pv000001/

[httpserver]
enabled=True
srvaddress=127.0.0.1
port=8080
directory=./templates

[webcam]
enabled=True
url=http://localhost:80/image.jpg
#username=admin
#password=secret
saveinterval=120
ttffile=./Roboto-Regular.ttf
savedirectory=./templates/public/webcam/
```
