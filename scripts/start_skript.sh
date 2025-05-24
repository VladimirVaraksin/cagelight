#!/bin/bash
#mit $ source start_skript.sh starten
# Ins Verzeichnis ~/RasberryPi wechseln
cd ~/RaspberryPi || { echo "Verzeichnis nicht gefunden!"; exit 1; }

# Python-Virtual-Environment "yolovenv" aktivieren
source yolovenv/bin/activate || { echo "Konnte yolovenv nicht aktivieren!"; exit 1; }

# Python-Skript mit Beispiel-Parametern ausführen
python main.py \
  --spieldauer 1 \
  --halbzeitdauer 1 \
  --fps 30 \
  --resolution 1280 720 \
  --kameranummer 0 \
  --start_after 5
