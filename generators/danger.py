import random
import json

BOARDSIZE = [30, 30]

WORLD = []

for x in range(BOARDSIZE[0]):
	WORLD.append([])
	for y in range(BOARDSIZE[1]):
		if y > 10: WORLD[x].append(1)
		else:
			if x % 2 == 0 or y % 2 == 0: WORLD[x].append(2)
			else: WORLD[x].append(4)

WORLD[2][0] = 0
WORLD[2][1] = 3

f = open("world.json", "w")
f.write(json.dumps(WORLD).replace("], [", "],\n ["))
f.close()
