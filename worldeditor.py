import json

def load():
	f = open("world.json", "r")
	w = json.loads(f.read())
	f.close()
	return w

def save(w):
	f = open("world.json", "w")
	f.write(json.dumps(w).replace("], [", "],\n ["))
	f.close()