#!/usr/bin/env bash
status=$(git status -s);

tfind=$"\n M";

if [[ $"\n$status" == *"$tfind"* ]]; then
	echo "WARNING: There are changes in the current directory that may conflict with incoming changes:"
	git status -s
	echo
fi

echo "Updates available:\n"
git fetch -q && git log --no-decorate --reverse --pretty=%C\(bold\)Update:\ %C\(red\)%s%n\ \ \ \ \ \ \ \ %b ..origin/main
echo
read -p "Continue (y/n)? " choice
case "$choice" in 
	y|Y ) echo "Downloading updates..."; git pull -q; echo "Done!";;
	n|N ) echo "Canceled.";;
	* ) echo "Invalid response; canceled.";;
esac
