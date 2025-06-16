#!/bin/bash
#mit $ source start_skript.sh starten
# Ins Verzeichnis ~/CageLight wechseln
cd ~/CageLight/AI--Realtime || { echo "Verzeichnis nicht gefunden!"; exit 1; }

# Python-Virtual-Environment "yolovenv" aktivieren
source yolovenv/bin/activate || { echo "Konnte yolovenv nicht aktivieren!"; exit 1; }

# Python-Skript mit Beispiel-Parametern ausführen
python main.py \
  --spieldauer 60 \
  --halbzeitdauer 5 \
  --fps 30 \
  --resolution 1280 720 \
  --start_after 5