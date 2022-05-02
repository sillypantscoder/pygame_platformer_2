import pygame
import subprocess
import os
import math

pygame.font.init()

WHITE = (255, 255, 255)

SCREENSIZE = [500, 500]
screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
FONT = pygame.font.SysFont(pygame.font.get_default_font(), 20)

subprocess.run(["git", "fetch"])
my_env = os.environ.copy()
my_env["GIT_PAGER"] = "/bin/cat"
commits = subprocess.run(["git", "log", "--reverse", "--pretty=%H", "origin/main"], stdout=subprocess.PIPE, env=my_env).stdout.decode("utf-8").split("\n")[:-1]

currentCommit = subprocess.run(["git", "rev-parse", "main"], stdout=subprocess.PIPE).stdout.decode("utf-8")[:-1]

def getPreviousCommit(hash):
	return commits[commits.index(hash) - 1]

def getNextCommits(hash):
	if len(commits) <= commits.index(hash) + 1: return []
	return [commits[commits.index(hash) + 1]]

def getPosition(hash):
	numprev = int(subprocess.run(["git", "rev-list", "--count", hash], stdout=subprocess.PIPE).stdout.decode("utf-8")) - 1
	return [0, numprev * 50]

def getCommitName(hash):
	return subprocess.run(["git", "show", hash, "--pretty=%s", "-s"], stdout=subprocess.PIPE).stdout.decode("utf-8")[:-1]

positions = [getPosition(i) for i in commits]
offset = [25, 25]
for h in commits:
	if h == currentCommit:
		offset = [(SCREENSIZE[0] / 4) - positions[commits.index(h)][0], SCREENSIZE[1] / 3 - positions[commits.index(h)][1]]

names = [getCommitName(i) for i in commits]

def MAIN():
	global screen
	global SCREENSIZE
	global currentCommit
	global offset
	c = pygame.time.Clock()
	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.VIDEORESIZE:
				SCREENSIZE = event.size
				screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
			elif event.type == pygame.MOUSEMOTION:
				if event.buttons[0]:
					offset[0] += event.rel[0]
					offset[1] += event.rel[1]
		# Drawing
		screen.fill(WHITE)
		for i in range(len(commits)):
			# Setup
			pos = positions[i][:]
			pos[0] += offset[0]
			pos[1] += offset[1]
			if math.dist(pos, pygame.mouse.get_pos()) > 1000: continue
			hovered = pygame.Rect(pos[0] - 25, pos[1] - 25, 50, 50).collidepoint(pygame.mouse.get_pos())
			# Draw the circle
			color = (0, 255, 0) if commits[i] == currentCommit else (0, 0, 0)
			pygame.draw.circle(screen, color, pos, (20 if hovered else 15))
			# Draw the lines to the next commits
			for n in getNextCommits(commits[i]):
				for j in range(len(commits)):
					if commits[j] == n:
						pygame.draw.line(screen, (0, 0, 0), pos, [positions[j][z] + offset[z] for z in range(len(positions[j]))], 5)
						break
		# Hover effects
		for ind in range(len(commits)):
			pos = positions[ind][:]
			pos[0] += offset[0]
			pos[1] += offset[1]
			i = commits[ind]
			if pygame.Rect(pos[0] - 25, pos[1] - 25, 50, 50).collidepoint(pygame.mouse.get_pos()):
				rendered = FONT.render(names[ind], True, (0, 0, 0))
				renderedSolid = pygame.Surface(rendered.get_size())
				renderedSolid.fill((255, 255, 255))
				renderedSolid.blit(rendered, (0, 0))
				screen.blit(renderedSolid, (pos[0] + 25, pos[1] - (rendered.get_height() / 2)))
				if pygame.mouse.get_pressed()[0]:
					MENU(i)
					currentCommit = subprocess.run(["git", "rev-parse", "main"], stdout=subprocess.PIPE).stdout.decode("utf-8")[:-1]
		# Update button
		commitsBehind = int(subprocess.run(["git", "rev-list", "--count", "origin/main...main"], stdout=subprocess.PIPE).stdout.decode("utf-8"))
		if commitsBehind > 0:
			rendered = FONT.render(f"{commitsBehind} commits behind; click to update", True, (255, 255, 255))
			updaterect = pygame.Rect(0, SCREENSIZE[1] - rendered.get_height(), rendered.get_width(), rendered.get_height())
			if updaterect.collidepoint(pygame.mouse.get_pos()):
				renderedSolid = pygame.Surface(rendered.get_size())
				renderedSolid.fill((0, 255, 255))
				renderedSolid.blit(rendered, (0, 0))
				screen.blit(renderedSolid, updaterect.topleft)
				if pygame.mouse.get_pressed()[0]:
					subprocess.run(["git", "pull"])
					currentCommit = subprocess.run(["git", "rev-parse", "main"], stdout=subprocess.PIPE).stdout.decode("utf-8")[:-1]
					for h in commits:
						if h == currentCommit:
							offset = [(SCREENSIZE[0] / 4) - positions[commits.index(h)][0], SCREENSIZE[1] / 3 - positions[commits.index(h)][1]]
			else:
				renderedSolid = pygame.Surface(rendered.get_size())
				renderedSolid.fill((0, 0, 255))
				renderedSolid.blit(rendered, (0, 0))
				screen.blit(renderedSolid, updaterect.topleft)
		pygame.display.flip()
		c.tick(10)

def MENU(selectedCommit: str):
	global screen
	global SCREENSIZE
	commitpos = positions[commits.index(selectedCommit)][:]
	dialogrect = pygame.Rect(commitpos[0] - 25, commitpos[1] - 25, 60 + FONT.render(names[commits.index(selectedCommit)], True, (0, 0, 0)).get_width(), 50)
	dialogrect.move_ip(*offset)
	c = pygame.time.Clock()
	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
			elif event.type == pygame.VIDEORESIZE:
				SCREENSIZE = event.size
				screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
			elif event.type == pygame.MOUSEBUTTONUP:
				if dialogrect.collidepoint(pygame.mouse.get_pos()):
					pass
				else:
					return
		# Drawing
		screen.fill(WHITE)
		for i in range(len(commits)):
			# Setup
			pos = positions[i][:]
			pos[0] += offset[0]
			pos[1] += offset[1]
			if math.dist(pos, pygame.mouse.get_pos()) > 1000: continue
			hovered = commits[i] == selectedCommit
			# Draw the circle
			color = (0, 255, 0) if commits[i] == currentCommit else (0, 0, 0)
			pygame.draw.circle(screen, color, pos, (20 if hovered else 15))
			# Draw the lines to the next commits
			for n in getNextCommits(commits[i]):
				for j in range(len(commits)):
					if commits[j] == n:
						pygame.draw.line(screen, (0, 0, 0), pos, [positions[j][z] + offset[z] for z in range(len(positions[j]))], 5)
						break
		# Hover effects
		for ind in range(len(commits)):
			pos = positions[ind][:]
			pos[0] += offset[0]
			pos[1] += offset[1]
			i = commits[ind]
			if i == selectedCommit:
				pygame.draw.rect(screen, (0, 0, 0), dialogrect, 1)
				rendered = FONT.render(names[ind], True, (0, 0, 0))
				renderedSolid = pygame.Surface(rendered.get_size())
				renderedSolid.fill((255, 255, 255))
				renderedSolid.blit(rendered, (0, 0))
				screen.blit(renderedSolid, (pos[0] + 25, pos[1] - (rendered.get_height() / 2)))
				# Go button
				rendered = FONT.render("Go here" if i != currentCommit else "Revert changes", True, (255, 255, 255))
				renderedSolid = pygame.Surface(rendered.get_size())
				renderedSolid.fill((0, 0, 255))
				renderedSolid.blit(rendered, (0, 0))
				pos = (dialogrect.left, dialogrect.bottom - rendered.get_height())
				screen.blit(renderedSolid, pos)
				textrect = pygame.Rect(*pos, *rendered.get_size())
				if textrect.collidepoint(pygame.mouse.get_pos()):
					if pygame.mouse.get_pressed()[0]:
						subprocess.run(["git", "reset", "--hard", i])
						return
		pygame.display.flip()
		c.tick(10)

MAIN()
