#!/usr/bin/env python3

from pv.data import PVData
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

    enabled = False
    url = ""
    username = ""
    password = ""
    savedirectory = "./htdocs/webcam"
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
        parser.add_argument('-wcsd', '--webcamsavedirectory', help='webcam directory for saved pictures', required=False)

    def SetConfig(self, config, args):
        super().SetConfig(config, args)
        configsection = "webcam"
        self.enabled = self.CheckArgsOrConfig(config, self.enabled, args.webcamenabled, configsection, "enabled", "bool")
        self.url = self.CheckArgsOrConfig(config, self.url, args.webcamurl, configsection, "url")
        self.username = self.CheckArgsOrConfig(config, self.username, args.webcamusername, configsection, "username")
        self.password = self.CheckArgsOrConfig(config, self.password, args.webcampassword, configsection, "password")
        self.interval = self.CheckArgsOrConfig(config, self.interval, args.webcamsaveinterval, configsection, "saveinterval", "int")
        self.savedirectory = self.CheckArgsOrConfig(config, self.savedirectory, args.webcamsavedirectory, configsection, "savedirectory")

    def Connect(self, onDataRequest=None):
        if(not os.path.exists(self.savedirectory)):
            os.makedirs(self.savedirectory)

        self.filename = os.path.join(self.savedirectory, "pv{}.jpg")

        self.onDataRequest = onDataRequest

    def GetWebCam(self, withdata=False):
        ba = bytearray()
        try:
            response = requests.get(self.url)
            if(response.status_code >= 200 and response.status_code < 300):
                im = Image.open(io.BytesIO(response.content))
            else:
                raise ValueError('Error GetWebCam: Status Code {}'.format(response.status_code))
        except Exception as e:
            print("Error GetWebCam: " + str(e), file=sys.stderr)
            im = self.GetErrorImage()

        try:
            if(withdata):
                self.pvdata = self.onDataRequest(self)
                # now = datetime.now()
                now = datetime.fromtimestamp(self.pvdata.Time)

                text = "{}, PDay: {} Wh, PNow: {} W, PNow1: {} W, PNow2: {} W".format(
                    now.strftime("%d.%m.%Y %H:%M:%S"),
                    int(self.pvdata.PDayGesamt),
                    int(self.pvdata.PGesamt),
                    int(self.pvdata.wr[0].PNow),
                    int(self.pvdata.wr[1].PNow))

                width, height = im.size

                draw = ImageDraw.Draw(im)
                font = ImageFont.truetype("./Roboto-Regular.ttf", 16)
                draw.text((4, height - 18), text, (0, 0, 0), font=font)
                draw.text((2, height - 20), text, (255, 255, 255), font=font)

            ba = self.ImageToBytearray(im)
        except Exception as e:
            print("Error GetWebCam: " + str(e), file=sys.stderr)

        return ba

    def SaveWebCam(self):
        try:
            webcam_ba = self.GetWebCam(withdata=True)
            im = self.ByteArrayToImage(webcam_ba)

            now = datetime.fromtimestamp(self.pvdata.Time)
            fn = self.filename.format(now.strftime("%H%M%S"))

            print("Save Webcam picture from {} to {}".format(self.url, self.savedirectory))

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
