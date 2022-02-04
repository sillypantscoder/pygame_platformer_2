import random
import json

BOARDSIZE = [30, 30]

WORLD = []

for x in range(BOARDSIZE[0]):
	WORLD.append([])
	for y in range(BOARDSIZE[1]):
		WORLD[x].append(random.choices([0, 1, 2, 3], weights=[10, 25, 2, 1], k=1)[0])

for i in range(10):
	cx = random.randint(1, BOARDSIZE[0] - 2)
	cy = random.randint(1, BOARDSIZE[1] - 2)
	for x in range(cx - 1, cx + 2):
		for y in range(cy - 1, cy + 2):
			if x == cx and y == cy: WORLD[x][y] = 2
			else: WORLD[x][y] = 4
	WORLD[cx][cy - 1] = 0

f = open("world.json", "w")
f.write(json.dumps(WORLD).replace("], [", "],\n ["))
f.close()
