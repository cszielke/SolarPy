#!/bin/bash

# Beispiel für ein Startscript

HOMEDIR=/home/zielke/SolarPy/
OLDDIR=$(pwd)
cd $HOMEDIR
source ./env/bin/activate
python3 ./SolarPy.py
cd $OLDDIR
exit 0
