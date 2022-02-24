import zipHelpers
import sys
import os

os.system("rm style_env.zip")

rawDefault = zipHelpers.extract_zip("default.zip").items
rawExtension = zipHelpers.extract_zip("extension.zip").items
rawNew = zipHelpers.InMemoryZip()

if "--remove-extension" in sys.argv:
	rawExtension = {}

for filename in rawDefault:
	if filename[-1] == "/": continue
	if filename in rawExtension:
		rawNew.append(filename, rawExtension[filename])
	else:
		rawNew.append(filename, rawDefault[filename])

for filename in rawExtension:
	if filename[-1] == "/": continue
	if filename not in rawDefault:
		rawNew.append(filename, rawExtension[filename])

rawNew.writetofile("style_env.zip")

if "--remove-extension" in sys.argv:
	x = zipHelpers.InMemoryZip()
	x.append("msg.txt", "No extension installed")
	x.writetofile("extension.zip")