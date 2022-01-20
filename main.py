import random
import pygame
import json
import math

pygame.init()
pygame.font.init()

BOARDSIZE = [30, 30]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
LIGHTRED = (255, 180, 180)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (28, 2, 0)
WORLD = [[random.choices([0, 1, 2, 3], weights=[10, 25, 2, 1], k=1)[0] for x in range(BOARDSIZE[0])] for y in range(BOARDSIZE[1])]
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
			elif WORLD[x][y] == 1:
				WORLD[x][y] = 0
	for l in more:
		explosion(*l, 2)

class Mob:
	def __init__(self, x, y, color):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.standing = False
		self.color = color
	def draw(self, playerx, playery):
		pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, 10, 10).move((250 - playerx, 250 - playery)))
	def tick(self):
		self.x += self.vx
		self.y += self.vy
		touching_platforms = []
		# World
		for x in range(len(WORLD)):
			for y in range(len(WORLD[x])):
				cell = WORLD[x][y]
				cellrect = pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
				if cell == 1 or cell == 3:
					if pygame.Rect(self.x, self.y + 1, 10, 10).colliderect(cellrect):
						touching_platforms.append(cellrect)
				if cell == 2:
					if pygame.Rect(self.x, self.y + 1, 10, 10).colliderect(cellrect):
						explosion(x, y, 2)
		# Velocity computations
		self.vx *= 0.5
		self.standing = False
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
					self.standing = True
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
		# Respawning, Crashing, and Moving
		if self.y > BOARDSIZE[1] * CELLSIZE:
			self.x = 100
			self.y = 0
		if self.vx > 20 or self.vy > 20 or self.vx < -20 or self.vy < -20:
			self.vx = 0
			self.vy = 0
		self.tickmove()
	def tickmove(self):
		pass
	def despawn(self):
		pass

class Player(Mob):
	def tickmove(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT]:
			self.vx -= 1
		if keys[pygame.K_RIGHT]:
			self.vx += 1
		if keys[pygame.K_UP] and self.standing:
			self.vy = -3.1
	def despawn(self):
		pygame.quit()
		exit()

class Monster(Mob):
	def __init__(self, x, y, color):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.standing = False
		self.color = color
		self.direction = None
	def tickmove(self):
		if self.standing and random.random() < 0.06: self.vy = -3.1
		if self.direction:
			self.vx += self.direction
			if random.random() < 0.1: self.direction = None
		else:
			self.direction = random.choice([1, -1])
	def despawn(self):
		if random.random() < 0.3: explosion(round(t.x / BOARDSIZE[0]), round(t.y / BOARDSIZE[1]), 3)

player = Player(100, 0, RED)
things = []

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			player.despawn()
			# User clicked close button
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
				if cell == 3:
					pygame.draw.rect(totalScreen, BROWN, cellrect)
	# Spawning
	if random.random() < 0.01:
		things.append(Monster(random.randint(0, BOARDSIZE[0] * CELLSIZE), random.randint(0, BOARDSIZE[1] * CELLSIZE), (0, 255, 0)))
	# Players & Screen
	player.tick()
	for t in things:
		t.tick()
	screen.blit(totalScreen, (250 - player.x, 250 - player.y))
	player.draw(player.x, player.y)
	for t in things:
		t.draw(player.x, player.y)
		# Despawning
		if random.random() < 0.005:
			t.despawn()
			things.remove(t)
		# Dying
		if t.y + 10 > BOARDSIZE[1] * CELLSIZE:
			things.remove(t)
	# FLIP -----------------
	pygame.display.flip()
	c.tick(60)
