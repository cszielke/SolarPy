# Setup

## SolarPy holen

ein Verzeichnis erzeugen und darin mittels

```git clone https://github.com/cszielke/SolarPy.git```

das Repository klonen.

Anschließend ```setup.bat``` für Windows, oder ```setup.sh``` für linux aufrufen um die Abhängigkeiten zu installieren.

Für die Konfiguration des Programms die Datei ```./solarpy-default.cfg``` nach ```./solarpy.cfg``` kopieren und anpassen.

Das Programm kann mit ```python ./SolarPy.py``` gestartet werden.

## Upate

Um das Programm upzudaten folgende Befehle eingeben:

```sh
git fetch origin
git reset --hard origin/master
sudo /etc/init.d/solarpy restart
```

Die Datei ```solarpy.cfg``` wird nicht überschrieben.

## Start als deamon unter Linux

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

Um das Script zur richtigen Zeit automatisch zu starten, muss noch folgender Befehl ausgeführt werden:

```sh
sudo update-rc.d myservice.sh defaults
```

Dieser Befehl fügt die entsprechenden symbolischen Links in ```/etc/rc?.d``` Verzeichnissen hinzu.

Info von <http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/>

## Raspberry mit read-only Filesystem

Wenn das System, auf dem SolayPy läuft, ein read-only Filesystem hat, dann kann kein Log-File geschrieben werden. Auch das Speichern von Webcam Bildern funktioniert dann nicht.

Man kann natürlich ein freigegebenes Verzeichnis einer externen NAS oder eines externen Servers in das Filesystem des Raspberrys einbinden.

Dazu muss das externe Verzeichnis in ein locales Verzeichnis gemountet werden. Dazu wird in die Datei ```/etc/fstab``` an das Ende folgendes eingetragen:

```sh
//192.168.15.107/web /var/nas cifs defaults,uid=1000,username=pi,password=<MeinPasswortFuerDenUserPi> 0 0
```

Das bewirkt, dass bereits beim Start des Raspberry in das Verzeichnis ```/var/nas``` die externe Netzwerkfreigabe ```//192.168.15.107/web``` eingebunden wird. Hier können jetzt Webcambilder und Log-File geschrieben werden.
