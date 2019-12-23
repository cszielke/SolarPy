#!/usr/bin/env python3
from pvhttpsrv.routes.response.requestHandler import RequestHandler


class TemplateHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.contentType = 'text/html'

    def find(self, routeData):
        try:
            template_file = open('./templates/{}'.format(routeData['template']))
            self.contents = template_file
            self.setStatus(200)
            return True
        except Exception as e:
            print("Error TemplateHandler: " + str(e))
            self.setStatus(404)
            return False
