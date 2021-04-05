#!bin/bash
APP_NAME=convert-pts-to-ply
pyinstaller src/main.py -n ${APP_NAME} --onedir --windowed --add-data "data:data" -y
