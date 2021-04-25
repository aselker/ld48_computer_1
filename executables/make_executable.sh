#!/bin/sh

pyinstaller -F ../game.py
mv dist/game ./deeper_bros
rm build dist game.spec -r
