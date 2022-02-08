import random
import json

BOARDSIZE = [30, 30]

WORLD = []

for x in range(BOARDSIZE[0]):
	WORLD.append([])
	for y in range(BOARDSIZE[1]):
		if y > 10: WORLD[x].append("stone")
		else:
			if x % 2 == 0 or y % 2 == 0: WORLD[x].append("tnt")
			else: WORLD[x].append("sand")

WORLD[2][0] = "air"
WORLD[2][1] = "hard_stone"

f = open("world.json", "w")
f.write(json.dumps(WORLD).replace("], [", "],\n ["))
f.close()
