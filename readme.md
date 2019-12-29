# SolarPy

## Datenerfassung für Solaranlage mit Fronius Wechselrichter und Fronius IG Interface Card/Box

Das Programm ist gedacht, um mittels eines Raspberry Pi's die Daten der Wechselrichter über das interne Netzwerk zur Verfügung zu stellen.

Es besteht die Möglichkeit die Daten in einer MySQL und/oder InfluxDB Datenbank zu archivieren.

Über eine REST-API Schnittstelle oder über MQTT können die Daten abgefragt werden. Andere Ein-/Ausgabeschnittstellen sind leicht implementierbar.

Das Programm ist komplett in Python geschrieben und benötigt keine Oberfläche. Das Programm lässt sich umfangreich über eine CFG-Datei konfigurieren.

## Setup

### SolarPy holen

ein Verzeichnis erzeugen und darin mittels

```git clone https://github.com/cszielke/SolarPy.git```

das Repository klonen.

Anschließend ```setup.bat``` für Windows, oder ```setup.sh``` für linux aufrufen um die Abhängigkeiten zu installieren.

Für die Konfiguration des Programms die Datei ```./fronius-default.cfg``` nach ```./fronius.cfg``` kopieren und anpassen.

Das Programm kann mit ```python ./SolarPy.py``` gestartet werden.

### Start als deamon unter Linux

Um SolarPy als Deamon im Hintergrund zu starten wird das Programm ```start-stop-daemon``` verwendet. SolarPy sollte im Verzeichnis ```/usr/local/bin/SolarPy``` liegen.
Man erzeugt eine Datei ```solarpy``` im Verzeichnis ```/etc/init.d``` (Rechte nicht vergessen!) mit folgendem Inhalt:

```sh
#!/bin/sh

### BEGIN INIT INFO
# Provides:          myservice
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Put a short description of the service here
# Description:       Put a long description of the service here
### END INIT INFO

# Change the next 3 lines to suit where you install your script and what you want to call it
DIR=/usr/local/bin/SolarPy
DAEMON=$DIR/SolarPy.py
DAEMON_NAME=SolarPy

# Add any command line options for your daemon here
DAEMON_OPTS=" -cf /etc/solarpy.cfg"

# This next line determines what user the script runs as.
# Root generally not recommended but necessary if you are using the Raspberry Pi GPIO from Python.
DAEMON_USER=root

# The process ID of the script when it runs is stored here:
PIDFILE=/var/run/$DAEMON_NAME.pid

. /lib/lsb/init-functions

do_start () {
    log_daemon_msg "Starting system $DAEMON_NAME daemon"
    start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas $DAEMON -- $DAEMON_OPTS
    log_end_msg $?
}
do_stop () {
    log_daemon_msg "Stopping system $DAEMON_NAME daemon"
    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    log_end_msg $?
}

case "$1" in

    start|stop)
        do_${1}
        ;;

    restart|reload|force-reload)
        do_stop
        do_start
        ;;

    status)
        status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
        ;;

    *)
        echo "Usage: /etc/init.d/$DAEMON_NAME {start|stop|restart|status}"
        exit 1
        ;;

esac
exit 0
```

Info von <http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/>

## Anwendung

### Http-Server mit REST-API

Der interne Webserver kann - sofern enabled - über die konfigurierte Adresse aufgerufen werden:

Per default ist das:

```http://localhost:8080/```

Der Inhalt dieser Seite kann den eigenen Bedürfnissen angepasst werden (template/index.html).

Unter ```http://localhost:8080/data.json``` können die aktuellen Daten der Solaranlage abgefragt werden. Man erhält eine JSON-Datei mit dieser Struktur:

```JSON
{
    "ActiveInvCnt": 0,
    "ActiveSensorCardCnt": 0,
    "DevTime": -1,
    "Error": "OK",
    "LocalNetStatus": -1,
    "PDayGesamt": 10000.0,
    "PGesamt": 0.0,
    "Time": 1577635117.0,
    "VersionIFC": -1,
    "wr": [{
            "DevType": -1,
            "FAC": 0.0,
            "IAC": 0.0,
            "IDC": 0.0,
            "OHDAY": -1,
            "OHTOT": -1,
            "OHYEAR": -1,
            "PDay": 4000.0,
            "PNow": 0.0,
            "UAC": 0.0,
            "UDC": 0.0
        }, {
            "DevType": -1,
            "FAC": 0.0,
            "IAC": 0.0,
            "IDC": 0.0,
            "OHDAY": -1,
            "OHTOT": -1,
            "OHYEAR": -1,
            "PDay": 6000.0,
            "PNow": 0.0,
            "UAC": 0.0,
            "UDC": 0.0
        }
    ]
}

```

### Webcam

Sofern das Bild der Webcam per URL abgefragt werden kann (z.B. <http://www.example.com:80/image.jpg>) , ist es möglich in das Bild die Daten der PV-Anlage zu implementieren. Das modifizierte Webcam Bild kann dann über den integrierten Webserver abgefragt werden (z.B. <http://localhost:8080/webcam.jpg)).>

Wenn gewüscht kann in konfigurierbaren Intervallen ein Bild gespeichert werden. Aus dieser Bilderserie kann dann zb. mit ffmpeg ein video generiert werden, was den Tagesverlauf der Beschattung auf den Solarpanelen generiert.

### InfluxDB

tbd.

### MySQL

tbd.
