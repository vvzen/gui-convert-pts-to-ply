#!/bin/bash
APP_NAME=convert-pts-to-ply
rm -rf ./build
rm -rf ./dist
pyinstaller src/main.py -n ${APP_NAME} --onedir --windowed --add-data "data:data" --paths "./src" -y
