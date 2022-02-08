import math
import random
import json

BOARDSIZE = [30, 30]

WORLD = [["air" for x in range(BOARDSIZE[1])] for x in range(BOARDSIZE[0])]

def island(x, y):
	rad = random.randint(2, 5)
	for mx in range(x - rad, x + rad):
		for my in range(y, y + rad):
			if (my - y) < rad - (mx - x) and (my - y) < (mx - x) + rad:
				if mx >= 0 and my >= 0 and mx < BOARDSIZE[0] and my < BOARDSIZE[1]:
					WORLD[mx][my] = random.choices(["stone", "water"], weights=[10, 1], k=1)[0]

island(2, 2)
for x in range(5):
    island(random.randint(0, BOARDSIZE[0] - 1), random.randint(0, BOARDSIZE[1] - 1))

f = open("world.json", "w")
f.write(json.dumps(WORLD).replace("], [", "],\n ["))
f.close()
