import zipHelpers
import sys
import os

if "--remove-extension" in sys.argv:
	rawExtension = zipHelpers.extract_zip("extension.zip").items
	x = zipHelpers.InMemoryZip()
	x.append("meta.txt", "(No extension installed)\n")
	x.writetofile("extension.zip")
	print("Removed extension:", rawExtension["meta.txt"].decode("UTF-8")[:-1])
if "--add-extension" in sys.argv:
	extension = sys.argv[sys.argv.index("--add-extension") + 1] + ".zip"
	extensions = os.listdir("extensions")
	if extension in extensions:
		os.system("cp extensions/" + extension + " extension.zip")
		rawExtension = zipHelpers.extract_zip("extension.zip").items
		print("Added extension:", rawExtension["meta.txt"].decode("UTF-8")[:-1])

rawDefault = zipHelpers.extract_zip("default.zip").items
rawExtension = zipHelpers.extract_zip("extension.zip").items
rawNew = zipHelpers.InMemoryZip()

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

print("Using extension:", rawExtension["meta.txt"].decode("UTF-8")[:-1])