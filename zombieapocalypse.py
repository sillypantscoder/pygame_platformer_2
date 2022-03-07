from os import listdir, system
import sys
import random
import pygame
import json
import math
import datetime
import zipHelpers
from basics import *

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

pygame.font.init()

WORLD = None
FONT = pygame.font.Font(pygame.font.get_default_font(), 30)
c = pygame.time.Clock()
rawStyleItems = zipHelpers.extract_zip("style_env.zip").items
BLOCKS = json.loads(rawStyleItems["blocks.json"].decode("UTF-8"))

screen = pygame.display.set_mode([500, 570])

def MAIN():
	c = True
	while c:
		WORLDSELECTION()
		GENERATORSELECTION()
		c = PLAYING()
	ENDGAME()

# SELECTOR SCRIPT

def SELECTOR(items: list):
	global screen
	if 40 * len(items) > 560:
		screen = pygame.display.set_mode((500, 40 * len(items)))
	running = True
	while running:
		pos = pygame.mouse.get_pos()
		screen.fill(WHITE)
		h = 0
		for i in items:
			w = FONT.render(i, True, BLACK)
			if math.floor(pos[1] / 40) * 40 == h:
				w = FONT.render(i, True, WHITE)
				pygame.draw.rect(screen, BLACK, pygame.Rect(0, h, 500, 40))
			screen.blit(w, (0, h))
			h += 40
		# Events
		for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit(); exit()
					# User clicked close button
				if event.type == pygame.MOUSEBUTTONUP:
					pos = pygame.mouse.get_pos()
					if pos[1] < len(items) * 40:
						return math.floor(pos[1] / 40)
		c.tick(60)
		pygame.display.flip()
	screen = pygame.display.set_mode([500, 570])

# WORLD SELECTION -----------------------------------------

gennewworld = True
alwaystick = True
autoapocalypse = False

def WORLDSELECTION():
	global gennewworld
	global alwaystick
	running = True
	while running:
		option = SELECTOR(["Play >", "", "Generate new world: " + str(gennewworld), "Always tick entities: " + str(alwaystick)])
		if option == 0:
			running = False
		elif option == 2:
			gennewworld = not gennewworld
		elif option == 3:
			alwaystick = not alwaystick
		c.tick(60)
		pygame.display.flip()

# GENERATOR SELECTION

WORLD = []
def GENERATORSELECTION():
	global gennewworld
	global WORLD
	global screen
	items = {}
	itemNames = []
	for filename in rawStyleItems:
		if "generators/" in filename:
			if filename != "generators/":
				items[filename[11:]] = rawStyleItems[filename].decode("UTF-8")
				itemNames.append(filename[11:])
	if gennewworld:
		option = SELECTOR(items)
		f = open("generator.py", "w")
		f.write(items[itemNames[option]])
		f.close()
		system("python3 generator.py")
		system("rm generator.py")
	f = open("world.json", "r")
	WORLD = json.loads(f.read())
	f.close()

# PLAYING -------------------------------------------------

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

def errormsg(entity, msg):
	if "--show-errors" in sys.argv:
		print(u"\u001b[31m" + f"[ {repr(entity)} {msg} ]" + u"\u001b[0m")
def debugmsg(msg):
	if "--show-debugs" in sys.argv:
		print(u"\u001b[33m" + f"[ {msg} ]" + u"\u001b[0m")

totalScreen = pygame.Surface((BOARDSIZE[0] * CELLSIZE, BOARDSIZE[1] * CELLSIZE))

def insideBoard(x, y):
	if x < 0 or y < 0 or x >= BOARDSIZE[0] or y >= BOARDSIZE[1]: return False
	return True

def explosion(cx, cy, rad):
	if not insideBoard(cx, cy): return
	if WORLD[cx][cy] not in BLOCKS: return
	WORLD[cx][cy] = BLOCKS[WORLD[cx][cy]]["explosion"]
	debugmsg(f"explosion at ({cx},{cy}) rad={rad}")
	Particle((cx * CELLSIZE) + (0.5 * CELLSIZE), (cy * CELLSIZE) + (0.5 * CELLSIZE))
	more = []
	for x in range(cx - rad, cx + rad + 1):
		for y in range(cy - rad, cy + rad + 1):
			#if ((x - cx) ** 2) + ((y - cy) ** 2) > (rad ** 2): continue
			if not insideBoard(x, y): continue
			if WORLD[x][y] not in BLOCKS: continue
			if BLOCKS[WORLD[x][y]]["collision"] == "explode":
				more.append([x, y])
			elif BLOCKS[WORLD[x][y]]["collision"] == "fall":
				MovingBlock(x * CELLSIZE, y * CELLSIZE).memory["block"] = WORLD[x][y]
			WORLD[x][y] = BLOCKS[WORLD[x][y]]["explosion"]
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
		self.canjump = False
		self.ticking = True
		self.memory = None
		self.initmemory()
		things.append(self)
	def draw(self, playerx, playery):
		pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, 10, 10).move((250 - playerx, 280 - playery)))
	def tick(self):
		self.standing = False
		self.canjump = False
		if not self.ticking: return
		self.x += self.vx
		self.y += self.vy
		touching_platforms = []
		# World
		for x in range(round(self.x / CELLSIZE) - 2, round(self.x / CELLSIZE) + 2):
			for y in range(round(self.y / CELLSIZE) - 2, round(self.y / CELLSIZE) + 2):
				cellrect = pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
				if not insideBoard(x, y): continue
				if "--show-ticked-cells" in sys.argv: pygame.draw.rect(totalScreen, (0, 0, 200), cellrect, 5)
				cell = WORLD[x][y]
				if not cell in BLOCKS: continue
				if BLOCKS[cell]["collision"] in ["solid", "fall"]:
					if pygame.Rect(self.x, self.y + 1, 10, 10).colliderect(cellrect):
						touching_platforms.append(cellrect)
				if BLOCKS[cell]["collision"] == "explode":
					if pygame.Rect(self.x, self.y + 1, 10, 10).colliderect(cellrect):
						explosion(x, y, 2)
				if BLOCKS[cell]["collision"] == "swim":
					if pygame.Rect(self.x, self.y + 1, 10, 10).colliderect(cellrect):
						if self.vy > 1.5: self.vy = 1.5
						if self.vy < -1.5: self.vy = -1.5
						self.canjump = True
						pygame.draw.rect(totalScreen, GREEN, cellrect, 5)
		# Velocity computations
		self.vx *= 0.5
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
					self.canjump = True
					pygame.draw.line(totalScreen, (0, 255, 0), platform.topleft, platform.topright, 5)
					if BLOCKS[WORLD[math.floor(platform.left / CELLSIZE)][math.floor(platform.top / CELLSIZE)]]["collision"] == "fall":
						# Standing on sand!
						fall = False
						try:
							if BLOCKS[WORLD[math.floor(platform.left / CELLSIZE)][math.floor(platform.top / CELLSIZE) + 1]]["collision"] == "empty":
								fall = True
						except:
							fall = True
							errormsg(self, "jumped on falling block at bottom of world")
						if fall:
							s = MovingBlock(*platform.topleft)
							s.vy = 3
							s.memory["block"] = WORLD[math.floor(platform.left / CELLSIZE)][math.floor(platform.top / CELLSIZE)]
							WORLD[math.floor(platform.left / CELLSIZE)][math.floor(platform.top / CELLSIZE)] = "air"
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
			self.x = (BOARDSIZE[0] / 2) * CELLSIZE
			self.y = (BOARDSIZE[1] / 2) * CELLSIZE
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
	def draw(self, playerx, playery):
		mvx = 250 - playerx
		mvy = 280 - playery
		pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, 10, 10).move((mvx, mvy)))
		if self.memory["target"]:
			color = GREEN
			if isinstance(self.memory["target"], Monster): color = RED
			pygame.draw.line(screen, color, (self.x + mvx + 5, self.y + mvy + 5), (self.memory["target"].x + mvx + 5, self.memory["target"].y + mvy + 5))
	def initmemory(self):
		self.memory = {"health": 100, "direction": None, "target": None}
	def tickmove(self):
		if self in things: things.remove(self)
		if autoapocalypse:
			# Find a target.
			target = None
			targetdist = 1000
			for t in things:
				dist = math.sqrt(math.pow(t.x - self.x, 2) + math.pow(t.y - self.y, 2))
				# Find the closest Item or Monster within screen size.
				if (dist < targetdist) and (isinstance(t, Item) or (isinstance(t, Monster) and dist < CELLSIZE * 5)):
					target = t
					targetdist = dist
			self.memory["target"] = target
			if isinstance(target, Item):
				# Go left or right depending on where the target is.
				if target.x < self.x:
					self.vx -= 1
				else: self.vx += 1
				# If the target is more than half a block above me, jump.
				if target.y - self.y < -(CELLSIZE / 2) and self.canjump: self.vy -= 3.1
			elif isinstance(target, Monster):
				# Go right or left depending on where the target is.
				if target.x < self.x:
					self.vx += 1
				else: self.vx -= 1
				# If the target is not more than half a block above me, jump.
				if target.y - self.y >= -(CELLSIZE / 2) and self.canjump: self.vy -= 3.1
			else:
				if self.canjump and random.random() < 0.06: self.vy = -3.1
				if self.memory["direction"]:
					self.vx += self.memory["direction"]
					if random.random() < 0.1: self.memory["direction"] = None
				else:
					self.memory["direction"] = random.choice([1, -1])
		else:
			keys = pygame.key.get_pressed()
			if keys[pygame.K_LEFT]:
				self.vx -= 1
			if keys[pygame.K_RIGHT]:
				self.vx += 1
			if keys[pygame.K_UP] and self.canjump:
				self.vy = -3.1

class Monster(Entity):
	color = (0, 150, 0)
	def initmemory(self):
		self.memory = {"direction": None}
	def tickmove(self):
		if pygame.Rect(self.x, self.y, 10, 10).colliderect(pygame.Rect(player.x, player.y, 10, 10)):
			player.memory["health"] -= 1
	def opt_ai_calc(self):
		# Find a target.
		target = player
		# Go left or right depending on where the target is.
		if target.x < self.x:
			self.vx -= 1
		else: self.vx += 1
		# If the target is more than half a block above me, jump.
		if target.y - self.y < -(CELLSIZE / 2) and self.canjump: self.vy -= 3.1
	def despawn(self):
		for i in range(random.choice([0, 1, 2, 3])):
			self.drop(Item)

class Item(Entity):
	def initmemory(self):
		self.memory = {"img": "gem", "img_surface": None}
	def draw(self, playerx, playery):
		#size = 5 + (self.memory["stacksize"] * 5)
		size = 11
		self.memory["img_surface"] = pygame.transform.scale(textures["item/" + self.memory["img"] + ".png"], (size, size))
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

class Particle(Entity):
	def initmemory(self):
		self.memory = {"img": "danger", "img_surface": None, "ticks": 100, "size": 0}
	def draw(self, playerx, playery):
		if self.memory["ticks"] > 70: self.memory["size"] += 2
		if (not self.memory["img_surface"]): self.memory["img_surface"] = textures["particle/" + self.memory["img"] + ".png"]
		toDraw = pygame.transform.scale(self.memory["img_surface"], (self.memory["size"], self.memory["size"]))
		drawX = self.x + (250 - playerx) + (self.memory["img_surface"].get_width() * -0.5)
		drawY = self.y + (280 - playery) + (self.memory["img_surface"].get_height() * -0.5)
		offsetX = (self.memory["img_surface"].get_width() - self.memory["size"]) / 2
		offsetY = (self.memory["img_surface"].get_height() - self.memory["size"]) / 2
		screen.blit(toDraw, (drawX + offsetX, drawY + offsetY))
		# and the red ring
		if self.memory["ticks"] > 70:
			pygame.draw.circle(screen, RED, (round(drawX + (CELLSIZE / 4)), round(drawY + (CELLSIZE / 4))), self.memory["size"] + 5, 5)
		if self.memory["ticks"] < 1:
			self.die()
	def tickmove(self):
		self.vy = 0
		self.vx = 0
		self.memory["ticks"] -= 1

class MovingBlock(Entity):
	color = TAN
	def initmemory(self):
		self.memory = {"block": "sand"}
	def tickmove(self):
		if self.standing:
			self.y -= CELLSIZE / 2
			self.die()
		self.vx *= 1.8
	def despawn(self):
		b = self.getBlock()
		try:
			WORLD[b[0]][b[1]] = self.memory["block"]
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
			# Find the closest Item.
			if dist < targetdist and isinstance(t, Item):
				target = t
				targetdist = dist
		if not target: return
		# Go left or right depending on where the target is.
		if target.x < self.x:
			self.vx -= 1
		else: self.vx += 1
		# If the target is more than half a block above me, jump.
		if target.y - self.y < -(CELLSIZE / 2) and self.canjump: self.vy -= 3.1
		# 1% chance kill myself.
		if random.random() < 0.01: self.die()

def ENDGAME():
	global player
	wc = FONT.render("Click anywhere to exit", True, BLACK)
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return;
				# User clicked close button
			if event.type == pygame.MOUSEBUTTONUP:
				return;
		screen.fill(WHITE)
		w = FONT.render(f"Score: {str(items['gem'])}", True, BLACK)
		screen.blit(w, (CELLSIZE, CELLSIZE))
		screen.blit(wc, (CELLSIZE, CELLSIZE + w.get_height() + 10))
		pygame.display.flip()
		c.tick(60)

def gainitem(item):
	if not item in items:
		items[item] = 0
	items[item] += 1

things = []
player = Player((BOARDSIZE[0] / 2) * CELLSIZE, (BOARDSIZE[1] / 2) * CELLSIZE)
items = {
	"gem": 0
}
def PLAYING():
	global things
	global player
	global items
	tickingrefresh = 10
	tickingcount = 0
	fpscalc = datetime.datetime.now()
	fps = "???"
	minimap = pygame.transform.scale(totalScreen, BOARDSIZE)
	while True:
		keys = pygame.key.get_pressed()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False;
				# User clicked close button
			if event.type == pygame.KEYDOWN:
				keys = pygame.key.get_pressed()
				if keys[pygame.K_SPACE]:
					for zzz in range(30):
						pos = (random.randint(0, BOARDSIZE[0] * CELLSIZE), random.randint(0, BOARDSIZE[1] * CELLSIZE))
						Monster(*pos)
				if keys[pygame.K_q]:
					for t in things:
						if isinstance(t, (Item, Monster, Particle)):
							t.die()
				if keys[pygame.K_ESCAPE]:
					if PAUSE(): return True;
		if keys[pygame.K_w]:
			Allay(player.x, player.y)
		# DRAWING ------------
		screen.fill(GRAY)
		totalScreen.fill(WHITE)
		# Board
		sets = []
		for x in range(round(player.x / CELLSIZE) - 7, round(player.x / CELLSIZE) + 7):
				for y in range(round(player.y / CELLSIZE) - 7, round(player.y / CELLSIZE) + 7):
					if not insideBoard(x, y): continue
					cell = WORLD[x][y]
					cellrect = pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
					if cell in BLOCKS:
						if BLOCKS[cell]["color"] == False: totalScreen.blit(textures["block/" + cell + ".png"], cellrect.topleft)
						else: pygame.draw.rect(totalScreen, BLOCKS[cell]["color"], cellrect)
					else:
						pygame.draw.rect(totalScreen, (255, 0, 255), cellrect)
						pygame.draw.rect(totalScreen, (0, 0, 0), pygame.Rect(*cellrect.topleft, CELLSIZE / 2, CELLSIZE / 2))
						pygame.draw.rect(totalScreen, (0, 0, 0), pygame.Rect(*cellrect.center, CELLSIZE / 2, CELLSIZE / 2))
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
			for x in range(len(WORLD)):
				for y in range(len(WORLD[x])):
					cell = WORLD[x][y]
					cellrect = pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
					if cell in BLOCKS:
						if BLOCKS[cell]["color"] == False: totalScreen.blit(textures["block/" + cell + ".png"], cellrect.topleft)
						else: pygame.draw.rect(totalScreen, BLOCKS[cell]["color"], cellrect)
						# FLUIDS
						if BLOCKS[cell]["fluid"] == "source":
							# Fall down
							if insideBoard(x, y + 1) and (WORLD[x][y + 1] in BLOCKS) and BLOCKS[WORLD[x][y + 1]]["collision"] == "empty":
								sets.append({"pos": (x, y + 1), "state": "flowing_" + cell})
							elif insideBoard(x, y + 1) and (WORLD[x][y + 1] in BLOCKS) and BLOCKS[WORLD[x][y + 1]]["collision"] == "solid":
								# Or flow left
								if insideBoard(x - 1, y) and (WORLD[x - 1][y] in BLOCKS) and BLOCKS[WORLD[x - 1][y]]["collision"] == "empty":
									sets.append({"pos": (x - 1, y), "state": "flowing_" + cell})
								# Or flow right
								if insideBoard(x + 1, y) and (WORLD[x + 1][y] in BLOCKS) and BLOCKS[WORLD[x + 1][y]]["collision"] == "empty":
									sets.append({"pos": (x + 1, y), "state": "flowing_" + cell})
						if BLOCKS[cell]["fluid"] == "flowing":
							# Stop falling
							sets.append({"pos": (x, y), "state": "air"})
							if WORLD[x][y - 1] in [cell, cell[8:]] and y - 1 >= 0:
								sets.append({"pos": (x, y), "state": cell})
							if insideBoard(x + 1, y) and WORLD[x + 1][y] in [cell, cell[8:]]:
								sets.append({"pos": (x, y), "state": cell})
							if insideBoard(x - 1, y) and WORLD[x - 1][y] in [cell, cell[8:]]:
								sets.append({"pos": (x, y), "state": cell})
							# Fall down
							if insideBoard(x, y + 1) and WORLD[x][y + 1] in BLOCKS and BLOCKS[WORLD[x][y + 1]]["collision"] == "empty":
								sets.append({"pos": (x, y + 1), "state": cell})
							elif insideBoard(x, y + 1) and WORLD[x][y + 1] in BLOCKS and BLOCKS[WORLD[x][y + 1]]["collision"] == "solid":
								# Or flow left
								if insideBoard(x - 1, y) and WORLD[x - 1][y] in BLOCKS and BLOCKS[WORLD[x - 1][y]]["collision"] == "empty":
									sets.append({"pos": (x - 1, y), "state": cell})
								# Or flow right
								if insideBoard(x + 1, y) and WORLD[x + 1][y] in BLOCKS and BLOCKS[WORLD[x + 1][y]]["collision"] == "empty":
									sets.append({"pos": (x + 1, y), "state": cell})
			minimap = pygame.transform.scale(totalScreen, BOARDSIZE)
		# Fluids and scheduled ticks
		for s in sets:
			WORLD[s["pos"][0]][s["pos"][1]] = s["state"]
		# Spawning
		if random.random() < (0.01 * items["gem"]) + 0.05:
			pos = (random.randint(0, BOARDSIZE[0] * CELLSIZE), random.randint(0, BOARDSIZE[1] * CELLSIZE))
			Monster(*pos)
			Particle(*pos)
		# Players & Screen
		player.tick()
		for t in things:
			t.tick()
		screen.blit(totalScreen, (250 - player.x, 280 - player.y))
		player.draw(player.x, player.y)
		for t in things:
			t.draw(player.x, player.y)
			# Despawning
			if random.random() < 0.005:
				t.die()
			# Dying
			elif t.y + 10 > BOARDSIZE[1] * CELLSIZE:
				t.die()
		if player.memory["health"] <= 0: return False
		# FLIP -----------------
		# Framerate
		if tickingrefresh == 1:
			newf = datetime.datetime.now()
			sec = (newf - fpscalc).total_seconds()
			fps = round(1/sec)
		if tickingrefresh == 2:
			fpscalc = datetime.datetime.now()
		# Debug info
		pygame.draw.rect(screen, WHITE, pygame.Rect(0, 0, 500, 60))
		screen.blit(minimap, (0, 0))
		w = FONT.render(f"Score: {str(items['gem'])}, HP: {str(player.memory['health'])}", True, BLACK)
		screen.blit(w, (BOARDSIZE[0], 0))
		w = FONT.render(f"{str(len(things))} entities, {str(tickingcount)} ticking; FPS: {fps}", True, BLACK)
		screen.blit(w, (0, BOARDSIZE[1]))
		# Health bar
		pygame.draw.rect(screen, RED, pygame.Rect(0, 560, 500, 10))
		pygame.draw.rect(screen, GREEN, pygame.Rect(0, 560, player.memory["health"] * 5, 10))
		# Flip
		pygame.display.flip()
		c.tick(60)

# Pause menu

def PAUSE():
	global things
	global items
	fps = "???"
	continuerect = pygame.Rect(50, 150, 400, 50)
	exitrect = pygame.Rect(50, 210, 400, 50)
	while True:
		pos = pygame.mouse.get_pos()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
				# User clicked close button
			if event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()
				if continuerect.collidepoint(pos):
					return False;
				if exitrect.collidepoint(pos):
					return True;
			if event.type == pygame.KEYDOWN:
				keys = pygame.key.get_pressed()
				if keys[pygame.K_ESCAPE]:
					return False;
		# DRAWING ------------
		screen.fill(GRAY)
		t = FONT.render("Paused", True, BLACK)
		screen.blit(t, ((500 - t.get_width()) / 2, 75))
		# Continue button
		pygame.draw.rect(screen, BLACK, continuerect)
		t = FONT.render("Resume", True, WHITE)
		if continuerect.collidepoint(pos):
			pygame.draw.rect(screen, WHITE, continuerect)
			t = FONT.render("Resume", True, BLACK)
		screen.blit(t, ((500 - t.get_width()) / 2, 160))
		# Exit button
		pygame.draw.rect(screen, BLACK, exitrect)
		t = FONT.render("Return to title screen", True, WHITE)
		if exitrect.collidepoint(pos):
			pygame.draw.rect(screen, WHITE, exitrect)
			t = FONT.render("Return to title screen", True, BLACK)
		screen.blit(t, ((500 - t.get_width()) / 2, 220))
		# FLIP -----------------
		# Debug info
		pygame.draw.rect(screen, WHITE, pygame.Rect(0, 0, 500, 60))
		minimap_pause = pygame.Surface(BOARDSIZE)
		minimap_pause.fill(WHITE)
		pygame.draw.rect(minimap_pause, GRAY, pygame.Rect(5, 5, 5, 20))
		pygame.draw.rect(minimap_pause, BLACK, pygame.Rect(6, 6, 5, 20))
		pygame.draw.rect(minimap_pause, GRAY, pygame.Rect(15, 5, 5, 20))
		pygame.draw.rect(minimap_pause, BLACK, pygame.Rect(16, 6, 5, 20))
		screen.blit(minimap_pause, (0, 0))
		w = FONT.render(f"Score: {str(items['gem'])}, HP: {str(player.memory['health'])}", True, BLACK)
		screen.blit(w, (BOARDSIZE[0], 0))
		w = FONT.render(f"{str(len(things))} entities", True, BLACK)
		screen.blit(w, (0, BOARDSIZE[1]))
		# Flip
		pygame.display.flip()
		c.tick(60)

# FUNCTION CALLS ==============================================================================================

MAIN()