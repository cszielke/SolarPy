# SolarPy

## Datenerfassung für Fronius Wechselrichter mit Fronius IG Interface Card/Box

Das Programm ist gedacht, um mittels eines Raspberry Pi's die Daten der Wechselrichter über das interne Netzwerk zur Verfügung zu stellen.

Es besteht die Möglichkeit die Daten in einer MySQL und/oder InfluxDB Datenbank zu archivieren.

Über eine REST-API Schnittstelle oder über MQTT können die Daten abgefragt werden. Andere Ausgabeschnittstellen sind leicht implementierbar.

Das Programm ist komplett in Python geschrieben und benötigt keine Oberfläche. Das Programm lässt sich umfangreich über eine CFG-Datei konfigurieren.

## Setup

### SolarPy holen

ein Verzeichnis erzeugen und darin mittels

```git clone https://github.com/cszielke/SolarPy.git```

das Repository klonen.

Anschließend ```setup.bat``` für Windows, oder ```setup.sh``` für linux aufrufen um die Abhängigkeiten zu installieren.

Für die Konfiguration des Programms die Datei ```./fronius-default.cfg``` nach ```./fronius.cfg``` kopieren und anpassen.

Das Programm kann mit ```python ./fronius.py``` gestartet werden.

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
DAEMON=$DIR/fronius.py
DAEMON_NAME=SolarPy

# Add any command line options for your daemon here
DAEMON_OPTS=" -cf /etc/fronius.cfg"

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
