# Einrichten als Service
Erstellen der Service Konfiguration:
```bash
sudo nano /etc/systemd/system/solarpy.service
```

Inhalt:
```ini
[Unit]
Description=SolarPy
After=syslog.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/zielke/SolarPy
ExecStart=/home/zielke/SolarPy/start.sh
SyslogIdentifier=solarpy
StandardOutput=syslog
StandardError=syslog
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
(Falls man die Datei ändert muss man dies systemd mittels `sudo systemctl daemon-reload` mitteilen)

Und schon können wir unseren Server starten:

```bash
sudo systemctl enable solarpy
sudo systemctl start solarpy
```


