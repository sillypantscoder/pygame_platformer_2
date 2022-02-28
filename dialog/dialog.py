import pygame
import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

f = open("dialog.txt", "r")
rawText = f.read().split("\n")
f.close()
msg = rawText[0]
options = rawText[1:]

def finish(s):
	pygame.quit()
	f = open("dialog.txt", "w")
	f.write(s)
	f.close()
	exit()

pygame.font.init()
FONT = pygame.font.Font(pygame.font.get_default_font(), 30)
msgRendered = FONT.render(msg, True, BLACK)
msgWidth = msgRendered.get_width()
msgHeight = msgRendered.get_height()
SCREENSIZE = [msgWidth + 100, msgHeight + 50 + msgHeight]
screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
# Loop
running = True
c = pygame.time.Clock()
option_width = (SCREENSIZE[0] - ((len(options) - 1) * 5)) / len(options)
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.VIDEORESIZE:
			SCREENSIZE = [*event.dict["size"]]
			screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
		elif event.type == pygame.MOUSEBUTTONUP:
			if pygame.mouse.get_pos()[1] < (SCREENSIZE[1] - msgHeight): continue
			pos = pygame.mouse.get_pos()[0]
			pos /= option_width
			pos = math.floor(pos)
			finish(options[pos])
	# Message
	screen.fill(WHITE)
	screen.blit(msgRendered, ((SCREENSIZE[0] - msgWidth) / 2, ((SCREENSIZE[1] - msgHeight) - msgHeight) / 2))
	# Options
	option_width = SCREENSIZE[0] / len(options)
	cum_x = 0
	pygame.draw.rect(screen, BLACK, pygame.Rect(0, SCREENSIZE[1] - msgHeight, SCREENSIZE[0], msgHeight))
	for o in options:
		oRendered = FONT.render(o, True, WHITE)
		screen.blit(oRendered, (cum_x + ((option_width - oRendered.get_width()) / 2), SCREENSIZE[1] - msgHeight))
		cum_x += option_width
		pygame.draw.line(screen, WHITE, (cum_x, SCREENSIZE[1] - msgHeight), (cum_x, SCREENSIZE[1]), 5)
	# Flip
	pygame.display.flip()
	c.tick(60)
# End
finish("")