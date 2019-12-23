#!/usr/bin/env python3
import jsons
import json
from dataclasses import dataclass

@dataclass
class PVData:
    Error = "No Data"
    Time = 0
    PGesamt = 0
    PDayGesamt = 0
    wr = []

    def toJson(self):
        jsondata = str(jsons.dump(self)).replace("'",'"')
        return jsondata