import random
import pygame

playerpos = [100, 0]
v = [0, 0]

BOARDSIZE = [30, 30]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
LIGHTRED = (255, 180, 180)
RED = (255, 0, 0)
WORLD = [[random.choice([0, 1]) for x in range(BOARDSIZE[0])] for y in range(BOARDSIZE[0])]
CELLSIZE = 50

screen = pygame.display.set_mode([500, 500])
totalScreen = pygame.Surface((BOARDSIZE[0] * CELLSIZE, BOARDSIZE[1] * CELLSIZE))

running = True
c = pygame.time.Clock()
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
			# User clicked close button
	keys = pygame.key.get_pressed()
	if keys[pygame.K_LEFT] and can_move_left:
		v[0] -= 1
	if keys[pygame.K_RIGHT] and can_move_right:
		v[0] += 1
	can_move_left = True
	can_move_right = True
	# DRAWING ------------
	screen.fill(GRAY)
	totalScreen.fill(WHITE)
	# Player
	playerpos[0] += v[0]
	playerpos[1] += v[1]
	pygame.draw.rect(screen, LIGHTRED, pygame.Rect(*playerpos, 10, 10).move((250 - playerpos[0], 250 - playerpos[1])))
	pygame.draw.rect(totalScreen, RED, pygame.Rect(*playerpos, 10, 10))
	touching_platforms = []
	# World
	for x in range(len(WORLD)):
		for y in range(len(WORLD[x])):
			cell = WORLD[x][y]
			if cell == 1:
				pygame.draw.rect(totalScreen, BLACK, pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE))
				if pygame.Rect(playerpos[0], playerpos[1] + 1, 10, 10).colliderect(pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)):
					touching_platforms.append(pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE))
	# Player v computations
	v[0] *= 0.5
	if len(touching_platforms) == 0:
		v[1] += 0.05
	else:
		for platform in touching_platforms:
			# Player is touching a platform!
			player = pygame.Rect(*playerpos, 10, 10)
			if platform.top - player.bottom > -10:
				# Player is standing on a platform!
				v[1] = 0
				playerpos[1] = platform.top - 10
				if keys[pygame.K_UP]:
					v[1] = -3
				pygame.draw.line(totalScreen, (0, 255, 0), platform.topleft, platform.topright, 5)
			else:
				if platform.left - player.right > -5:
					# Player is bumping into left side of platform!
					v[0] = -1
					pygame.draw.line(totalScreen, (0, 255, 0), platform.topleft, platform.bottomleft, 5)
				elif player.left - platform.right > -5:
					# Player is bumping into right side of platform!
					v[0] = 1
					pygame.draw.line(totalScreen, (0, 255, 0), platform.topright, platform.bottomright, 5)
				elif platform.bottom - player.top > -10:
					# Player is whacking into the top of a platform!
					v[1] = 0
					playerpos[1] = platform.bottom
					pygame.draw.line(totalScreen, (0, 255, 0), platform.bottomleft, platform.bottomright, 5)
	# Respawning
	if playerpos[1] > BOARDSIZE[1] * CELLSIZE:
		playerpos = [100, 0]
	# FLIP -----------------
	screen.blit(totalScreen, (250 - playerpos[0], 250 - playerpos[1]))
	pygame.display.flip()
	c.tick(60)
pygame.quit()
