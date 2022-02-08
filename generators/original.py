import random
import json

BOARDSIZE = [30, 30]

WORLD = []

for x in range(BOARDSIZE[0]):
	WORLD.append([])
	for y in range(BOARDSIZE[1]):
		WORLD[x].append(random.choices(["air", "stone", "tnt", "hard_stone", "sand", "water"], weights=[10, 25, 2, 1, 1, 5], k=1)[0])

f = open("world.json", "w")
f.write(json.dumps(WORLD).replace("], [", "],\n ["))
f.close()
