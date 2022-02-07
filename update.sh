#!/usr/bin/env bash

echo "Updates available:\n"
git fetch -q && git log --no-decorate --reverse --pretty=%C\(bold\)Update:\ %C\(red\)%s%n\ \ \ \ \ \ \ \ %b ..origin/main
echo
read -p "Continue (y/n)? " choice
case "$choice" in 
  y|Y ) echo "Downloading updates..."; git pull -q; echo "Done!";;
  n|N ) echo "Canceled.";;
  * ) echo "Invalid response; canceled.";;
esac
