import random
import json

BOARDSIZE = [30, 30]

WORLD = []

for x in range(BOARDSIZE[0]):
	WORLD.append([])
	for y in range(BOARDSIZE[1]):
		WORLD[x].append(random.choices([0, 2, 4], weights=[10, 1, 10], k=1)[0])

WORLD[2][1] = 3

f = open("world.json", "w")
f.write(json.dumps(WORLD).replace("], [", "],\n ["))
f.close()
