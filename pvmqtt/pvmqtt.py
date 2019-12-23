
#!/usr/bin/env python3
from pv.data import PVData
import time
#Infos: http://www.steves-internet-guide.com/into-mqtt-python-client/
import paho.mqtt.client as mqtt

class PVMqtt:
    pvdata = PVData()
    client = None

    def __init__(self,host='127.0.0.1',id='foniusiginterfaceeasy1',user='',pw='',basetopic='fronius',onRequestData=None):
        self.host = host
        self.id = id
        self.user = user
        self.pw = pw
        self.basetopic = basetopic
        self.onRequestData = onRequestData

                #MQTT connect
        print("connecting to mqttbroker '{}' with client ID '{}'".format(self.host,self.id))
        self.client = mqtt.Client(client_id=self.id)
        self.client.username_pw_set(self.user, self.pw)
        self.client.on_log = self.on_log
        self.client.connect(self.host)
        
        print("Subscribing to topic",self.basetopic+'controller')
        self.client.subscribe(self.basetopic+'controller')
        self.client.on_message=self.on_message        #attach function to callback

        self.client.loop_start()    #start the loop

        t = time.time()
        print("Publishing message to topic '{}' with value '{}'".format(self.basetopic+"alive",t))
        self.client.publish(self.basetopic+"alive",t)

    def on_log(self,client, userdata, level, buf):
        levelstr = "INFO"
        if(level == 0x08):
            levelstr = "Error"
            
        print("MQTT log: {}: {}".format(levelstr,buf))

    def on_message(self,client, userdata, message):

        print("message received {}".format(str(message.payload.decode("utf-8"))))
        print("message topic={}".format(message.topic))
        print("message qos={}".format(message.qos))
        print("message retain flag={}".format(message.retain))

        self.publishData()

    def publishKeepAlive(self):
        t = time.time()
        print("Publishing message to topic '{}' with value '{}'".format(self.basetopic+"alive",t))
        self.client.publish(self.basetopic+"alive",t)

    def publishData(self):
        self._getData()
        self.client.publish(self.basetopic+"data/json",self.pvdata.toJson())
        print("Publishing message to topic '{}'".format(self.basetopic+"data/json"))

    def close(self):
        print("MQTT close..")
        print("Publishing message to topic '{}' with value '{}'".format(self.basetopic+"alive",0))
        self.client.publish(self.basetopic+"alive",0)

        self.client.loop_stop()    #stop the loop
        time.sleep(1)
        self.client.disconnect()

    def _getData(self):
        if(self.onRequestData != None):
            self.pvdata = self.onRequestData(self)