#!/bin/bash

cp main.py zombieapocalypse.py
patch zombieapocalypse.py convert_zombie.patch
diff main.py zombieapocalypse.py > convert_zombie.patch