#!/bin/bash

#diff main.py zombieapocalypse.py > convert_zombie.patch
cp main.py zombieapocalypse.py
patch zombieapocalypse.py convert_zombie.patch