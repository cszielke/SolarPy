#!/usr/bin/env python3
from pv.data import PVData
from pvbasemodul import PVBaseModul
import sys
import time
# Infos: http://www.steves-internet-guide.com/into-mqtt-python-client/
import paho.mqtt.client as mqtt


class PVMqtt(PVBaseModul):
    pvdata = PVData()
    client = None

    enabled = False
    host = '127.0.0.1'
    port = 1880
    id = 'foniusiginterfaceeasy1'
    user = ''
    pw = ''
    basetopic = 'solarpy/pv000001/'
    onDataRequest = None
    interval = 10
    keepalive = 120

    def __init__(self):
        pass

    def InitArguments(self, parser):
        super().InitArguments(parser)
        parser.add_argument('-men', '--mqttenabled', help='mqtt enabled [True,False]', required=False)
        parser.add_argument('-mb', '--mqttbroker', help='url for mqttbroker', required=False)
        parser.add_argument('-mp', '--mqttport', help='port for mqttbroker', required=False)
        parser.add_argument('-mid', '--mqttid', help='id for mqttbroker', required=False)
        parser.add_argument('-mu', '--mqttuser', help='user for mqttbroker', required=False)
        parser.add_argument('-mpw', '--mqttpassword', help='password for mqttbroker', required=False)
        parser.add_argument('-mbt', '--mqttbasetopic', help='basetopic for mqtt', required=False)
        parser.add_argument('-mbi', '--mqttinterval', help='data send interval for mqtt', required=False)
        parser.add_argument('-mka', '--mqttkeepalive', help='keepalive time for mqtt', required=False)

    def SetConfig(self, config, args):
        super().SetConfig(config, args)
        configsection = "mqtt"
        self.enabled = self.CheckArgsOrConfig(config, self.enabled, args.mqttenabled, configsection, "enabled", "bool")
        self.host = self.CheckArgsOrConfig(config, self.host, args.mqttbroker, configsection, "broker")
        self.port = self.CheckArgsOrConfig(config, self.port, args.mqttport, configsection, "port", "int")
        self.id = self.CheckArgsOrConfig(config, self.id, args.mqttid, configsection, "id")
        self.user = self.CheckArgsOrConfig(config, self.user, args.mqttuser, configsection, "user")
        self.pw = self.CheckArgsOrConfig(config, self.pw, args.mqttpassword, configsection, "password")
        self.basetopic = self.CheckArgsOrConfig(config, self.basetopic, args.mqttbasetopic, configsection, "basetopic")
        self.interval = self.CheckArgsOrConfig(config, self.interval, args.mqttinterval, configsection, "interval", "int")
        self.keepalive = self.CheckArgsOrConfig(config, self.keepalive, args.mqttkeepalive, configsection, "keepalive", "int")

    def Connect(self, onDataRequest=None):
        print("PVMqtt.Connect() called")
        super().Connect()
        # MQTT connect
        self.onDataRequest = onDataRequest

        print("connecting to mqttbroker '{}' with client ID '{}'".format(self.host, self.id))
        self.client = mqtt.Client(client_id=self.id)
        self.client.username_pw_set(self.user, self.pw)
        self.client.on_log = self.on_log
        self.client.connect(self.host)

        print("Subscribing to topic", self.basetopic + 'controller')
        self.client.subscribe(self.basetopic + 'controller')
        self.client.on_message = self.on_message        # attach function to callback

        self.client.loop_start()  # start the loop

        t = time.time()
        print("Publishing message to topic '{}' with value '{}'".format(self.basetopic + "alive", t))
        self.client.publish(self.basetopic + "alive", t)

    def on_log(self, client, userdata, level, buf):
        if(level == 0x08):
            levelstr = "Error"
            print("MQTT log: {}: {}".format(levelstr, buf), file=sys.stderr)
        else:
            levelstr = "INFO"
            print("MQTT log: {}: {}".format(levelstr, buf))

    def on_message(self, client, userdata, message):

        print("message received {}".format(str(message.payload.decode("utf-8"))))
        print("message topic={}".format(message.topic))
        print("message qos={}".format(message.qos))
        print("message retain flag={}".format(message.retain))

        self.publishData()

    def publishKeepAlive(self):
        t = time.time()
        print("Publishing message to topic '{}' with value '{}'".format(self.basetopic + "alive", t))
        self.client.publish(self.basetopic + "alive", t)

    def publishData(self):
        self._getData()
        self.client.publish(self.basetopic + "data/json", self.pvdata.toJson())
        print("Publishing message to topic '{}'".format(self.basetopic + "data/json"))

    def close(self):
        print("MQTT close..")
        print("Publishing message to topic '{}' with value '{}'".format(self.basetopic + "alive", 0))
        self.client.publish(self.basetopic + "alive", 0)

        self.client.loop_stop()  # stop the loop
        time.sleep(1)
        self.client.disconnect()

    def _getData(self):
        if(self.onDataRequest is not None):
            self.pvdata, self.weatherdata = self.onDataRequest(self)
