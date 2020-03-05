# Scripts

## Erzeugen der Dokumentation

Die Dokumentation wird aus den Markdown Dateien im Verzeichnis "docs" erstellt. Dazu wird das Tool **"mkdocs"** verwendet. Als Template wird **"material"** verwendet.

### Echtzeit Darstellung

Mit dem Befehl

```sh
mkdocs serve
```

Kann eine Echtzeitdarstellung in einem Webbrowser angesehen werden. Unter der Adresse [http://localhost:8000](http://localhost:8000) kann jede gespeicherte Änderung an einer Markdown Datei sofort kontrolliert werden.

### Lokale Erzeugung

Mit dem Befehl

```sh
mkdocs build
```

wird im Verzeichnis **"site"** ein lokales Abbild der Dokumentation erzeugt. Das Verzeichnis kann dann auf einen Webspace kopiert werden. Das Verzeichnis **"site"** wird nicht in Git eingecheckt.

### Github publish

Mit dem Befehl

```sh
mkdocs gh-deploy
```

wird die Dokumentation erzeugt und im Branch **"gh-pages"** veröffentlicht. Github sorgt dafür, dass die erzeugte Seite dann unter [https://cszielke.github.io/SolarPy/](https://cszielke.github.io/SolarPy/) aufgerufen werden kann.

## Erzeugen von Video Dateien

Um aus den gespeicherten Bilder eines Tages ein Video zu erstellen, befinden sich im Verzeichnis **"scripts"** zwei PowerShell Scripts:

* encode_pictures.ps1 (Encodiert das Video mittels ffmpeg)
* makeallpvvideos.ps1 (Durchsucht die Verzeichnisstruktur nach Bildern)

### Beispiel

```powershell
 .\makeallpvvideos.ps1 \\raspidbsrv\web\html\webcam \\raspidbsrv\web\html\webcam\videos
```
