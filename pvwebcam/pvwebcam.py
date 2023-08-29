#!/usr/bin/env python3

from pv.data import PVData
from pvweather import PVWeather
from pvbasemodul import PVBaseModul
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from datetime import datetime
import requests
import os
import io
import sys


class PVWebCam(PVBaseModul):
    pvdata = PVData()
    weatherdata = PVWeather()
    enabled = False
    url = ""
    username = ""
    password = ""
    ttffile = "./Roboto-Regular.ttf"
    savedirectory = "./template/webcam"
    interval = 120

    onDataRequest = None
    filename = "pv{}.jpg"

    def __init__(self):
        super().__init__()

    def InitArguments(self, parser):
        super().InitArguments(parser)
        parser.add_argument('-wcen', '--webcamenabled', help='webcam processing enabled', required=False)
        parser.add_argument('-wcurl', '--webcamurl', help='webcam URL', required=False)
        parser.add_argument('-wcu', '--webcamusername', help='webcam username', required=False)
        parser.add_argument('-wcpw', '--webcampassword', help='webcam password', required=False)
        parser.add_argument('-wci', '--webcamsaveinterval', help='webcam interval to save pictures', required=False)
        parser.add_argument('-wct', '--webcamttffile', help='webcam True-Type font file', required=False)
        parser.add_argument('-wcsd', '--webcamsavedirectory', help='webcam directory for saved pictures', required=False)

    def SetConfig(self, config, args):
        super().SetConfig(config, args)
        configsection = "webcam"
        self.enabled = self.CheckArgsOrConfig(config, self.enabled, args.webcamenabled, configsection, "enabled", "bool")
        self.url = self.CheckArgsOrConfig(config, self.url, args.webcamurl, configsection, "url")
        self.username = self.CheckArgsOrConfig(config, self.username, args.webcamusername, configsection, "username")
        self.password = self.CheckArgsOrConfig(config, self.password, args.webcampassword, configsection, "password")
        self.interval = self.CheckArgsOrConfig(config, self.interval, args.webcamsaveinterval, configsection, "saveinterval", "int")
        self.ttffile = self.CheckArgsOrConfig(config, self.interval, args.webcamsaveinterval, configsection, "ttffile")
        self.savedirectory = self.CheckArgsOrConfig(config, self.savedirectory, args.webcamsavedirectory, configsection, "savedirectory")

    def Connect(self, onDataRequest=None):
        print("PVWebCam.Connect() called")

        self.filename = "pv{}.jpg"

        self.onDataRequest = onDataRequest

    def GetWebCam(self, withdata=False):
        ba = bytearray()
        try:
            # response = requests.get(self.url)
            response = requests.get(self.url, verify=False,auth=(self.username, self.password))
            if(response.status_code >= 200 and response.status_code < 300):
                im = Image.open(io.BytesIO(response.content))
            else:
                raise ValueError('Error GetWebCam: Status Code {}'.format(response.status_code))
        except Exception as e:
            print("Error GetWebCam request: " + str(e), file=sys.stderr)
            im = self.GetErrorImage()

        try:
            if(withdata):
                self.pvdata, self.weatherdata = self.onDataRequest(self)
                # now = datetime.now()
                now = datetime.fromtimestamp(self.pvdata.Time)

                textpv = "{}, PDay: {} Wh, PNow: {} W, PNow1: {} W, PNow2: {} W".format(
                    now.strftime("%d.%m.%Y %H:%M:%S"),
                    int(self.pvdata.PDayTotal),
                    int(self.pvdata.PTotal),
                    int(self.pvdata.wr[0].PNow),
                    int(self.pvdata.wr[1].PNow))

                textw = "{}, Tout: {} Wind {}".format(
                    now.strftime("%d.%m.%Y %H:%M:%S"),
                    round(self.weatherdata.Tout, 1),
                    round(self.weatherdata.Wind, 1))

                width, height = im.size

                # Check for Font file
                if(not os.path.isfile(self.ttffile)):
                    raise ValueError('TTF-File not exist {}'.format(self.ttffile))
                font = ImageFont.truetype(self.ttffile, 16)

                draw = ImageDraw.Draw(im)
                draw.text((4, height - 18), textpv, (0, 0, 0), font=font)
                draw.text((2, height - 20), textpv, (255, 255, 255), font=font)
                draw.text((4, height - 38), textw, (0, 0, 0), font=font)
                draw.text((2, height - 40), textw, (255, 255, 255), font=font)

            ba = self.ImageToBytearray(im)
        except Exception as e:
            print("Error GetWebCam withdata: " + str(e), file=sys.stderr)

        return ba

    def SaveWebCam(self):
        try:
            webcam_ba = self.GetWebCam(withdata=True)
            im = self.ByteArrayToImage(webcam_ba)

            now = datetime.fromtimestamp(self.pvdata.Time)

            fnpath = os.path.join(self.savedirectory, now.strftime("%Y%m%d"))
            name = "pv{}.jpg".format(now.strftime("%H%M%S"))

            fn = os.path.join(fnpath, name)

            if(not os.path.exists(fnpath)):
                os.makedirs(fnpath)

            print("Save Webcam picture from {} to {}".format(self.url, fn))

            im.save(fn)  # , "JPEG", quality=80, optimize=True, progressive=True)
        except Exception as e:
            print("Error SaveWebCam: " + str(e), file=sys.stderr)

    def ImageToBytearray(self, image: Image):
        imgByteArr = io.BytesIO()
        try:
            image.save(imgByteArr, format='JPEG')  # image.format)
            imgByteArr = imgByteArr.getvalue()
        except Exception as e:
            print("Error ImageToBytearray: " + str(e), file=sys.stderr)

        return imgByteArr

    def ByteArrayToImage(self, ba: bytearray):
        try:
            im = Image.open(io.BytesIO(ba))
        except Exception as e:
            print("Error ByteArrayToImage: " + str(e), file=sys.stderr)
            im = self.GetErrorImage()
        return im

    def GetErrorImage(self):
        im = Image.new(mode="RGB", size=(640, 480), color=(153, 153, 153))
        im.format = 'JPEG'
        try:
            # Schönes Bild zeichnen :-)
            pass
        except Exception as e:
            print("Error GetErrorImage: " + str(e), file=sys.stderr)
        return im
