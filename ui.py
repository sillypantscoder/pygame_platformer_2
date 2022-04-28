import pygame
import typing

settings = {}

def init(screen, font):
	global settings
	settings = {
		"screen": screen,
		"font": font
	}

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class UIElement:
	"""Base class for an element in a UI. Renders as a 1x1 black pixel."""
	def __init__(self): pass
	def render(self, mouse):
		r = pygame.Surface((1, 1))
		r.fill(BLACK)
		return r
	def handleclick(self): pass

class Header(UIElement):
	"""A header for a UI. Renders as a white text against a black background."""
	def __init__(self, text):
		self.text = text
	def render(self, mouse):
		retext = settings["font"].render(self.text, True, WHITE)
		r = pygame.Surface((500, retext.get_height()))
		r.fill(BLACK)
		r.blit(retext, (0, 0))
		return r

class Text(UIElement):
	"""A text element. Renders as a white text against a black background. Cannot be clicked."""
	def __init__(self, text):
		self.text = text
	def render(self, mouse):
		retext = settings["font"].render(self.text, True, BLACK)
		r = pygame.Surface((500, retext.get_height()))
		r.fill(WHITE)
		r.blit(retext, (0, 0))
		return r

class Button(UIElement):
	"""A button. Renders as a white text against a black background. Can be clicked. When hovered, the text turns white with a black background."""
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
	"""A UI to be drawn to the screen. Contains a list of UIElements."""
	def __init__(self):
		self.items: list[UIElement] = []
	def add(self, item: UIElement):
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
	"""Renders a UI to the screen."""
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
	"""Displays a menu with the given header and items. Returns the index of the selected item."""
	def getitemcallback(finish):
		ui = [Header(header)] # Create the UI element list, with a header
		getclickerfunc = lambda i: (lambda: finish(i))
		index = 0
		for item in items:
			ui.append(Button(item).addclick(getclickerfunc(index)))
				# i is used to lock the index into the inner lambda
			index += 1
		return ui
	return listmenu(getitemcallback)

def listmenu(getitemcallback: "typing.Callable[[function], list[UIElement]]"):
	"""Displays a UI, with options for each element to return a specific value."""
	ui = UI() # Create the UI
	finished = [False, None] # 1st item stops the mainloop, 2nd item stores the selected item
	def finish(v):
		finished[0] = True
		finished[1] = v
	index = 0
	for item in getitemcallback(finish):
		ui.add(item)
		index += 1
	while not finished[0]:
		render_ui(ui)
	return finished[1]
