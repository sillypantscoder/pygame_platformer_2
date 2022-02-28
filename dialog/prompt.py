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
userText = rawText[1]

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
cursorTicks = 0
# Loop
running = True
c = pygame.time.Clock()
pygame.key.set_repeat(500, 30)
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.VIDEORESIZE:
			SCREENSIZE = [*event.dict["size"]]
			screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
		elif event.type == pygame.KEYDOWN:
			keys = pygame.key.get_pressed()
			letterchars = [ord(char) for char in "abcdefghijklmnopqrstuvwxyz 1234567890.,/;'[]\\-="]
			if event.key in letterchars:
				k = chr(event.key)
				if pygame.key.get_mods() & pygame.KMOD_SHIFT:
					k = k.upper()
					if k in "0123456789": k = ")!@#$%^&*("[int(k)]
					trans = ",./;'[\]-="
					if k in trans: k = "<>?:\"{|}_+"[trans.find(k)]
				userText += k
			if keys[pygame.K_BACKSPACE]: userText = userText[:-1]
			if keys[pygame.K_RETURN]: finish(userText)
		elif event.type == pygame.MOUSEBUTTONUP:
			if pygame.mouse.get_pos()[1] < (SCREENSIZE[1] - msgHeight): continue
			finish(userText)
	# Message
	screen.fill(WHITE)
	screen.blit(msgRendered, ((SCREENSIZE[0] - msgWidth) / 2, ((SCREENSIZE[1] - msgHeight) - (msgHeight * 2)) / 2))
	# Textbox
	textboxY = ((SCREENSIZE[1] - msgHeight) - (msgHeight * 2)) / 2
	textboxY += msgHeight
	pygame.draw.rect(screen, BLACK, pygame.Rect(0, textboxY, SCREENSIZE[0], msgHeight), 5)
	# Cursor & Rendering
	cursorTicks += 1
	if cursorTicks >= 100:
		cursorTicks = 0
	if cursorTicks < 50:
		renderedUserText = FONT.render(userText + "|", True, BLACK)
	else:
		renderedUserText = FONT.render(userText, True, BLACK)
	screen.blit(renderedUserText, (0, textboxY))
	# OK button
	pygame.draw.rect(screen, BLACK, pygame.Rect(0, SCREENSIZE[1] - msgHeight, SCREENSIZE[0], msgHeight))
	r = FONT.render("OK", True, WHITE)
	screen.blit(r, ((SCREENSIZE[0] - r.get_width()) / 2, SCREENSIZE[1] - msgHeight))
	# Flip
	pygame.display.flip()
	c.tick(60)
# End
finish("")
