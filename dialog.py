import os

def dialog(msg, items=["OK"]):
	f = open("dialog.txt", "w")
	f.write(msg + "\n" + "\n".join(items))
	f.close()
	os.system("python3 dialog/dialog.py")
	f = open("dialog.txt", "r")
	chosen = f.read()
	f.close()
	os.system("rm dialog.txt")
	return chosen
def prompt(msg, pretext=""):
	f = open("dialog.txt", "w")
	f.write(msg + "\n" + pretext)
	f.close()
	os.system("python3 dialog/prompt.py")
	f = open("dialog.txt", "r")
	chosen = f.read()
	f.close()
	os.system("rm dialog.txt")
	return chosen