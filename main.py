from os import listdir, system
import sys
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

screen = pygame.display.set_mode([500, 560])

# WORLD SELECTION -----------------------------------------

wr = True
alwaystick = False

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
	# Always ticking?
	if alwaystick:
		a = FONT.render("Always tick entities: Y", True, BLACK)
	else:
		a = FONT.render("Always tick entities: N", True, BLACK)
	screen.blit(a, (0, wy + gy))
	ay = a.get_height() + wy + gy
	# Events
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
				elif pos[1] < ay:
					alwaystick = not alwaystick
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

def errormsg(entity, msg):
	if "--show-errors" in sys.argv:
		print(u"\u001b[31m" + f"[ {repr(entity)} {msg} ]" + u"\u001b[0m")
def debugmsg(msg):
	if "--show-debugs" in sys.argv:
		print(u"\u001b[33m" + f"[ {msg} ]" + u"\u001b[0m")

totalScreen = pygame.Surface((BOARDSIZE[0] * CELLSIZE, BOARDSIZE[1] * CELLSIZE))

def explosion(cx, cy, rad):
	if cx < 0 or cy < 0 or cx >= BOARDSIZE[0] or cy >= BOARDSIZE[1]: return
	WORLD[cx][cy] = 0
	debugmsg(f"explosion at ({cx},{cy}) rad={rad}")
	Particle((cx * CELLSIZE) + (0.5 * CELLSIZE), (cy * CELLSIZE) + (0.5 * CELLSIZE))
	more = []
	for x in range(cx - rad, cx + rad + 1):
		for y in range(cy - rad, cy + rad + 1):
			if ((x - cx) ** 2) + ((y - cy) ** 2) > (rad ** 2): continue
			if x < 0 or y < 0 or x >= BOARDSIZE[0] or y >= BOARDSIZE[1]: continue
			if WORLD[x][y] == 2:
				more.append([x, y])
				WORLD[x][y] = 0
			elif WORLD[x][y] == 1:
				WORLD[x][y] = 0
			elif WORLD[x][y] == 4:
				WORLD[x][y] = 0
				s = MovingBlock(x * CELLSIZE, y * CELLSIZE)
	for t in [player, *things]:
		dx = t.x - ((cx + 0.5) * CELLSIZE)
		dy = t.y - ((cy + 0.5) * CELLSIZE)
		distanceFromExplosion = math.sqrt(dx ** 2 + dy ** 2)
		if distanceFromExplosion < (rad + 1) * CELLSIZE:
			dirx = dx / distanceFromExplosion if distanceFromExplosion > 0 else 0
			diry = dy / distanceFromExplosion if distanceFromExplosion > 0 else 0
			# if it's on the left of the explosion, it should fly out to the left.
			# if it's close to the explosion, it should fly out faster.
			# if it's far from the explosion, it should be less affected.
			# if t.x < cx (it's on the left of the explosion), then dx is negative
			dvx = dirx * (rad - (distanceFromExplosion/CELLSIZE)) * 8
			dvy = diry * (rad - (distanceFromExplosion/CELLSIZE)) * 8
			t.vx += dvx
			t.vy += dvy
	for l in more:
		explosion(*l, 2)
	if random.random() < 0.3:
		Item((cx * CELLSIZE) + (0.5 * CELLSIZE), (cy * CELLSIZE) + (0.5 * CELLSIZE))

class Entity:
	color = (0, 0, 0)
	def __init__(self, x, y):
		global things
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.standing = False
		self.ticking = True
		self.memory = None
		self.initmemory()
		things.append(self)
	def draw(self, playerx, playery):
		pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, 10, 10).move((250 - playerx, 280 - playery)))
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
							errormsg(self, "jumped on sand at bottom of world")
						if fall:
							WORLD[math.floor(platform.left / CELLSIZE)][math.floor(platform.top / CELLSIZE)] = 0
							s = MovingBlock(*platform.topleft)
							s.vy = 3
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
			errormsg(self, "went too fast")
		self.tickmove()
		if len(things) < 20 or pygame.key.get_pressed()[pygame.K_a] or alwaystick: self.opt_ai_calc()
	def tickmove(self):
		pass
	def despawn(self):
		pass
	def die(self):
		if self in things:
			self.despawn()
			things.remove(self)
		else: errormsg(self, "was removed twice")
	def getBlock(self):
		return (round(self.x / CELLSIZE), round(self.y / CELLSIZE))
	def createExplosion(self, rad):
		explosion(*self.getBlock(), rad)
	def opt_ai_calc(self):
		pass
	def drop(self, item):
		item(self.x + random.randint(-10, 10), self.y + random.randint(10, 25))
	def initmemory(self):
		self.memory = {}

class Player(Entity):
	color = (255, 0, 0)
	def tickmove(self):
		if self in things: things.remove(self)
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
	def initmemory(self):
		self.memory = {"direction": None}
	def opt_ai_calc(self):
		if self.standing and random.random() < 0.06: self.vy = -3.1
		if self.memory["direction"]:
			self.vx += self.memory["direction"]
			if random.random() < 0.1: self.memory["direction"] = None
		else:
			self.memory["direction"] = random.choice([1, -1])
	def despawn(self):
		for i in range(random.choice([0, 1, 2, 3])):
			self.drop(Item)

class ExplodingMonster(Monster):
	color = (0, 255, 0)
	def despawn(self):
		self.createExplosion(3)
		for i in range(random.choice([0, 1, 2, 3])):
			self.drop(ScoreItem)

class Spawner(Entity):
	color = (0, 0, 150)
	def tickmove(self):
		if random.random() < 0.1: Monster(self.x, self.y)
		if random.random() < 0.005: ExplodingMonster(self.x, self.y)

class Item(Entity):
	def initmemory(self):
		self.memory = {"img": "danger", "img_surface": None}
	def draw(self, playerx, playery):
		if (not self.memory["img_surface"]): self.memory["img_surface"] = pygame.transform.scale(pygame.image.load(self.memory["img"] + ".png"), (10, 10))
		screen.blit(self.memory["img_surface"], (self.x + (250 - playerx), self.y + (280 - playery)))
		if pygame.Rect(self.x, self.y, 10, 10).colliderect(pygame.Rect(playerx, playery, 10, 10)):
			self.die()
			gainitem(self.memory["img"])
		for t in things:
			if isinstance(t, Allay) and pygame.Rect(self.x, self.y, 10, 10).colliderect(pygame.Rect(t.x, t.y, 10, 10)):
				self.die()
				gainitem(self.memory["img"])
	def opt_ai_calc(self):
		if self.vy >= 0.5: self.vy = 0.5



class ScoreItem(Item):
	def initmemory(self):
		self.memory = {"img": "score", "img_surface": None}

class Particle(Entity):
	def initmemory(self):
		self.memory = {"img": "danger", "img_surface": None, "ticks": 100}
	def draw(self, playerx, playery):
		if (not self.memory["img_surface"]): self.memory["img_surface"] = pygame.image.load(self.memory["img"] + ".png")
		screen.blit(self.memory["img_surface"], (self.x + (250 - playerx) + (self.memory["img_surface"].get_width() * -0.5), self.y + (280 - playery) + (self.memory["img_surface"].get_width() * -0.5)))
		if self.memory["ticks"] < 1:
			self.die()
	def tickmove(self):
		self.vy = 0
		self.vx = 0
		self.memory["ticks"] -= 1

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
			errormsg(self, "attempted to re-place block at: " + str(b[0]) + ", " + str(b[1]))

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

class AllaySpawner(Entity):
	color = (0, 100, 150)
	def tickmove(self):
		if random.random() < 0.1: Allay(self.x, self.y)

def gainitem(item):
	if not item in items:
		items[item] = 0
	items[item] += 1

things = []
player = Player(100, 0)
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
				Spawner(pos[0] + (player.x - 250), pos[1] + (player.y - 250))
		if event.type == pygame.KEYDOWN:
			keys = pygame.key.get_pressed()
			if keys[pygame.K_SPACE]:
				if items["danger"] >= 10:
					items["danger"] -= 10
					player.createExplosion(2)
			if keys[pygame.K_z]:
				if items["danger"] >= 5:
					items["danger"] -= 5
					Spawner(random.randint(0, BOARDSIZE[0] * CELLSIZE), random.randint(0, BOARDSIZE[1] * CELLSIZE))
			if keys[pygame.K_q]:
				for t in things:
					if isinstance(t, (Item, Monster, Spawner)) and not isinstance(t, ScoreItem):
						t.die()
			if keys[pygame.K_w]:
				AllaySpawner(player.x, player.y)
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
			if (abs(t.x - player.x) < 250) and (abs(t.y - player.y) < 250) or keys[pygame.K_a] or alwaystick:
				t.ticking = True
				tickingcount += 1
			else: t.ticking = False
	# Spawning
	if random.random() < 0.001:
		Spawner(random.randint(0, BOARDSIZE[0] * CELLSIZE), random.randint(0, BOARDSIZE[1] * CELLSIZE))
	# Players & Screen
	player.tick()
	for t in things:
		t.tick()
	screen.blit(totalScreen, (250 - player.x, 280 - player.y))
	player.draw(player.x, player.y)
	for t in things:
		t.draw(player.x, player.y)
		# Despawning
		if random.random() < 0.005 and not isinstance(t, Item):
			t.die()
		#elif random.random() < 0.0001 and isinstance(t, Item):
			#t.die()
		# Dying
		elif t.y + 10 > BOARDSIZE[1] * CELLSIZE:
			t.die()
	# FLIP -----------------
	pygame.draw.rect(screen, WHITE, pygame.Rect(0, 0, 500, 60))
	screen.blit(pygame.transform.scale(totalScreen, BOARDSIZE), (0, 0))
	w = FONT.render(f"{str(items['danger'])} danger items; Score: {str(items['score'])}", True, BLACK)
	screen.blit(w, (BOARDSIZE[0], 0))
	w = FONT.render(f"{str(len(things))} entities, {str(tickingcount)} ticking", True, BLACK)
	screen.blit(w, (0, BOARDSIZE[1]))
	pygame.display.flip()
	c.tick(60)
