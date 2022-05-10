from os import listdir, system
import sys
import random
import pygame
import json
import math
import datetime
import zipHelpers
from basics import *
import worldeditor
import ui
import threading

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

pygame.font.init()

WORLD: "list[list[str]]" = None
FONT = pygame.font.Font(pygame.font.get_default_font(), 30)
c = pygame.time.Clock()

screen = pygame.display.set_mode([500, 570])
ui.init(screen, FONT)

class HomeScreenHeader(ui.Header):
	def __init__(self): pass
	def render(self, mouse):
		# ZOMBIE
		cum_y = 20
		retext = FONT.render("Mode", True, WHITE)
		h = 40 + 100 + (retext.get_height())
		r = pygame.Surface((500, h))
		r.fill(BLACK)
		cum_y += retext.get_height()
		r.blit(retext, (20, h - cum_y))
		# APOCALYPSE
		retext = FONT.render("Apocalypse", True, WHITE)
		cum_y += retext.get_height()
		r.blit(retext, (20, h - cum_y))
		# MODE
		retext = FONT.render("Zombie", True, WHITE)
		cum_y += retext.get_height()
		r.blit(retext, (20, h - cum_y))
		return r

def MAIN():
	global entities
	global player
	global items
	global game_playing
	# HOME SCREEN
	homescreen = ui.UI().add(HomeScreenHeader())
	homescreen.add(ui.Spacer(40))
	homescreen.add(ui.Option("Play >"))
	ui.uimenu(homescreen)
	# PLAYING
	c = True
	while c:
		entities = []
		player = Player((BOARDSIZE[0] / 2) * CELLSIZE, (BOARDSIZE[1] / 2) * CELLSIZE)
		items = {
			"gem": 0
		}
		WORLDSELECTION()
		GENERATORSELECTION()
		game_playing = True
		c = PLAYING()
		game_playing = False
		# SAVING
		e = []
		for n in entities:
			if n.save_as != None:
				e.append([n.save_as, n.x, n.y])
		worldeditor.save(WORLD, e, [player.x, player.y], items, player.memory["health"])
		ENDGAME()

# WORLD SELECTION -----------------------------------------

gennewworld = True
alwaystick = True
doSpawning = True
autoapocalypse = False

def WORLDSELECTION():
	global gennewworld
	global alwaystick
	global doSpawning
	global autoapocalypse
	gennewworld = True
	alwaystick = True
	doSpawning = True
	autoapocalypse = False
	running = True
	while running:
		option = ui.menu("Zombie Apocalypse Mode", ["New world >", "Load save file >", "", "Auto Apocalypse: " + str(autoapocalypse), "", "Extensions"])
		if option == 0:
			running = False
		elif option == 1:
			gennewworld = False
			running = False
		elif option == 3:
			autoapocalypse = not autoapocalypse
		elif option == 5:
			EXTENSIONS()
		c.tick(60)
		pygame.display.flip()

# GENERATOR SELECTION

WORLD = []
rawStyleItems = {}
BLOCKS: "list[dict]" = []
textures: "dict[str, pygame.Surface]" = {}
LIGHT = [[False for x in range(BOARDSIZE[0])] for y in range(BOARDSIZE[1])]
def GENERATORSELECTION():
	global gennewworld
	global WORLD
	global screen
	global rawStyleItems
	global BLOCKS
	global textures
	global entities
	global player
	global items
	rawStyleItems = zipHelpers.extract_zip("style_env.zip").items
	BLOCKS = json.loads(rawStyleItems["blocks.json"].decode("UTF-8"))
	for filename in rawStyleItems:
		if "textures/" in filename:
			if filename[-1] != "/":
				try:
					textures[filename[9:]] = bytesToSurface(rawStyleItems[filename])
				except:
					print(filename)
					exit(1)
	generators = {}
	itemNames = []
	for filename in rawStyleItems:
		if "generators/" in filename:
			if filename != "generators/":
				generators[filename[11:]] = rawStyleItems[filename].decode("UTF-8")
				itemNames.append(filename[11:])
	if gennewworld:
		option = ui.menu("Select Generator", generators)
		f = open("generator.py", "w")
		f.write(generators[itemNames[option]])
		f.close()
		system("python3 generator.py")
		system("rm generator.py")
	# WORLD LOADING
	WORLD, e, playerpos, i, player.memory["health"] = worldeditor.load()
	for t in e:
		newEntity = {
			"monster": Monster,
			"exploding_monster": ExplodingMonster,
			"item_danger": Item,
			"item_score": ScoreItem,
			"allay": Allay,
			"allay_spawner": AllaySpawner
		}[t[0]]
		newEntity(t[1], t[2])
	player.x, player.y = playerpos
	for n in i.keys():
		for z in range(i[n]):
			gainitem(n)

# EXTENSION MANAGER

def EXTENSIONS():
	def addextension():
		ex = []
		e = listdir("extensions")
		for x in e:
			ex.append(x[:-4])
		optionui = ui.UI().add(ui.Header("Extensions")).add(ui.Button("Cancel"))
		for x in ex: optionui.add(ui.Option(x))
		option = ui.uimenu(optionui)
		if option < 2:
			pass
		else:
			system("python3 updateenv.py --add-extension " + ex[option - 3])
	running = True
	while running:
		currentExtension = zipHelpers.extract_zip("style_env.zip").items["meta.txt"].decode("UTF-8")[:-1]
		if currentExtension == "(No extension installed)":
			option = ui.uimenu(ui.UI().add(ui.Header("Extensions")).add(ui.Button("Back")).add(ui.Text("")).add(ui.Text("No extension installed")).add(ui.Option("Add extension")))
			if option == 1: running = False
			elif option == 4: addextension()
		else:
			option = ui.uimenu(ui.UI().add(ui.Header("Extensions")).add(ui.Button("Back")).add(ui.Text("")).add(ui.Text("Current extension: " + currentExtension)).add(ui.Option("Remove extension")))
			if option == 1: running = False
			elif option == 4: system("python3 updateenv.py --remove-extension --rm-hard")

# PLAYING -------------------------------------------------------------------------------------------------------------------------------------------

def bytesToSurface(b: bytes) -> pygame.Surface:
	f = open("texture.png", "wb")
	f.write(b)
	f.close()
	s = pygame.image.load("texture.png")
	system("rm texture.png")
	return s

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

def explosion(float_cx: float, float_cy: float, rad: int):
	"""Creates an explosion at the given coordinates with the given radius."""
	cx = round(float_cx)
	cy = round(float_cy)
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
	for t in [player, *entities]:
		dx = t.x - ((float_cx) * CELLSIZE)
		dy = t.y - ((float_cy + 0.2) * CELLSIZE)
		distanceFromExplosion = math.sqrt(dx ** 2 + dy ** 2)
		if distanceFromExplosion < (rad + 1) * CELLSIZE:
			dirx = dx / distanceFromExplosion if distanceFromExplosion > 0 else 0
			diry = dy / distanceFromExplosion if distanceFromExplosion > 0 else 0
			# if it's on the left of the explosion, it should fly out to the left.
			# if it's close to the explosion, it should fly out faster.
			# if it's far from the explosion, it should be less affected.
			# if t.x < cx (it's on the left of the explosion), then dx is negative
			power = 9
			dvx = dirx * (rad - (distanceFromExplosion/CELLSIZE)) * power * 2
			dvy = diry * (rad - (distanceFromExplosion/CELLSIZE)) * power
			t.vx += dvx
			t.vy += dvy
	for l in more:
		explosion(*l, 2)
	if random.random() < 0.3:
		Item((cx * CELLSIZE) + (0.5 * CELLSIZE), (cy * CELLSIZE) + (0.5 * CELLSIZE))

class Entity:
	save_as = None
	color = (0, 0, 0)
	def __init__(self, x, y):
		global entities
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.standing = False
		self.canjump = False
		self.ticking = True
		self.memory = None
		entities.append(self)
		self.initmemory()
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
		floor = BOARDSIZE[1] * CELLSIZE
		floor -= 10
		if self.y > floor:
			self.y = floor
			self.vy = -5
		if self.x < 0: self.vx += 0.5
		if self.x > BOARDSIZE[0] * CELLSIZE: self.vx -= 0.5
		if self.vx > 20 or self.vy > 20 or self.vx < -20 or self.vy < -20:
			self.vx = 0
			self.vy = 0
			errormsg(self, "went too fast")
		self.tickmove()
		if len(entities) < 20 or pygame.key.get_pressed()[pygame.K_a] or alwaystick: self.opt_ai_calc()
	def tickmove(self):
		pass
	def despawn(self):
		pass
	def die(self, despawn_first=True):
		if self in entities:
			if despawn_first: self.despawn()
			if self in entities: entities.remove(self)
		else: errormsg(self, "was removed twice")
	def getBlock(self):
		if not insideBoard(round(self.x / CELLSIZE), round(self.y / CELLSIZE)):
			# Out of bounds - clamp to edge
			if self.x < 0: self.x = 0
			if self.y < 0: self.y = 0
			if self.x > BOARDSIZE[0] * CELLSIZE: self.x = BOARDSIZE[0] * CELLSIZE
			if self.y > BOARDSIZE[1] * CELLSIZE: self.y = BOARDSIZE[1] * CELLSIZE
			return (0, 0)
		return (round(self.x / CELLSIZE), round(self.y / CELLSIZE))
	def createExplosion(self, rad):
		explosion(self.x / CELLSIZE, self.y / CELLSIZE, rad)
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
		self.memory = {"health": maxhealth, "direction": None, "target": None}
		entities.remove(self)
	def tickmove(self):
		if autoapocalypse:
			# Find a target.
			target = None
			targetdist = 1000
			for t in entities:
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
	save_as = "monster"
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

class ExplodingMonster(Monster):
	save_as = "exploding_monster"
	color = (0, 255, 0)
	def despawn(self):
		self.createExplosion(3)
		for i in range(random.choice([0, 1, 2, 3])):
			self.drop(ScoreItem)

class Item(Entity):
	save_as = "item_danger"
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
		for t in entities:
			if isinstance(t, Allay) and pygame.Rect(self.x, self.y, 10, 10).colliderect(pygame.Rect(t.x, t.y, 10, 10)):
				self.die()
				gainitem(self.memory["img"])
	def opt_ai_calc(self):
		if self.vy >= 0.5: self.vy = 0.5

class ScoreItem(Item):
	save_as = "item_score"
	def initmemory(self):
		self.memory = {"img": "score", "img_surface": None}

class Particle(Entity):
	# Particles do not need to be saved.
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
	# MovingBlocks cannot be saved because their memory needs to be set afterwards,
	# which is not possible with the current "list of names" strategy.
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
	save_as = "allay"
	color = (100, 100, 255)
	def opt_ai_calc(self):
		# Find a target.
		target = player
		targetdist = 1000
		for t in entities:
			dist = math.sqrt(math.pow(t.x - self.x, 2) + math.pow(t.y - self.y, 2))
			# Find the closest Item.
			if dist < targetdist and isinstance(t, Item):
				target = t
				targetdist = dist
		if not target: return
		# Go left or right depending on where the target is.
		# 1% chance kill myself.
		if random.random() < 0.01: self.die()
		if target.x < self.x:
			self.vx -= 1
		else: self.vx += 1
		# If the target is more than half a block above me, jump.
		if target.y - self.y < -(CELLSIZE / 2) and self.canjump: self.vy -= 3.1

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

class AllaySpawner(Entity):
	save_as = "allay_spawner"
	color = (0, 100, 150)
	def tickmove(self):
		if random.random() < 0.1: Allay(self.x, self.y)

def gainitem(item):
	if not item in items:
		items[item] = 0
	items[item] += 1

maxhealth = 100
entities: "list[Entity]" = []
player = Player((BOARDSIZE[0] / 2) * CELLSIZE, (BOARDSIZE[1] / 2) * CELLSIZE)
items = {
	"gem": 0
}
game_playing = False
def PLAYING():
	global entities
	global player
	global items
	tickingrefresh: int = 10
	tickingcount: int = 0
	fpscalc = datetime.datetime.now()
	fps: int = "???"
	minimap = pygame.transform.scale(totalScreen, BOARDSIZE)
	threading.Thread(target=PLAYING_ASYNC_LIGHT).start()
	while True:
		keys = pygame.key.get_pressed()
		pos = pygame.mouse.get_pos()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False;
				# User clicked close button
			if event.type == pygame.KEYDOWN:
				keys = pygame.key.get_pressed()
				if keys[pygame.K_SPACE]:
					if items["danger"] >= 10:
						items["danger"] -= 10
						player.createExplosion(2)
				if keys[pygame.K_q]:
					for t in entities:
						if isinstance(t, (Item, Monster, Particle)):
							t.die()
				if keys[pygame.K_ESCAPE]:
					if PAUSE(): return True;
					threading.Thread(target=PLAYING_ASYNC_LIGHT).start()
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
					if LIGHT[x][y] == False:
						l = pygame.Surface(cellrect.size)
						l.fill((0, 0, 0))
						l.set_alpha(200)
						totalScreen.blit(l, cellrect.topleft)
		# Ticking
		if tickingrefresh > 0:
			tickingrefresh -= 1
		else:
			tickingcount = 0
			tickingrefresh = 10
			keys = pygame.key.get_pressed()
			for t in entities:
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
						if LIGHT[x][y] == False:
							l = pygame.Surface(cellrect.size)
							l.fill((0, 0, 0))
							l.set_alpha(200)
							totalScreen.blit(l, cellrect.topleft)
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
		# Players & Screen
		player.tick()
		for t in entities:
			t.tick()
		screen.blit(totalScreen, (250 - player.x, 280 - player.y))
		player.draw(player.x, player.y)
		for t in entities:
			t.draw(player.x, player.y)
			# Despawning
			if random.random() < 0.005:
				t.die()
			# Dying
			elif t.y + 10 > BOARDSIZE[1] * CELLSIZE:
				t.die()
		if player.memory["health"] <= 0: return True
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
		w = FONT.render(f"{str(len(entities))} entities, {str(tickingcount)} ticking; FPS: {fps}", True, BLACK)
		screen.blit(w, (0, BOARDSIZE[1]))
		# Health bar
		pygame.draw.rect(screen, RED, pygame.Rect(0, 560, 500, 10))
		pygame.draw.rect(screen, GREEN, pygame.Rect(0, 560, player.memory["health"] * (500 / maxhealth), 10))
		# Flip
		pygame.display.flip()
		c.tick(60)

def PLAYING_ASYNC_LIGHT():
	global LIGHT
	c = pygame.time.Clock()
	while game_playing:
		# 1. Iterate over every block
		for x in range(BOARDSIZE[0]):
			for y in range(BOARDSIZE[1]):
				cell = WORLD[x][y]
				# 2. Check whether the block is exposed to the roof
				hasLight = True
				for cy in range(0, y):
					if BLOCKS[WORLD[x][cy]]["collision"] != "empty":
						hasLight = False
				LIGHT[x][y] = hasLight
				# 3. If the block is dark and is non-solid, there is a chance to spawn a monster
				if (not hasLight) and BLOCKS[cell]["collision"] == "empty" and random.random() < 0.00001:
					Monster(x * CELLSIZE, y * CELLSIZE)
				if BLOCKS[cell]["collision"] == "spawner" and random.random() < 0.01:
					Monster(x * CELLSIZE, y * CELLSIZE)
				# 4. There is always a chance to spawn an Allay
				#    because we are already spawning things so why not
				if BLOCKS[cell]["collision"] == "empty" and random.random() < 0.0001:
					Allay(x * CELLSIZE, y * CELLSIZE)
		c.tick(60)

# Pause menu

def PAUSE():
	global game_playing
	global entities
	global items
	game_playing = False
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
					game_playing = True
					return False;
				if exitrect.collidepoint(pos):
					game_playing = True
					return True;
			if event.type == pygame.KEYDOWN:
				keys = pygame.key.get_pressed()
				if keys[pygame.K_ESCAPE]:
					game_playing = True
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
		w = FONT.render(f"{str(len(entities))} entities", True, BLACK)
		screen.blit(w, (0, BOARDSIZE[1]))
		# Flip
		pygame.display.flip()
		c.tick(60)

# FUNCTION CALLS ==============================================================================================

MAIN()
