import math
import random
import json
import time

BOARDSIZE = [30, 30]

WORLD = [[1 for x in range(BOARDSIZE[1])] for x in range(BOARDSIZE[0])]

def getRandomPositionOnSide(side):
	if side == 0:
		return (0, random.randint(0, BOARDSIZE[1] - 1))
	elif side == 1:
		return (BOARDSIZE[0] - 1, random.randint(0, BOARDSIZE[1] - 1))
	elif side == 2:
		return (random.randint(0, BOARDSIZE[0] - 1), 0)
	elif side == 3:
		return (random.randint(0, BOARDSIZE[0] - 1), BOARDSIZE[1] - 1)

def getRandomEdge():
	side = random.randint(0, 3)
	return getRandomPositionOnSide(side)

def drawPoint(cx, cy, rad):
	for x in range(cx - rad, cx + rad + 1):
		for y in range(cy - rad, cy + rad + 1):
			if x < 0 or y < 0 or x >= BOARDSIZE[0] or y >= BOARDSIZE[1]: continue
			WORLD[x][y] = 0

def makeNoodleCave(startX, startY, targetX, targetY):
	x = startX
	y = startY
	dist = 30
	incX = (targetX - startX) / dist
	incY = (targetY - startY) / dist
	for i in range(dist):
		x += incX
		y += incY
		try:
			drawPoint(round(x), round(y), 1)
		except Exception as e:
			print(f"[ Worldgen: Error when placing block: {e} where x is {x} and y is {y} ]")

makeNoodleCave(*getRandomPositionOnSide(0), *getRandomEdge())
for cave in range(3):
	makeNoodleCave(*getRandomEdge(), *getRandomEdge())

f = open("world.json", "w")
f.write(json.dumps(WORLD).replace("], [", "],\n ["))
f.close()
