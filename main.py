import random
import pygame
import json

pygame.init()
pygame.font.init()

BOARDSIZE = [30, 30]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
LIGHTRED = (255, 180, 180)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WORLD = [[random.choice([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2]) for x in range(BOARDSIZE[0])] for y in range(BOARDSIZE[1])]
CELLSIZE = 50
FONT = pygame.font.Font(pygame.font.get_default_font(), 30)
c = pygame.time.Clock()

screen = pygame.display.set_mode([500, 500])

# WORLD SELECTION -----------------------------------------

wr = True

running = True
while running:
	screen.fill(WHITE)
	if wr:
		w = FONT.render("Generate new world", True, BLACK)
	else:
		w = FONT.render("Load world file", True, BLACK)
	screen.blit(w, (0, 0))
	wy = w.get_height()
	g = FONT.render("Go >", True, GREEN)
	screen.blit(g, (0, wy))
	gy = g.get_height() + wy
	for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit(); exit()
				# User clicked close button
			if event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()
				if pos[1] < wy:
					wr = not wr
				elif pos[1] < gy:
					running = False
	c.tick(60)
	pygame.display.flip()

if wr:
	f = open("world.json", "w")
	f.write(json.dumps(WORLD).replace("], [", "],\n ["))
	f.close()
else:
	f = open("world.json", "r")
	WORLD = json.loads(f.read())
	f.close()

# PLAYING -------------------------------------------------

totalScreen = pygame.Surface((BOARDSIZE[0] * CELLSIZE, BOARDSIZE[1] * CELLSIZE))

def explosion(cx, cy, rad):
	more = []
	for x in range(cx - rad, cx + rad):
		for y in range(cy - rad, cy + rad):
			if x < 0 or y < 0 or x >= BOARDSIZE[0] or y >= BOARDSIZE[1]: continue;
			if WORLD[x][y] == 2:
				more.append([x, y])
			WORLD[x][y] = 0
	for l in more:
		explosion(*l, 3)

class Mob:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
	def tick(self):
		self.x += self.vx
		self.y += self.vy
		pygame.draw.rect(screen, LIGHTRED, pygame.Rect(self.x, self.y, 10, 10).move((250 - self.x, 250 - self.y)))
		pygame.draw.rect(totalScreen, RED, pygame.Rect(self.x, self.y, 10, 10))
		touching_platforms = []
		# World
		for x in range(len(WORLD)):
			for y in range(len(WORLD[x])):
				cell = WORLD[x][y]
				cellrect = pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
				if cell == 1:
					if pygame.Rect(self.x, self.y + 1, 10, 10).colliderect(cellrect):
						touching_platforms.append(cellrect)
				if cell == 2:
					if pygame.Rect(self.x, self.y + 1, 10, 10).colliderect(cellrect):
						explosion(x, y, 3)
		# Velocity computations
		self.vx *= 0.5
		if len(touching_platforms) == 0:
			self.vy += 0.05
		else:
			for platform in touching_platforms:
				# Mob is touching a platform!
				thismob = pygame.Rect(self.x, self.y, 10, 10)
				if platform.top - thismob.bottom > -10:
					# Mob is standing on a platform!
					self.vy = 0
					self.y = platform.top - 10
					if keys[pygame.K_UP]:
						self.vy = -3.1
					pygame.draw.line(totalScreen, (0, 255, 0), platform.topleft, platform.topright, 5)
				else:
					if platform.left - thismob.right > -5:
						# Mob is bumping into left side of platform!
						self.vx = -1
						pygame.draw.line(totalScreen, (0, 255, 0), platform.topleft, platform.bottomleft, 5)
					elif thismob.left - platform.right > -5:
						# Mob is bumping into right side of platform!
						self.vx = 1
						pygame.draw.line(totalScreen, (0, 255, 0), platform.topright, platform.bottomright, 5)
					elif platform.bottom - thismob.top > -10:
						# Player is whacking into the top of a platform!
						self.vy = 0
						self.y = platform.bottom
						pygame.draw.line(totalScreen, (0, 255, 0), platform.bottomleft, platform.bottomright, 5)
		# Respawning
		if self.y > BOARDSIZE[1] * CELLSIZE:
			self.x = 100
			self.y = 0

player = Mob(100, 0)

running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
			# User clicked close button
	keys = pygame.key.get_pressed()
	if keys[pygame.K_LEFT]:
		player.vx -= 1
	if keys[pygame.K_RIGHT]:
		player.vx += 1
	# DRAWING ------------
	screen.fill(GRAY)
	totalScreen.fill(WHITE)
	# Board
	for x in range(len(WORLD)):
			for y in range(len(WORLD[x])):
				cell = WORLD[x][y]
				cellrect = pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
				if cell == 1:
					pygame.draw.rect(totalScreen, BLACK, cellrect)
				if cell == 2:
					pygame.draw.rect(totalScreen, RED, cellrect)
	# Player
	player.tick()
	# FLIP -----------------
	screen.blit(totalScreen, (250 - player.x, 250 - player.y))
	pygame.display.flip()
	c.tick(60)
pygame.quit()
