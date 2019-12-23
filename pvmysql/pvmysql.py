#!/usr/bin/env python3
from pv.data import PVData
import pymysql
import pytz

# infos: https://www.tutorialspoint.com/python3/python_database_access.htm


class PVMySQL:
    local = pytz.timezone("Europe/Berlin")
    pvdata = PVData()

    db = None
    cursor = None
    host = '127.0.0.1'
    port = 3306
    username = 'admin'
    password = ''
    database = 'pvtest'

    def __init__(self, host='127.0.0.1', port=3306, username='admin', password='', database='pvtest', tablename='Data'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

        self.tableName = tablename

        # connect database
        try:
            self.db = pymysql.connect(self.host, self.username, self.password, self.database)
            self.cursor = self.db.cursor()
        except Exception as e:
            print("Error MySQL: ", str(e))

    def SendData(self):
        try:
            wrfields = ""
            for wrn in range(len(self.pvdata.wr)):
                wrfields = wrfields + "`WR{0}WNow`,`WR{0}DCVNow`,`WR{0}DCANow`,`WR{0}ACVNow`,`WR{0}ACANow`,`WR{0}ACHzNow`,`WR{0}WDay`,".format(wrn+1)
            wrfields = wrfields[:-1]

            wrvalues = ""
            for wrn in range(len(self.pvdata.wr)):
                wrvalues = wrvalues + "{},{},{},{},{},{},{},".format(
                    self.pvdata.wr[wrn]["PNow"],
                    self.pvdata.wr[wrn]["UDC"],
                    self.pvdata.wr[wrn]["IDC"],
                    self.pvdata.wr[wrn]["UAC"],
                    self.pvdata.wr[wrn]["IAC"],
                    self.pvdata.wr[wrn]["FAC"],
                    self.pvdata.wr[wrn]["PDay"]
                )
            wrvalues = wrvalues[:-1]

            sql = "INSERT INTO {} ".format(self.tableName)
            sql = sql + "(`Index`,`Station`," + wrfields + ") VALUES('','PVAnlage'," + wrvalues + ")"

            try:
                # Execute the SQL command
                self.cursor.execute(sql)
                # Commit your changes in the database
                self.db.commit()
            except Exception as e:
                print("Error MySQL: "+str(e))
                # Rollback in case there is any error
                self.db.rollback()

            print("Inserted MySQL dataset")
        except Exception as e:
            print("Error MySQL: "+str(e))

    def close(self):
        self.db.close()

    def CreateTable(self):
        createTableStr = """
            CREATE TABLE `Data` (
            `Index` BIGINT NOT NULL AUTO_INCREMENT ,
            `Station` VARCHAR( 30 ) NOT NULL ,
            `TimeStamp` TIMESTAMP NOT NULL ,
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
            )"""
        try:
            # Execute the SQL command
            self.cursor.execute(createTableStr)
            # Commit your changes in the database
            self.db.commit()
        except Exception as e:
            print("Error CreateDatabase:", str(e))
            # Rollback in case there is any error
            self.db.rollback()
