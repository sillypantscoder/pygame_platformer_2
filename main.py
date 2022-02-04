from os import listdir, system
import random
import pygame
import json
import math

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

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
TAN = (255, 241, 171)
WORLD = [[random.choices([0, 1, 2, 3, 4], weights=[10, 25, 2, 1, 1], k=1)[0] for y in range(BOARDSIZE[1])] for x in range(BOARDSIZE[0])]
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

# GENERATOR SELECTION

items = listdir("generators")
running = wr
while running:
	screen.fill(WHITE)
	for i in range(len(items)):
		w = FONT.render(items[i], True, BLACK)
		screen.blit(w, (0, i * 40))
	for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit(); exit()
				# User clicked close button
			if event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()
				y = math.floor(pos[1] / 40)
				wr = items[y]
				running = False
	c.tick(60)
	pygame.display.flip()

if wr:
	system("python3 generators/" + wr)
f = open("world.json", "r")
WORLD = json.loads(f.read())
f.close()

# PLAYING -------------------------------------------------

totalScreen = pygame.Surface((BOARDSIZE[0] * CELLSIZE, BOARDSIZE[1] * CELLSIZE))

def explosion(cx, cy, rad):
	things.append(Particle((cx * CELLSIZE) + (0.5 * CELLSIZE), (cy * CELLSIZE) + (0.5 * CELLSIZE)))
	more = []
	for x in range(cx - rad, cx + rad + 1):
		for y in range(cy - rad, cy + rad + 1):
			if x < 0 or y < 0 or x >= BOARDSIZE[0] or y >= BOARDSIZE[1]: continue
			if WORLD[x][y] == 2:
				more.append([x, y])
				WORLD[x][y] = 0
			elif WORLD[x][y] == 1:
				WORLD[x][y] = 0
			elif WORLD[x][y] == 4:
				WORLD[x][y] = 0
				s = MovingBlock(x * CELLSIZE, y * CELLSIZE)
				things.append(s)
	for t in things:
		if pygame.Rect(cx - rad, cy - rad, rad * 2, rad * 2).collidepoint((t.x / CELLSIZE, t.y / CELLSIZE)):
			t.vx += (random.random() * 4) - 2
			t.vy += (random.random() * 4) - 2
	for l in more:
		explosion(*l, 2)
	if random.random() < 0.3: things.append(Item((cx * CELLSIZE) + (0.5 * CELLSIZE), (cy * CELLSIZE) + (0.5 * CELLSIZE)))

class Entity:
	color = (0, 0, 0)
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.standing = False
		self.ticking = True
	def draw(self, playerx, playery):
		pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, 10, 10).move((250 - playerx, 250 - playery)))
	def tick(self):
		if not self.ticking: return
		self.x += self.vx
		self.y += self.vy
		touching_platforms = []
		# World
		for x in range(len(WORLD)):
			for y in range(len(WORLD[x])):
				cell = WORLD[x][y]
				cellrect = pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
				if cell == 1 or cell == 3 or cell == 4:
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
				# Entity is touching a platform!
				thisEntity = pygame.Rect(self.x, self.y, 10, 10)
				if platform.top - thisEntity.bottom > -10:
					# Entity is standing on a platform!
					self.vy = 0
					self.y = platform.top - 10
					self.standing = True
					pygame.draw.line(totalScreen, (0, 255, 0), platform.topleft, platform.topright, 5)
					if WORLD[math.floor(platform.left / CELLSIZE)][math.floor(platform.top / CELLSIZE)] == 4:
						# Standing on sand!
						fall = False
						try:
							if WORLD[math.floor(platform.left / CELLSIZE)][math.floor(platform.top / CELLSIZE) + 1] == 0:
								fall = True
						except:
							fall = True
							print("Entity " + str(self) + " caused sand to fall out bottom of world")
						if fall:
							WORLD[math.floor(platform.left / CELLSIZE)][math.floor(platform.top / CELLSIZE)] = 0
							s = MovingBlock(*platform.topleft)
							s.vy = 3
							things.append(s)
				else:
					if platform.left - thisEntity.right > -5:
						# Entity is bumping into left side of platform!
						self.vx = -1.05
						pygame.draw.line(totalScreen, (0, 255, 0), platform.topleft, platform.bottomleft, 5)
					elif thisEntity.left - platform.right > -5:
						# Entity is bumping into right side of platform!
						self.vx = 1.05
						pygame.draw.line(totalScreen, (0, 255, 0), platform.topright, platform.bottomright, 5)
					elif platform.bottom - thisEntity.top > -10:
						# Entity is whacking into the top of a platform!
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
			print("Entity " + str(self) + " went too fast!")
		self.tickmove()
		if len(things) < 20 or pygame.key.get_pressed()[pygame.K_a]: self.opt_ai_calc()
	def tickmove(self):
		pass
	def despawn(self):
		pass
	def die(self):
		if self in things:
			self.despawn()
			things.remove(self)
		else: print("Entity " + str(self) + " was removed twice!")
	def getBlock(self):
		return (round(self.x / CELLSIZE), round(self.y / CELLSIZE))
	def createExplosion(self, rad):
		explosion(*self.getBlock(), rad)
	def opt_ai_calc(self):
		pass
	def drop(self, item):
		things.append(item(self.x + random.randint(-10, 10), self.y + random.randint(10, 25)))

class Player(Entity):
	color = (255, 0, 0)
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

class Monster(Entity):
	color = (0, 150, 0)
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.standing = False
		self.ticking = False
		self.direction = None
	def opt_ai_calc(self):
		if self.standing and random.random() < 0.06: self.vy = -3.1
		if self.direction:
			self.vx += self.direction
			if random.random() < 0.1: self.direction = None
		else:
			self.direction = random.choice([1, -1])
	def despawn(self):
		for i in range(random.choice([0, 1, 2, 3])):
			self.drop(Item)

class ExplodingMonster(Monster):
	color = (0, 255, 0)
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.standing = False
		self.ticking = False
		self.direction = None
	def despawn(self):
		self.createExplosion(3)
		for i in range(random.choice([0, 1, 2, 3])):
			self.drop(ScoreItem)

class Spawner(Entity):
	color = (0, 0, 150)
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.standing = False
		self.ticking = False
		self.direction = None
	def tickmove(self):
		if random.random() < 0.1: things.append(Monster(self.x, self.y))
		if random.random() < 0.005: things.append(ExplodingMonster(self.x, self.y))

class Item(Entity):
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 10
		self.standing = False
		self.img = "danger"
		self.ticking = False
		self.direction = None
		self.img_surface = pygame.transform.scale(pygame.image.load(self.img + ".png"), (10, 10))
	def draw(self, playerx, playery):
		screen.blit(self.img_surface, (self.x + (250 - playerx), self.y + (250 - playery)))
		if pygame.Rect(self.x, self.y, 10, 10).colliderect(pygame.Rect(playerx, playery, 10, 10)):
			self.die()
			gainitem(self.img)
		for t in things:
			if isinstance(t, Allay) and pygame.Rect(self.x, self.y, 10, 10).colliderect(pygame.Rect(t.x, t.y, 10, 10)):
				self.die()
				gainitem(self.img)
	def opt_ai_calc(self):
		if self.vy >= 0.5: self.vy = 0.5

class ScoreItem(Item):
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 10
		self.standing = False
		self.img = "score"
		self.direction = None
		self.ticking = False
		self.img_surface = pygame.transform.scale(pygame.image.load(self.img + ".png"), (10, 10))

class Particle(Entity):
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.standing = False
		self.img = "danger"
		self.ticks = 100
		self.direction = None
		self.ticking = False
		self.img_surface = pygame.image.load(self.img + ".png")
	def draw(self, playerx, playery):
		screen.blit(self.img_surface, (self.x + (250 - playerx) + (self.img_surface.get_width() * -0.5), self.y + (250 - playery) + (self.img_surface.get_width() * -0.5)))
		if self.ticks < 1:
			self.die()
	def tickmove(self):
		self.vy = 0
		self.vx = 0
		self.ticks -= 1

class MovingBlock(Entity):
	color = TAN
	def tickmove(self):
		if self.standing:
			self.y -= CELLSIZE / 2
			self.die()
		self.vx *= 1.8
	def despawn(self):
		b = self.getBlock()
		try:
			WORLD[b[0]][b[1]] = 4
		except:
			print("MovingBlock " + str(self) + " attempted to re-place block at: " + str(b[0]) + ", " + str(b[1]))

class Allay(Entity):
	color = (100, 100, 255)
	def opt_ai_calc(self):
		# Find a target.
		target = None
		targetdist = 1000
		for t in things:
			dist = math.sqrt(math.pow(t.x - self.x, 2) + math.pow(t.y - self.y, 2))
			# Find the closest Item, but if a ScoreItem is available, go for that instead.
			# 30% chance of targeting a different Item.
			if (dist < targetdist or random.random()<0.3 or isinstance(t, ScoreItem)) and isinstance(t, Item):
				target = t
				targetdist = dist
		if not target: return
		# Go left or right depending on where the target is.
		if target.x < self.x:
			self.vx -= 1
		else: self.vx += 1
		# If the target is more than half a block above me, jump.
		if target.y - self.y < -(CELLSIZE / 2) and self.standing: self.vy -= 3.1

def gainitem(item):
	if not item in items:
		items[item] = 0
	items[item] += 1

player = Player(100, 0)
things = []
items = {
	"danger": 0,
	"score": 0
}
tickingrefresh = 10
tickingcount = 0

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			player.despawn()
			# User clicked close button
		if event.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()
			if items["danger"] >= 15:
				items["danger"] -= 15
				things.append(Spawner(pos[0] + (player.x - 250), pos[1] + (player.y - 250)))
		if event.type == pygame.KEYDOWN:
			keys = pygame.key.get_pressed()
			if keys[pygame.K_SPACE]:
				if items["danger"] >= 10:
					items["danger"] -= 10
					player.createExplosion(2)
			if keys[pygame.K_z]:
				if items["danger"] >= 5:
					items["danger"] -= 5
					things.append(Spawner(random.randint(0, BOARDSIZE[0] * CELLSIZE), random.randint(0, BOARDSIZE[1] * CELLSIZE)))
			if keys[pygame.K_q]:
				for t in things:
					if isinstance(t, (Item, Monster, Spawner)) and not isinstance(t, ScoreItem):
						t.die()
			if keys[pygame.K_w]:
				things.append(Allay(player.x, player.y))
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
				if cell == 4:
					pygame.draw.rect(totalScreen, TAN, cellrect)
	# Ticking
	if tickingrefresh > 0:
		tickingrefresh -= 1
	else:
		tickingcount = 0
		tickingrefresh = 10
		keys = pygame.key.get_pressed()
		for t in things:
			if (abs(t.x - player.x) < 250) and (abs(t.y - player.y) < 250) or keys[pygame.K_a]:
				t.ticking = True
				tickingcount += 1
			else: t.ticking = False
	# Spawning
	if random.random() < 0.001:
		things.append(Spawner(random.randint(0, BOARDSIZE[0] * CELLSIZE), random.randint(0, BOARDSIZE[1] * CELLSIZE)))
	# Players & Screen
	player.tick()
	for t in things:
		t.tick()
	screen.blit(totalScreen, (250 - player.x, 250 - player.y))
	player.draw(player.x, player.y)
	for t in things:
		t.draw(player.x, player.y)
		# Despawning
		if random.random() < 0.005 and not isinstance(t, Item):
			t.die()
		elif random.random() < 0.0001 and isinstance(t, Item):
			t.die()
		# Dying
		elif t.y + 10 > BOARDSIZE[1] * CELLSIZE:
			t.die()
	# FLIP -----------------
	screen.blit(pygame.transform.scale(totalScreen, BOARDSIZE), (0, 0))
	w = FONT.render(f"{str(items['danger'])} danger items; Score: {str(items['score'])}", True, BLACK)
	screen.blit(w, (BOARDSIZE[0], 0))
	w = FONT.render(f"{str(len(things))} entities, {str(tickingcount)} ticking", True, BLACK)
	screen.blit(w, (0, BOARDSIZE[1]))
	pygame.display.flip()
	c.tick(60)
