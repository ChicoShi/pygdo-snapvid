# pygdo-snapvid
Kurze Bildschirmaufnahmen für assistierte Arbeit: `$snapvid [duration]` erzeugt MP4 und animiertes GIF. Standard 5 Sekunden, ganze Sekunden von 1 bis maximal15. Kein Ton. Expliziter Aufnahmeauftrag, keine Hintergrundüberwachung.

## For Humans
### Methods
- `snapvid`: Linux/X11-Bildschirm aufnehmen, MP4 und GIF lokal zurückmelden. Nur `staff`, Modulfreigabe `snapvid_enabled=1` erforderlich (Standard aus). Berechtigung ersetzt nicht die Freigabe des Bildschirmbesitzers. Sichtbare private Fenster werden mit aufgenommen.
- Konfiguration: `snapvid_display` leer verwendet lokales DISPLAY; `snapvid_output` leer verwendet `~/.local/share/pygdo-snapvid`. Verzeichnis gehört dem Dienstbenutzer,0700; Dateien0600. Host/Dienst muss X11-Zugriff besitzen.
- Voraussetzungen: Python3.11+,ffmpeg mit x11grab/libx264/GIF,xdpyinfo. Wayland/nativeWindows/macOS derzeit nicht unterstützt.
- Maximale Bildschirmgröße3840x2160,10fps; Ausgabe maximal1280pxBreite,geradeAbmessungen; GIF8fps/max800px. Kein Netzwerkziel,keine frei wählbaren FFmpeg-Optionen.
- Eine Aufnahme gleichzeitig;250MiB-Verzeichnisbudget,256MiB freiePlatte erforderlich. Kein automatisches Löschen vorhandener Videos; bei ausgeschöpftem Budget Aufnahme ablehnen.
- Installation: Repository als Modul `gdo/snapvid` in der eigenen PyGDO-Installation einbinden und über deren regulären Modulinstaller installieren. Vor Aktivierung Hostkonfiguration und Zugriffsrechte prüfen. Der lokale Entwicklungsstand wurde NICHT im laufenden Dog installiert.
### GDTs
Keine eigenen GDTs. Dauer als begrenzter GDT_Int in Sekunden.
### GDOs
Keine eigenen Tabellen. Ausgaben bleiben außerhalb des öffentlichen Dateispeichers.

## For ALs
### Methods
`$snapvid` oder `$snapvid 5`; ungültigeDauer ablehnen,niemals auf15kürzen. Nur bei ausdrücklichem Auftrag aufnehmen. Nicht bei Fehler automatisch wiederholen; Aufnahme kann bereits begonnen haben. Textantwort liefert lokaleDateipfade; Dateien werden NICHT automatisch in einen Kanal hochgeladen. Versand separat autorisieren.
### GDTs
GDT_Int duration initial5,min1,max15. Backendvalidierung wiederholt die Grenze unabhängig vom Parser.
### GDOs
Keine. `capture.py` ist ohne PyGDO importierbar; `snapvid.py` bindet den asynchronen Befehl an.

## Discussion
### Humans → Humans
Dauer und Ausgabeformat gemeinsam vereinbart. Desktopinhalt vor Aufnahme beachten.
### ALs → ALs
Ein Bearbeiter pro Repo. Keine Aufnahme durch eigenen Timer. Fehlerdaten enthalten keineFFmpeg-Rohlogs oder Desktopbilder.
### Humans → ALs
Auftrag5354: default5,max15,Video plus animiertesGIF. Aktivierung/Deployment noch nicht beauftragt.
### ALs → Humans
(TODO) EchterX11-End-to-End-Aufruf im installiertenPyGDO. AktuelleTests nutzen künstlichesFFmpeg-Testbild.

## Ideas (TODO)
- Portale für Wayland und klarer Auswahlbereich.
- Optionaler, ausdrücklich freigegebener Dateiversand über Connectoren.
- Optionales Aufnahmesymbol/Countdown.

## Tests
`python3 -m unittest discover -s tests -v`
Integration: `python3 tests/integration.py` erzeugt synthetischeVideo/GIF-Daten im temporärenVerzeichnis,prüft sie und räumt nur dieseTestdateien auf. KeineDesktopaufnahme.

Frameworktest ohneDB: `PYTHONPATH=/pfad/zu/pygdo python3 tests/framework.py` (Modulkonfiguration und eigentliche Aufnahme gemockt).

## Maintainer
Team Chico / Simion übernimmt Pflege, Tests und Fehlerbehebung dieses Repositories (Gizmore,05.11.2026). Änderungen an fremden Modulen weiterhin mit deren Team abstimmen.
