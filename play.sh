#!/bin/bash

alias play='python3 main.py'
alias zombie='python3 zombieapocalypse.py'
alias leveleditor='python3 level_editor.py'
alias update='bash update.sh; cont="0"'
alias back='cont="0"'

echo "Hi there! This is the platformer terminal."
echo "Type 'play' (and press Enter) to play the game."
echo "Type 'back' (and press Enter) to exit this terminal and go back to the normal one."
echo "Type 'update' (and press Enter) to update the game."
echo "Type 'instructions' (and press Enter) to view the instructions."

cont="1"
MY_PROMPT='$ '
while [ $cont -eq 1 ]
do
	echo -n "$MY_PROMPT"
	read line
	eval "$line"
	done

echo
echo "Bye! Type 'sh play.sh' to get back here."
exit 0