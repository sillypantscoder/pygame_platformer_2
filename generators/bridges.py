import random
import json

BOARDSIZE = [30, 30]

WORLD = [["air" for x in range(BOARDSIZE[1])] for x in range(BOARDSIZE[0])]

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
	side = random.choice([0, 1])
	return getRandomPositionOnSide(side)

def drawPoint(cx, cy):
	WORLD[cx][cy] = random.choices(["stone", "tnt"], weights=[10, 1], k=1)[0]

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
			drawPoint(round(x), round(y))
		except Exception as e:
			print(f"[ Worldgen: Error when placing block: {e} where x is {x} and y is {y} ]")

pos = getRandomPositionOnSide(0)
for cave in range(10):
	newPos = getRandomEdge()
	makeNoodleCave(*pos, *newPos)
	pos = newPos

f = open("world.json", "w")
f.write(json.dumps(WORLD).replace("], [", "],\n ["))
f.close()
