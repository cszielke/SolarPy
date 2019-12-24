# SolarPy

## Datenerfassung für Fronius Wechselrichter mit Fronius IG Interface Card/Box

Das Programm ist gedacht, um mittels eines Raspberry Pi's die Daten der Wechselrichter über das interne Netzwerk zur Verfügung zu stellen.

Es besteht die Möglichkeit die Daten in einer MySQL und/oder InfluxDB Datenbank zu archivieren.

Über eine REST-API Schnittstelle oder über MQTT können die Daten abgefragt werden. Andere Ausgabeschnittstellen sind leicht implementierbar.

Das Programm ist komplett in Python geschrieben und benötigt keine Oberfläche. Das Programm lässt sich umfangreich über eine CFG-Datei konfigurieren.

## Setup

ein Verzeichnis erzeugen und darin mittels

```git clone https://github.com/cszielke/SolarPy.git```

das Repository klonen.

Anschließend ```setup.bat``` für Windows, oder ```setup.sh``` für linux aufrufen um die Abhängigkeiten zu installieren.

Für die Konfiguration des Programms die Datei ```./fronius-default.cfg``` nach ```./fronius.cfg``` kopieren und anpassen.

Das Programm kann mit ```python3 ./fronius.py``` gestartet werden.

## Anwendung

### Http-Server mit REST-API

Der interne Webserver kann - sofern enabled - über die konfigurierte Adresse aufgerufen werden:

Per default ist das:

```http://localhost:8080/```

Der Inhalt dieser Seite kann den eigenen Bedürfnissen angepasst werden (template/index.html).

Unter ```http://localhost:8080/data.json``` können die aktuellen Daten der Solaranlage abgefragt werden. Man erhält eine JSON-Datei mit dieser Struktur:

```JSON
{
    "Error": "OK",
    "PDayGesamt": 20058.800000000003,
    "PGesamt": 28651.899999999998,
    "Time": 1577182434.6023476,
    "wr": [{
            "ATMP": 21,
            "FAC": 50,
            "FAN0": 1978,
            "FAN1": 2088,
            "FAN2": 2058,
            "FAN3": 3329,
            "IAC": 5,
            "IDC": 7,
            "OHDAY": 202.34,
            "OHTOT": 517660,
            "OHYEAR": 79650,
            "PDay": 810.2,
            "PNow": 1206.0,
            "STATUS": 2,
            "UAC": 232,
            "UDC": 179.96
        }, {
            "ATMP": 21,
            "FAC": 50,
            "FAN0": 1977,
            "FAN1": 2083,
            "FAN2": 2053,
            "FAN3": 3324,
            "IAC": 5,
            "IDC": 7,
            "OHDAY": 202.41,
            "OHTOT": 517660,
            "OHYEAR": 79650,
            "PDay": 809.5,
            "PNow": 1206.3,
            "STATUS": 2,
            "UAC": 232,
            "UDC": 179.96
        }
    ]
}

```

### InfluxDB

tbd.

### MySQL

tbd.
