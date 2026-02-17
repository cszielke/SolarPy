# Todo's

## Allgemein

* Eventuell PV- Daten zyklisch holen und nicht auf Anforderung (schnellere Antwortzeit)
* Zu erwartende Anzahl an Bytes auf der seriellen Schnittstelle (length Byte) ermittlen und bei Erhalt sofort weiter im Programm. Erhöht die Geschwindigkeit des Lesens.
* Konfigurierbarkeit über MQTT und Http (Sicherheit?)
* Http-Server auch über https
* Logging via MQTT/Http
* Scripte zur Erzeugung von videos am Tagesende aufrufen:
  `.\scripts\makeallpvvideos.ps1 \\192.168.15.241\web\html\webcam \\192.168.15.241\web\html\webcam\videos`
* Strategie zum löschen der Tagesbilder nach Video Erstellung.

## PVData

* ~~Wirkungsgrade der Inverter berechnen~~ **Implementiert**

## WeatherData

* ~~Taupunktberechnung~~ **Implementiert**
* ~~Richtungstext Wind~~ **Implementiert**
* Windrichtungshistorie (Dir1-5)
