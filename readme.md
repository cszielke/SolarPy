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
    "PDayGesamt": 4000.0,
    "PGesamt": 325.0,
    "Time": 1577107367.0,
    "wr": [{
            "PDay": 2000.0,
            "PNow": 143.0,
            "UDC": 259.0,
            "IDC": 0.7,
            "UAC": 230.0,
            "IAC": 0.6,
            "FAC": 49.9
        }, {
            "PDay": 2000.0,
            "PNow": 182.0,
            "UDC": 237.0,
            "IDC": 0.9,
            "UAC": 230.0,
            "IAC": 0.8,
            "FAC": 49.9
        }
    ]
}

```

### InfluxDB

tbd.

### MySQL

tbd.
