# Ausgabe Module

## Http-Server mit REST-API

### Templates

Der interne Webserver kann - sofern enabled - über die konfigurierte Adresse aufgerufen werden:

Per default ist das:

```http://localhost:8080/```

Der Inhalt dieser Seite kann den eigenen Bedürfnissen angepasst werden (template/index.html).

Folgende Tags werden durch aktuelle Daten ersetzt:

| Tag                            | Beschreibung                        |   Beispiel           |
|--------------------------------|-------------------------------------|----------------------|
| {{pvdata.ActiveInvCnt}}        | tbd.                                |                      |
| {{pvdata.ActiveSensorCardCnt}} | tbd.                                |                      |
| {{pvdata.DevTime}}             | tbd.                                |                      |
| {{pvdata.Error}}               | tbd.                                |                      |
| {{pvdata.LocalNetStatus}}      | tbd.                                |                      |
| {{pvdata.PDayTotal}}           | tbd.                                |                      |
| {{pvdata.PTotal}}              | tbd.                                |                      |
| {{pvdata.Time}}                | Messzeit als Timestamp              | 1578383866.0         |
| {{pvdata.VersionIFC}}          | tbd.                                |                      |
| {{pvdata.wr0.DevType}}         | tbd.                                |                      |
| {{pvdata.wr0.FAC}}             | tbd.                                |                      |
| {{pvdata.wr0.IAC}}             | tbd.                                |                      |
| {{pvdata.wr0.IDC}}             | tbd.                                |                      |
| {{pvdata.wr0.OHDAY}}           | tbd.                                |                      |
| {{pvdata.wr0.OHTOT}}           | tbd.                                |                      |
| {{pvdata.wr0.OHYEAR}}          | tbd.                                |                      |
| {{pvdata.wr0.PDay}}            | tbd.                                |                      |
| {{pvdata.wr0.PNow}}            | tbd.                                |                      |
| {{pvdata.wr0.UAC}}             | tbd.                                |                      |
| {{pvdata.wr0.UDC}}             | tbd.                                |                      |
| {{pvdata.wr1.DevType}}         | tbd.                                |                      |
| {{pvdata.wr1.FAC}}             | tbd.                                |                      |
| {{pvdata.wr1.IAC}}             | tbd.                                |                      |
| {{pvdata.wr1.IDC}}             | tbd.                                |                      |
| {{pvdata.wr1.OHDAY}}           | tbd.                                |                      |
| {{pvdata.wr1.OHTOT}}           | tbd.                                |                      |
| {{pvdata.wr1.OHYEAR}}          | tbd.                                |                      |
| {{pvdata.wr1.PDay}}            | tbd.                                |                      |
| {{pvdata.wr1.PNow}}            | tbd.                                |                      |
| {{pvdata.wr1.UAC}}             | tbd.                                |                      |
| {{pvdata.wr1.UDC}}             | tbd.                                |                      |
| {{weatherdata.Error}}          | tbd.                                |                      |
| {{weatherdata.Hin}}            | tbd.                                |                      |
| {{weatherdata.Hout}}           | tbd.                                |                      |
| {{weatherdata.MeasureTime}}    | tbd.                                |                      |
| {{weatherdata.PressureAbs}}    | tbd.                                |                      |
| {{weatherdata.PressureRel}}    | tbd.                                |                      |
| {{weatherdata.Rain1h}}         | tbd.                                |                      |
| {{weatherdata.Rain24h}}        | tbd.                                |                      |
| {{weatherdata.RainTotal}}      | tbd.                                |                      |
| {{weatherdata.State}}          | tbd.                                |                      |
| {{weatherdata.Tin}}            | tbd.                                |                      |
| {{weatherdata.Tout}}           | tbd.                                |                      |
| {{weatherdata.Wind}}           | tbd.                                |                      |
| {{weatherdata.WindAvg}}        | tbd.                                |                      |
| {{weatherdata.WindDir}}        | tbd.                                |                      |
| {{weatherdata.WindGust}}       | tbd.                                |                      |
| {{pvdata.Time.text}}           | pvdata.Time als Text                |'2020-01-23 08:43:07' |
| {{replacetags.version}}        | Version der Tag Ersetzung           |'1.0.0'               |

### Daten

#### Photovoltaik Anlage

Unter ```http://localhost:8080/pvdata.json``` können die aktuellen Daten der Solaranlage abgefragt werden. Man erhält eine JSON-Datei mit dieser Struktur:

```JSON
{
    "ActiveInvCnt": 258,
    "ActiveSensorCardCnt": 0,
    "DevTime": "7.1.20T13:56:29",
    "Error": "OK",
    "LocalNetStatus": 1,
    "PDayTotal": 2000,
    "PTotal": 859,
    "Time": 1578401760.712453,
    "VersionIFC": [1, 1, 1, 0],
    "wr": [{
            "DevType": 250,
            "EFF": 0.903,
            "FAC": 50.0,
            "IAC": 1.58,
            "IDC": 1.52,
            "OHDAY": 272,
            "OHTOT": 272,
            "OHYEAR": 2706,
            "PDay": 1000,
            "PNow": 367,
            "UAC": 232,
            "UDC": 267
        }, {
            "DevType": 250,
            "EFF": 0.907,
            "FAC": 50.0,
            "IAC": 2.14,
            "IDC": 2.18,
            "OHDAY": 283,
            "OHTOT": 283,
            "OHYEAR": 2777,
            "PDay": 1000,
            "PNow": 492,
            "UAC": 230,
            "UDC": 249
        }
    ]
}
```

#### Daten des Hostsystems

Unter ```http://localhost:8080/osdata.json``` können die aktuellen Daten des Host Systems abgefragt werden. Man erhält eine JSON-Datei mit dieser Struktur:

```JSON
{
    "BootTime": 1578298334.0,
    "Cpu": 17.6,
    "CpuFreq": {
        "current": 1596.0,
        "min": 0.0,
        "max": 1596.0
    },
    "Memory": {
        "total": 1064689664,
        "available": 286121984,
        "percent": 73.1,
        "used": 778567680,
        "free": 286121984
    },
    "Network": {
        "bytes_sent": 3558595771,
        "bytes_recv": 958812200,
        "packets_sent": 4336624,
        "packets_recv": 4099384,
        "errin": 0,
        "errout": 0,
        "dropin": 0,
        "dropout": 0
    },
    "PsUtilVersion": [5, 6, 7],
    "Temperatures": 0
}
```

Die Struktur kann unter Linux etwas anders aussehen

#### Wetterdaten

Unter ```http://localhost:8080/wsdata.json``` können die aktuellen Daten der Wetterstation abgefragt werden. Man erhält eine JSON-Datei mit dieser Struktur:

```JSON
{
    "Error": "OK",
    "Hin": 37.0,
    "Hout": 94.0,
    "MeasureTime": 1578402134.0,
    "PressureAbs": 1033.3,
    "PressureRel": 1033.3,
    "Rain1h": 0.0,
    "Rain24h": 0.0,
    "RainTotal": 3.9,
    "State": 0.0,
    "Tin": 23.5,
    "Tout": 5.5,
    "Wind": 1.4,
    "WindAvg": 0,
    "WindDir": 180.0,
    "WindGust": 2.0
}
```

Die Daten werde per Http von einem anderen System abgefragt.

## Webcam

Sofern das Bild einer Webcam per URL abgefragt werden kann (z.B. <http://www.example.com:80/img/ipcam.jpg>) , ist es möglich in das Bild die Daten der PV-Anlage zu implementieren. Das modifizierte Webcam Bild kann dann über den integrierten Webserver abgefragt werden (url: <http://localhost:8080/img/pvipcam.jpg)).>

Wenn gewüscht kann in konfigurierbaren Intervallen ein Bild gespeichert werden. Aus dieser Bilderserie kann dann zb. mit ffmpeg ein Video generiert werden, was den Tagesverlauf der Beschattung auf den Solarpanelen zeigt.

## InfluxDB

In konfigurierbaren Intervallen können die ermittelten Daten in einer Influx Datenbank gespeichert werden.

## MySQL

In konfigurierbaren Intervallen können die ermittelten Daten in einer MySQL / MariaDB Datenbank gespeichert werden.
