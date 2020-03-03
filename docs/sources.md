# Quellen

## Daten der Photovoltaik Anlage

Folgende Quellen für die PV-Daten sind Möglich:

* Fronius
* REST-Api
* Simulation

Es darf nur eine der Möglichkeiten aktiv sein. Welche das ist, kann in der Konfiguration angegeben werden.

### Fronius

Über eine Serielle Schnittstelle werden die Daten direkt von der InterfaceCard der Fronius Anlage geholt.

### REST-Api

Die Daten werden mittels Http-GET von einem anderen Server geholt. Die kann auch z.B. eine laufende Instanz auf einem Raspberry sein, die die Daten von der Fronius Anlage per Serieller Schnittstelle holt sein. Die Datenstruktur entspricht der Datei [rawdata.html](./templates/rawdata.html) im Verzeichnis "template".

Eine Anpassung an andere HTML Formate ist durch eine Programmänderung in der Datei [restapi.py](./pv/restapi.py) möglich. Dazu muss lediglich die Funktion "GetPVDataRestApi" angepasst werden.

### Simulation

Sollte kein Zugriff auf reale Daten vorhanden sein, kann mit diesen simulierten Daten zumindest das Programm getestet werden

## Wetter Daten

Um in den Ausgabe Modulen Wetter Daten zur Verfügung zu stellen, werden diese via REST-Api von einer Wetterstation geholt. Es wird eine Textdatei mit folgendem Inhalt erwartet:

```TEXT
DTime 2020-01-09 12:56:55
RHi 40
Ti 23.6
RHo 98
To 9.6
RP 1020.1
WS 1.4
WG 2.0
DIR 180
WDT S
Rtot 15.0
R24 10.2
R1H 1.1
state 00
```

Jede Zeile wird am ersten Leerzeichen in Key und Value getrennt. Welcher Key was bedeutet sollte offensichtlich sein.

## Daten des Host-Systems

SolarPy ermittelt Daten zum Rechner, auf dem es läuft und stellt diese über die Ausgabemodule zur Verfügung.
