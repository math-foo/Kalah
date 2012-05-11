#!/usr/bin/python

#    Copyright 2012, Caelyn McAulay

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygame
from pygame.locals import *
import random

def make_move(hole_moved_indice):
	global all_holes, screen, background, current_player, player_1,_hand, player_2_hand

	if current_player == 1:
		player_hand = player_1_hand
		next_player = 2
	else:
		player_hand = player_2_hand
		next_player = 1

	c = len(all_holes)

	i = hole_moved_indice

	beads_to_move = all_holes[i].beads

	all_holes[i].beads = []
	all_holes[i].bead_count = 0

	i += 1
	i %= c

	switch_players = True	

	player_hand.bead_count = len(beads_to_move)

	bead_new_location = []

	while len(beads_to_move) > 0:
		if all_holes[i].standard or all_holes[i].player == current_player:
			cur_bead = beads_to_move.pop()
			player_hand.beads.append(cur_bead)
			bead_new_location.append(i)

			if all_holes[i].standard:
				switch_players = True
			else:
				switch_players = False

		i += 1
		i %= c


	screen.blit(background, (0,0))

	if switch_players:
		current_player = next_player

	game_over = True

	player_1_score = 0
	player_2_score = 0

	for hole in all_holes:
		if not hole.standard:
			if hole.player == 1:
				player_1_score = hole.bead_count
			else:
				player_2_score = hole.bead_count
			
			hole.draw_beads(screen)
	
		elif hole.player == current_player:
			if hole.draw_beads(screen):
				game_over = False
		else:
			hole.draw_beads(screen)

	player_hand.draw_beads(screen)
	pygame.display.flip()
	moving_bead = None
	destination = None
	dest_hole = None

	while True:
		if moving_bead == None:
			indice = bead_new_location.pop(0)
			dest_hole = all_holes[indice]
			destination = (dest_hole.rect.centerx, dest_hole.rect.centery)

			moving_bead = player_hand.beads.pop(0)
			player_hand.bead_count -= 1

			moving_bead.pos = [player_hand.rect.centerx, player_hand.rect.centery]
		else:
			if moving_bead.pos[0] == destination[0]:
				i = 1
			elif moving_bead.pos[1] == destination[1]:
				i = 0
			else:
				i = random.randint(0,1)

			
			if moving_bead.pos[i] > destination[i]:
				moving_bead.pos[i] -= 1
			else:
				moving_bead.pos[i] += 1

		screen.blit(background,(0,0))
		
		for hole in all_holes:
			hole.draw_beads(screen)

		player_hand.draw_beads(screen)

		moving_bead.draw(screen)
		
		pygame.display.flip()
		

		if moving_bead.pos[0] == destination[0] and moving_bead.pos[1] == destination[1]:
			dest_hole.beads.append(moving_bead)
			dest_hole.bead_count += 1
			moving_bead = None
			if len(bead_new_location) == 0:
				break

			
	screen.blit(background,(0,0))
		
	for hole in all_holes:
		hole.draw_beads(screen)

	if pygame.font:
		if game_over:
			font = pygame.font.Font(None, 36)

			if   player_1_score > player_2_score:
				text = font.render("Player 1 Wins!",1, (0,0,0))
			elif player_2_score > player_1_score:
				text = font.render("Player 2 Wins!",1, (0,0,0))
			else:
				text = font.render("A Tie!",1, (0,0,0))

			text_pos = text.get_rect()
			text_pos.centerx = screen.get_rect().centerx
			screen.blit(text,text_pos)
		else:
			font = pygame.font.Font(None, 36)

			text = font.render("Player "+str(current_player)+"'s Turn",1, (0,0,0))

			text_pos = text.get_rect()
			text_pos.centerx = screen.get_rect().centerx 
			screen.blit(text,text_pos)

	pygame.display.flip()



class Bead:

	def __init__(self):
		self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
		self. pos = None

	def draw(self, location, surface=None):
		if surface == None:
			surface = location
			location = self.pos
		else:
			self.pos = location

		pygame.draw.circle(surface, (0,0,0),       location,                            10)
		pygame.draw.circle(surface, self.color,    location,                            9)
		pygame.draw.circle(surface, (255,255,255), (location[0]+2, location[1]+2),      1 )


class Hole:

	def __init__(self, rect, player, standard):
		self.rect = rect
		self.beads = []
		self.bead_count = 0
		self.player = player
		self.standard = standard


	def draw_beads(self,surface):
		x = self.rect.centerx
		y = self.rect.centery

		standard = self.standard
		beads = self.beads

		if self.bead_count == 0:
			return False
		elif self.bead_count == 1:
			beads[0].draw((x,y), surface)
		elif self.bead_count == 2:	
			beads[0].draw((x,y+20), surface)
			beads[1].draw((x,y-20), surface)
		elif self.bead_count == 3:
			if standard:
				beads[0].draw((x,y+25), surface)
				beads[1].draw((x,y-25), surface)
				beads[2].draw((x,y), surface)
			else:
				beads[0].draw((x,y+30), surface)
				beads[1].draw((x,y-30), surface)
				beads[2].draw((x,y), surface)
		elif self.bead_count == 4:
			if standard:
				beads[0].draw((x+12,y+12), surface)
				beads[1].draw((x+12,y-12), surface)
				beads[2].draw((x-12,y+12), surface)
				beads[3].draw((x-12,y-12), surface)
			else:
				beads[0].draw((x,y+45), surface)
				beads[1].draw((x,y-45), surface)
				beads[2].draw((x,y+15), surface)
				beads[3].draw((x,y-15), surface)
		elif self.bead_count == 5:
			if standard:
				beads[0].draw((x+15,y+15), surface)
				beads[1].draw((x+15,y-15), surface)
				beads[2].draw((x-15,y+15), surface)
				beads[3].draw((x-15,y-15), surface)
				beads[4].draw((x,y), surface)
			else:
				beads[0].draw((x,y+60), surface)
				beads[1].draw((x,y-60), surface)
				beads[2].draw((x,y+30), surface)
				beads[3].draw((x,y-30), surface)
				beads[3].draw((x,y), surface)
		else:
			beads[0].draw((x,y-20), surface)

			for bead in beads:
				bead.pos = None

			if pygame.font:
				font = pygame.font.Font(None, 24)
				text = font.render(str(self.bead_count),1, (0,0,0))
				text_pos = text.get_rect()
				text_pos.centerx = x
				text_pos.centery = y+20
				surface.blit(text,text_pos)

		return True


	def is_clicked(self, player):
		if self.standard:
			if self.player == player:
				if self.bead_count > 0:
					pos = pygame.mouse.get_pos()
					if self.rect.collidepoint(pos):
						return True

		return False



pygame.init()

screen = pygame.display.set_mode((800,400))
pygame.display.set_caption("Kalah")

current_player = 1

#Creating the background surface
background = pygame.Surface(screen.get_size())
background = background.convert()

background.fill((255,255,255))

board = pygame.image.load("board.png")
board = board.convert()

colorkey = board.get_at((0,0))

board.set_colorkey(colorkey, RLEACCEL)

background.blit(board, (100,100))
screen.blit(background,(0,0))

#Creating the text layer
if pygame.font:
	font = pygame.font.Font(None, 36)
	text = font.render("Player "+str(current_player)+"'s Turn",1, (0,0,0))
	text_pos = text.get_rect()
	text_pos.centerx = screen.get_rect().centerx
	screen.blit(text,text_pos)


#Creating the bead layer

player_1_hand = Hole(pygame.Rect(500,300,75,100),1,True)
player_2_hand = Hole(pygame.Rect(125,0  ,75,100),1,True)

all_holes = []

for i in xrange(0,14):
	if i == 0 or i == 7:
		standard = False
	else:
		standard = True

	if standard:
		new_rect = pygame.Rect(0,0,75,100)
		if i < 7:
			player = 1
			new_rect.top = 100

		if i > 7:
			player = 2
			i -= 14
			i *= -1

		new_rect.left = i*75
	else:
		new_rect = pygame.Rect(0,0,75,200)
		
		if i == 7:
			player = 1
			new_rect.left = 525
		else:
			player = 2

	new_rect.top  += 100
	new_rect.left += 100

	new_hole = Hole(new_rect, player, standard)

	if standard:
		new_hole.beads.append(Bead())
		new_hole.beads.append(Bead())
		new_hole.beads.append(Bead())
		new_hole.beads.append(Bead())
		new_hole.bead_count = 4

		new_hole.draw_beads(screen)

	all_holes.append(new_hole)


pygame.display.flip()



while True:

	for event in pygame.event.get():
		if event.type == QUIT:
			exit(0)
		elif event.type == MOUSEBUTTONDOWN:
			for i in xrange(0,14):
				if all_holes[i].is_clicked(current_player):
					make_move(i)
					break
				
