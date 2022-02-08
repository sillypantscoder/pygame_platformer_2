import random
import json

BOARDSIZE = [30, 30]

WORLD = []

for x in range(BOARDSIZE[0]):
	WORLD.append([])
	for y in range(BOARDSIZE[1]):
		if x % 2 == 0 and y % 2 == 0: WORLD[x].append("hard_stone")
		elif x % 2 == 0 or y % 2 == 0: WORLD[x].append(random.choice(["stone", "hard_stone", "air", "tnt"]))
		else: WORLD[x].append("air")

WORLD[2][0] = "air"
WORLD[2][1] = "hard_stone"

f = open("world.json", "w")
f.write(json.dumps(WORLD).replace("], [", "],\n ["))
f.close()
