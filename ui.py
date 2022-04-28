import math
import pygame

settings = {}

def init(screen, font):
	global settings
	settings = {
		"screen": screen,
		"font": font
	}

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class UIelement:
	def __init__(self): pass
	def render(self, mouse):
		r = pygame.Surface((1, 1))
		r.fill(BLACK)
		return r
	def handleclick(self): pass

class Header(UIelement):
	def __init__(self, text):
		self.text = text
	def render(self, mouse):
		retext = settings["font"].render(self.text, True, WHITE)
		r = pygame.Surface((500, retext.get_height()))
		r.fill(BLACK)
		r.blit(retext, (0, 0))
		return r

class Text(UIelement):
	def __init__(self, text):
		self.text = text
	def render(self, mouse):
		retext = settings["font"].render(self.text, True, BLACK)
		r = pygame.Surface((500, retext.get_height()))
		r.fill(WHITE)
		r.blit(retext, (0, 0))
		return r

class Button(UIelement):
	def __init__(self, text):
		self.text = text
		self.clickevents = []
	def render(self, mouse):
		retext = settings["font"].render(self.text, True, (WHITE if mouse else BLACK))
		r = pygame.Surface((500, retext.get_height()))
		r.fill((BLACK if mouse else WHITE))
		r.blit(retext, (0, 0))
		return r
	def addclick(self, handler):
		self.clickevents.append(handler)
		return self
	def handleclick(self):
		for handler in self.clickevents:
			handler()

class UI:
	def __init__(self):
		self.items: list[UIelement] = []
	def add(self, item: UIelement):
		self.items.append(item)
		return self
	def render(self, mousepos, mouseclicked):
		scrn_height = 560
		scrn_width = 500
		rendered_items = []
		cum_y = 0
		for item in self.items:
			i = item.render(False)
			if i.get_rect().move(0, cum_y).collidepoint(mousepos):
				i = item.render(True)
				if mouseclicked:
					item.handleclick()
			rendered_items.append(i)
			if i.get_width() > scrn_width:
				scrn_width = i.get_width()
			cum_y += i.get_height()
		ret = pygame.Surface((scrn_width, scrn_height))
		ret.fill(WHITE)
		cum_y = 0
		for item in rendered_items:
			ret.blit(item, (0, cum_y))
			cum_y += item.get_height()
		return ret

def render_ui(ui: UI):
	clicked = False
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit(); exit()
			# User clicked close button
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = True
	m = pygame.mouse.get_pos()
	settings["screen"].blit(ui.render(m, clicked), (0, 0))
	pygame.display.flip()

def menu(header: str, items: "list[str]"):
	ui = UI().add(Header(header))
	finished = [False, None]
	def finish(v):
		finished[0] = True
		finished[1] = v
	index = 0
	for item in items:
		ui.add(Button(item).addclick((lambda i: (lambda: finish(i)))(index)))
		index += 1
	while not finished[0]:
		render_ui(ui)
	return finished[1]
