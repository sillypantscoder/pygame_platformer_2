import random
import pygame
import json
import zipHelpers

pygame.init()
pygame.font.init()

playerpos = [100, 0]
selectedx = 0
selectedy = 0

BOARDSIZE = [30, 30]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
LIGHTRED = (255, 180, 180)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (28, 2, 0)
TAN = (255, 241, 171)
WORLD = [[random.choice(["air", "stone"]) for x in range(BOARDSIZE[0])] for y in range(BOARDSIZE[1])]
CELLSIZE = 50
FONT = pygame.font.Font(pygame.font.get_default_font(), 30)
c = pygame.time.Clock()
rawStyleItems = zipHelpers.extract_zip("default.zip").items
BLOCKS = json.loads(rawStyleItems["blocks.json"].decode("UTF-8"))

screen = pygame.display.set_mode([500, 500 + CELLSIZE])

f = open("world.json", "r")
WORLD = json.loads(f.read())
f.close()

# PLAYING -------------------------------------------------

totalScreen = pygame.Surface((BOARDSIZE[0] * CELLSIZE, BOARDSIZE[1] * CELLSIZE))

pallete = []
pos = 0
for id in BLOCKS:
	pallete.append({"color": BLOCKS[id]["color"], "id": id, "rect": pygame.Rect(CELLSIZE * pos, 0, CELLSIZE, CELLSIZE)})
	pos += 1
selectedbrush = 0

running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
			# User clicked close button
		if event.type == pygame.MOUSEBUTTONUP:
			world = True
			for o in pallete:
				if o["rect"].collidepoint(pygame.mouse.get_pos()):
					world = False
					selectedbrush = o["id"]
			if world:
				WORLD[selectedx][selectedy] = selectedbrush
	keys = pygame.key.get_pressed()
	if keys[pygame.K_LEFT]:
		playerpos[0] -= 2
	if keys[pygame.K_RIGHT]:
		playerpos[0] += 2
	if keys[pygame.K_UP]:
		playerpos[1] -= 2
	if keys[pygame.K_DOWN]:
		playerpos[1] += 2
	pos = [*pygame.mouse.get_pos()]
	pos[0] += playerpos[0] - 250
	pos[1] += playerpos[1] - 250
	# DRAWING ------------
	screen.fill(GRAY)
	totalScreen.fill(WHITE)
	# World
	for x in range(len(WORLD)):
		for y in range(len(WORLD[x])):
			cell = WORLD[x][y]
			if cell in BLOCKS:
				pygame.draw.rect(totalScreen, BLOCKS[cell]["color"], pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE))
			if pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE).collidepoint(pos):
				selectedx = x
				selectedy = y
				pygame.draw.rect(totalScreen, RED, pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE), 10)
	# Player
	pygame.draw.rect(screen, LIGHTRED, pygame.Rect(*playerpos, 10, 10).move((250 - playerpos[0], 250 - playerpos[1])))
	pygame.draw.rect(totalScreen, RED, pygame.Rect(*playerpos, 10, 10))
	# FLIP -----------------
	screen.blit(totalScreen, (250 - playerpos[0], 250 - playerpos[1]))
	# Pallete
	for o in pallete:
		pygame.draw.rect(screen, o["color"], o["rect"])
	pygame.display.flip()
	c.tick(60)
pygame.quit()

f = open("world.json", "w")
f.write(json.dumps(WORLD).replace("], [", "],\n ["))
f.close()
