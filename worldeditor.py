import json
import basics

def load():
	f = open("world.json", "r")
	w = json.loads(f.read())
	f.close()
	return (w["world"], w["entities"], w["playerpos"], w["items"], w["health"])

def save(world, entities, playerpos=[100, 0], items={}, health=basics.PLAYERHEALTH):
	towrite = {
		"world": world,
		"entities": entities,
		"playerpos": playerpos,
		"items": items,
		"health": health
	}
	f = open("world.json", "w")
	f.write(json.dumps(towrite).replace("], [", "],\n ["))
	f.close()
