import json
import basics
import requests

def load():
	r = requests.get("http://localhost:8080/getworld")
	w = json.loads(r.text)
	return (w["world"], w["entities"], w["playerpos"], w["items"], w["health"])

def save(world, entities, playerpos=[100, 0], items={}, health=basics.PLAYERHEALTH):
	towrite = {
		"world": world,
		"entities": entities,
		"playerpos": playerpos,
		"items": items,
		"health": health
	}
	t = json.dumps(towrite).replace("], [", "],\n [")
	r = requests.post("http://localhost:8080/setworld", data=t)