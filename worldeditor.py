import json

def load():
	f = open("world.json", "r")
	w = json.loads(f.read())
	f.close()
	return (w["world"], w["entities"], w["playerpos"])

def save(world, entities, playerpos=[100, 0]):
	towrite = {
		"world": world,
		"entities": entities,
		"playerpos": playerpos
	}
	f = open("world.json", "w")
	f.write(json.dumps(towrite).replace("], [", "],\n ["))
	f.close()