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
	def addclick(self, func): pass
	def __repr__(self): return "UIElement"

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
	def __repr__(self): return f"UIElement (Header \"{self.text}\")"

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
	def __repr__(self): return f"UIElement (Text \"{self.text}\")"

class Option(UIElement):
	"""A clickable text element. Renders as a white text against a black background. When hovered, the text turns white with a black background."""
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
	def __repr__(self): return f"UIElement (Option \"{self.text}\")"

class Button(UIElement):
	"""A button. Renders as a white text against a black background. Can be clicked. When hovered, the text turns black with a white background."""
	def __init__(self, text):
		self.text = text
		self.clickevents = []
	def render(self, mouse):
		retext = settings["font"].render(self.text, True, (BLACK if mouse else WHITE))
		r = pygame.Surface((500, retext.get_height() + 30))
		r.fill(WHITE)
		pygame.draw.rect(r, BLACK, (50, 10, 400, retext.get_height() + 10), 1 if mouse else 0)
		r.blit(retext, (((500) // 2) - (retext.get_width() // 2), 15))
		return r
	def addclick(self, handler):
		self.clickevents.append(handler)
		return self
	def handleclick(self):
		for handler in self.clickevents:
			handler()
	def __repr__(self): return f"UIElement (Button \"{self.text}\")"

class Spacer(UIElement):
	"""A spacer. Renders as a white bar."""
	def __init__(self, height):
		self.height = height
	def render(self, mouse):
		r = pygame.Surface((500, self.height))
		r.fill(WHITE)
		return r
	def __repr__(self): return f"UIElement (Spacer)"

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
	def __repr__(self): return f"UI [ {', '.join([str(i) for i in self.items])} ]"

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
	ui = UI().add(Header(header))
	for i in items:
		if i == "": ui.add(Text(""))
		else: ui.add(Option(i))
	return uimenu(ui) - 1

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

def uimenu(ui: UI):
	"""Displays an already-created UI object, with click handlers."""
	def getitemcallback(finish):
		u: list[UIElement] = [i for i in ui.items] # Create the UI element list
		getclickerfunc = lambda i: (lambda: finish(i))
		index = 0
		for item in u:
			item.addclick(getclickerfunc(index))
			index += 1
		return u
	return listmenu(getitemcallback)
