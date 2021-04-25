#!/bin/sh

pyinstaller -F ../game.py
mv dist/game ./game
rm build dist game.spec -r
