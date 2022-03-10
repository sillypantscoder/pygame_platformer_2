#!/bin/bash

#diff main.py zombieapocalypse.py > make_zombieapocalypse.patch
cp main.py zombieapocalypse.py
patch zombieapocalypse.py convert_zombie.patch