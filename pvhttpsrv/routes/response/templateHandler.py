#!/usr/bin/env python3
from pv.data import PVData
from pvweather import PVWeather
from pvhttpsrv.routes.response.requestHandler import RequestHandler
import os
import io


class TemplateHandler(RequestHandler):
    pvdata = PVData()
    weatherdata = PVWeather()

    onDataRequest = None

    def __init__(self):
        super().__init__()
        self.contentType = 'text/html'

    def find(self, routeData):
        try:
            basedir = os.path.abspath(self.directory)

            filename = routeData['template']
            while(os.path.isabs(filename) and len(filename) > 0):  # begins with a "/"?
                filename = filename[1:]
            filename = os.path.join(basedir, filename.replace("..", ""))

            template_file = open(filename)
            contentstream = self.ReplaceTags(template_file)
            self.contents = contentstream
            self.setStatus(200)
            return True
        except Exception as e:
            print("Error TemplateHandler: " + str(e))
            self.setStatus(404)
            return False

    def ReplaceTags(self, source):
        if(self.onDataRequest is not None):
            self.pvdata, self.weatherdata = self.onDataRequest()

        text = source.read()
        desttext = text.replace("{{replacetags.version}}", "1.0.0")
        desttext = self.__replaceObjTags(desttext, self.pvdata, "pvdata.")
        desttext = self.__replaceObjTags(desttext, self.weatherdata, "weatherdata.")
        #Spezielle Tags
        dtstr = datetime.fromtimestamp(self.pvdata.Time).strftime("%Y-%m-%d %H:%M:%S")
        desttext = desttext.replace('{{pvdata.Time.text}}', dtstr)
        dest = io.StringIO(desttext)
        return dest

    def __replaceObjTags(self, text, obj, tagprefix=""):
        member = [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("__")]
        for key in member:
            if(isinstance(getattr(obj, key), list)):
                for i in range(len(getattr(obj, key))):
                    tagpre = tagprefix + key + str(i) + '.'
                    arrobj = getattr(obj, key)[i]
                    text = self.__replaceObjTags(text, arrobj, tagpre)
            else:
                tag = '{{' + tagprefix + key + '}}'
                value = str(getattr(obj, key))
                print("replace {}={}".format(tag, value))
                text = text.replace(tag, value)
        return text
