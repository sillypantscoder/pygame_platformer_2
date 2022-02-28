import random
import pygame
import json
import zipHelpers
from basics import *
from os import system

pygame.font.init()

playerpos = [100, 0]
selectedx = 0
selectedy = 0

rawStyleItems = zipHelpers.extract_zip("style_env.zip").items
BLOCKS = json.loads(rawStyleItems["blocks.json"].decode("UTF-8"))
pallete = []
pos = 0
for id in BLOCKS:
	pallete.append({"color": BLOCKS[id]["color"], "id": id, "rect": pygame.Rect(CELLSIZE * pos, 0, CELLSIZE, CELLSIZE)})
	pos += 1
selectedbrush = 0

WORLD = [[random.choice(["air", "stone"]) for x in range(BOARDSIZE[0])] for y in range(BOARDSIZE[1])]
FONT = pygame.font.Font(pygame.font.get_default_font(), 30)
c = pygame.time.Clock()

screen = pygame.display.set_mode([min(max(500, len(pallete) * CELLSIZE), 2000), 500 + CELLSIZE])

f = open("world.json", "r")
WORLD = json.loads(f.read())
f.close()

# PLAYING -------------------------------------------------

totalScreen = pygame.Surface((BOARDSIZE[0] * CELLSIZE, BOARDSIZE[1] * CELLSIZE))

def insideBoard(x, y):
	if x < 0 or y < 0 or x >= BOARDSIZE[0] or y >= BOARDSIZE[1]: return False
	return True

def bytesToSurface(b: bytes):
	f = open("texture.png", "wb")
	f.write(b)
	f.close()
	s = pygame.image.load("texture.png")
	system("rm texture.png")
	return s

textures = {}
for filename in rawStyleItems:
	if "textures/" in filename:
		if filename[-1] != "/":
			try:
				textures[filename[9:]] = bytesToSurface(rawStyleItems[filename])
			except:
				print(filename)
				exit(1)

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
	renderdistance = 6
	for x in range(round(playerpos[0] / CELLSIZE) - renderdistance, round(playerpos[0] / CELLSIZE) + renderdistance):
		for y in range(round(playerpos[1] / CELLSIZE) - renderdistance, round(playerpos[1] / CELLSIZE) + renderdistance):
			if not insideBoard(x, y): continue;
			cell = WORLD[x][y]
			cellrect = pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
			if cell in BLOCKS:
				if BLOCKS[cell]["color"] == False: totalScreen.blit(textures["block/" + cell + ".png"], cellrect.topleft)
				else: pygame.draw.rect(totalScreen, BLOCKS[cell]["color"], cellrect)
			if pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE).collidepoint(pos):
				selectedx = x
				selectedy = y
				pygame.draw.rect(totalScreen, RED, pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE), 10)
	# Player
	pygame.draw.rect(screen, LIGHTRED, pygame.Rect(*playerpos, 10, 10).move((250 - playerpos[0], 250 - playerpos[1])))
	pygame.draw.rect(totalScreen, RED, pygame.Rect(*playerpos, 10, 10))
	# FLIP -----------------
	screen.blit(totalScreen, (250 - playerpos[0], 250 - playerpos[1]))
	screen.blit(FONT.render(str(WORLD[selectedx][selectedy]), True, BLACK), (0, CELLSIZE))
	# Pallete
	for o in pallete:
		if o["color"] == False:
			screen.blit(textures["block/" + o["id"] + ".png"], o["rect"].topleft)
		else: pygame.draw.rect(screen, o["color"], o["rect"])
	pygame.display.flip()
	c.tick(60)
pygame.quit()

f = open("world.json", "w")
f.write(json.dumps(WORLD).replace("], [", "],\n ["))
f.close()
