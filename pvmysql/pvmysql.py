#!/usr/bin/env python3
from pv.data import PVData
from pvweather import WeatherData
from pvbasemodul import PVBaseModul
import sys
import pymysql
import pytz

# infos: https://www.tutorialspoint.com/python3/python_database_access.htm


class PVMySQL(PVBaseModul):
    local = pytz.timezone("Europe/Berlin")
    pvdata = PVData()
    weatherdata = WeatherData()

    db = None
    cursor = None

    enabled = False
    host = '127.0.0.1'
    port = 3306
    username = 'admin'
    password = ''
    database = 'pvtest'
    tableName = 'Data'
    interval = 0

    def __init__(self):
        super().__init__()

    def InitArguments(self, parser):
        super().InitArguments(parser)
        parser.add_argument('-mysen', '--mysqlenabled', help='MySQL enabled [True, False]', required=False)
        parser.add_argument('-mysh', '--mysqlhost', help='MySQL url/host', required=False)
        parser.add_argument('-mysp', '--mysqlport', help='MySQL port', required=False)
        parser.add_argument('-mysu', '--mysqluser', help='MySQL username', required=False)
        parser.add_argument('-myspw', '--mysqlpassword', help='MySQL password', required=False)
        parser.add_argument('-mysdb', '--mysqldatabase', help='MySQL database name', required=False)
        parser.add_argument('-myst', '--mysqltablename', help='MySQL Table name', required=False)
        parser.add_argument('-mysi', '--mysqlinterval', help='MySQL send interval', required=False)

    def SetConfig(self, config, args):
        super().SetConfig(config, args)
        configsection = "mysql"
        self.enabled = self.CheckArgsOrConfig(config, self.enabled, args.mysqlenabled, configsection, "enabled", "bool")
        self.host = self.CheckArgsOrConfig(config, self.host, args.mysqlhost, configsection, "host")
        self.port = self.CheckArgsOrConfig(config, self.port, args.mysqlport, configsection, "port", "int")
        self.username = self.CheckArgsOrConfig(config, self.username, args.mysqluser, configsection, "user")
        self.password = self.CheckArgsOrConfig(config, self.password, args.mysqlpassword, configsection, "password")
        self.database = self.CheckArgsOrConfig(config, self.database, args.mysqldatabase, configsection, "database")
        self.tableName = self.CheckArgsOrConfig(config, self.tableName, args.mysqltablename, configsection, "tablename")
        self.interval = self.CheckArgsOrConfig(config, self.interval, args.mysqlinterval, configsection, "interval", "int")

    def Connect(self):
        print("PVMySQL.Connect() called")
        super().Connect()
        # connect database
        try:
            self.db = pymysql.connect(self.host, self.username, self.password, self.database)
            self.cursor = self.db.cursor()
        except Exception as e:
            print("Error MySQL: ", str(e), file=sys.stderr)

    def SendData(self):
        try:
            weatherfields = "`Windspeed`,`Winddirection`,`Outdoortemp`,`Outdoorhumidity`,"
            weatherfields = weatherfields + "`Drewpoint`,`Windchill`,`Indoortemp`,`Indoorhumidity`,"
            weatherfields = weatherfields + "`Rain1h`,`Rain24h`,`RainTotal`,`PressureRelativ`,`PressureAbsolut`,"
            weatherfields = weatherfields + "`ExtraValue1`,`ExtraValue2`,`ExtraValue3`,"
            weatherfields = weatherfields + "`Tendency`,`Forecast`,`Storm`,"
            weathervalues = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},'{}','{}','{}',".format(
                self.weatherdata.Wind,
                self.weatherdata.WindDir,
                self.weatherdata.Tout,
                self.weatherdata.Hout,
                self.weatherdata.Drewpoint,
                self.weatherdata.Windchill,
                self.weatherdata.Tin,
                self.weatherdata.Hin,
                self.weatherdata.Rain1h,
                self.weatherdata.Rain24h,
                self.weatherdata.RainTotal,
                self.weatherdata.PressureRel,
                self.weatherdata.PressureAbs,
                0,
                0,
                0,
                self.weatherdata.Tendency,
                self.weatherdata.Forecast,
                self.weatherdata.Storm
            )
            # self.weatherdata.WindAvg,
            # self.weatherdata.WindGust,
            # self.weatherdata.State,
            # self.weatherdata.Error
            # self.weatherdata.MeasureTime,

            wrfields = ""
            for wrn in range(len(self.pvdata.wr)):
                wrfields = wrfields + "`WR{0}WNow`,`WR{0}DCVNow`,`WR{0}DCANow`,`WR{0}ACVNow`,`WR{0}ACANow`,`WR{0}ACHzNow`,`WR{0}WDay`,".format(wrn + 1)
            wrfields = wrfields[:-1]

            wrvalues = ""
            for wrn in range(len(self.pvdata.wr)):
                wrvalues = wrvalues + "{},{},{},{},{},{},{},".format(
                    self.pvdata.wr[wrn].PNow,
                    self.pvdata.wr[wrn].UDC,
                    self.pvdata.wr[wrn].IDC,
                    self.pvdata.wr[wrn].UAC,
                    self.pvdata.wr[wrn].IAC,
                    self.pvdata.wr[wrn].FAC,
                    self.pvdata.wr[wrn].PDay
                )
            wrvalues = wrvalues[:-1]

            sql = "INSERT INTO {} ".format(self.tableName)
            sql = sql + " (`Index`,`Station`," + weatherfields + wrfields + ")"
            sql = sql + " VALUES('','PVAnlage'," + weathervalues + wrvalues + ")"

            try:
                # Execute the SQL command
                self.cursor.execute(sql)
                # Commit your changes in the database
                self.db.commit()
            except Exception as e:
                print("Error MySQL: " + str(e), file=sys.stderr)
                # Rollback in case there is any error
                self.db.rollback()

            print("Inserted MySQL dataset")
        except Exception as e:
            print("Error MySQL: " + str(e))

    def close(self):
        self.db.close()

    def CreateTable(self):
        createTableStr = """
            CREATE TABLE `Data` (
            `Index` BIGINT NOT NULL AUTO_INCREMENT ,
            `Station` VARCHAR( 30 ) NOT NULL ,
            `TimeStamp` TIMESTAMP NOT NULL ,
            `Windspeed` double NOT NULL DEFAULT '0',
            `Winddirection` double NOT NULL DEFAULT '0',
            `Outdoortemp` double NOT NULL DEFAULT '0',
            `Outdoorhumidity` double NOT NULL DEFAULT '0',
            `Drewpoint` double NOT NULL DEFAULT '0',
            `Windchill` double NOT NULL DEFAULT '0',
            `Indoortemp` double NOT NULL DEFAULT '0',
            `Indoorhumidity` double NOT NULL DEFAULT '0',
            `Rain1h` double NOT NULL DEFAULT '0',
            `Rain24h` double NOT NULL DEFAULT '0',
            `RainTotal` double NOT NULL DEFAULT '0',
            `PressureRelativ` double NOT NULL DEFAULT '0',
            `PressureAbsolut` double NOT NULL DEFAULT '0',
            `ExtraValue1` double NOT NULL DEFAULT '0',
            `ExtraValue2` double NOT NULL DEFAULT '0',
            `ExtraValue3` double NOT NULL DEFAULT '0',
            `Tendency` varchar(20) NOT NULL DEFAULT '',
            `Forecast` varchar(20) NOT NULL DEFAULT '',
            `Storm` varchar(20) NOT NULL DEFAULT '',
            `WR1WNow` DOUBLE NOT NULL ,
            `WR1DCVNow` DOUBLE NOT NULL ,
            `WR1DCANow` DOUBLE NOT NULL ,
            `WR1ACVNow` DOUBLE NOT NULL ,
            `WR1ACANow` DOUBLE NOT NULL ,
            `WR1ACHzNow` DOUBLE NOT NULL ,
            `WR1WDay` DOUBLE NOT NULL ,
            `WR2WNow` DOUBLE NOT NULL ,
            `WR2DCVNow` DOUBLE NOT NULL ,
            `WR2DCANow` DOUBLE NOT NULL ,
            `WR2ACVNow` DOUBLE NOT NULL ,
            `WR2ACANow` DOUBLE NOT NULL ,
            `WR2ACHzNow` DOUBLE NOT NULL ,
            `WR2WDay` DOUBLE NOT NULL ,
            PRIMARY KEY ( `Index` )
            )
            """
        try:
            # Execute the SQL command
            self.cursor.execute(createTableStr)
            # Commit your changes in the database
            self.db.commit()
        except Exception as e:
            print("Error CreateDatabase:", str(e))
            # Rollback in case there is any error
            self.db.rollback()
