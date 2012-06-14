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

import sys
import os


progname = sys.argv[0]
progdir = os.path.dirname(progname)
sys.path.append(os.path.join(progdir,'data','popup_menu_data','gamelib'))

from popup_menu import NonBlockingPopupMenu

#stores the game state
class Game(object):
	def __init__(self):
		
		self.current_player = 1
		self.game_over = False
		self.winner = 0

		self.player_hands = [Hole(pygame.Rect(500,300,75,100), 1, True, 0), Hole(pygame.Rect(125, 0, 75, 100), 1, True, 0)]
		self.all_holes = []

		for i in xrange(0,14):
			if i == 0 or i == 7:
				standard = False

				new_rect = pygame.Rect(0,0,75,200)
		
				if i == 7:
					player = 1
					new_rect.left = 525
				else:
					player = 2

			else:
				standard = True

				new_rect = pygame.Rect(0,0,75,100)
				if i < 7:
					player = 1
					new_rect.top = 100

				if i > 7:
					player = 2
					i -= 14
					i *= -1

				new_rect.left = i*75

			new_rect.top  += 100
			new_rect.left += 100

			new_hole = Hole(new_rect, player, standard, 4 if standard else 0)
			self.all_holes.append(new_hole)

	def switch_players(self):
		self.current_player ^= 3

	def state(self):

		bead_list = [(i,bead) for (i,hole) in enumerate(self.all_holes) for bead in hole.beads]
		game_state = [self.current_player, self.game_over, self.winner, bead_list]
		
		return game_state

	def reset(self, game_state=None):

		#initialize a new game
		if not game_state:
			self.current_player = 1
			self.game_over = False
			self.winner = 0

			bead_list = [bead for hole in self.all_holes for bead in hole.beads]

			for (i,hole) in enumerate(self.all_holes):
				if i == 0 or i == 7:
					hole.beads = []
					hole.bead_count = 0
				else:
					hole.beads = []

					for i in xrange(4):
						hole.beads.append(bead_list.pop())

					hole.bead_count = 4
		else:
			self.current_player = game_state[0]
			self.game_over = game_state[1]
			self.winner = game_state[2]

			bead_list = game_state[3]

			for hole in self.all_holes:
				hole.beads = []
				hole.bead_count = 0

			for (i,bead) in bead_list:
				self.all_holes[i].beads.append(bead)
				self.all_holes[i].bead_count += 1

	def move(self, index):

		player_hand = self.player_hands[self.current_player-1]

		c = len(self.all_holes)
		i = index

		current_hole = self.all_holes[i]

		beads_to_move = current_hole.beads

		player_hand.bead_count = current_hole.bead_count
		player_hand.beads = []

		current_hole.beads =  []
		current_hole.bead_count = 0

		bead_new_location = []

		for bead in beads_to_move:
			i += 1
			i %= c
			
			player_hand.beads.append(bead)

			if self.all_holes[i].standard or self.all_holes[i].player == self.current_player:
				bead_new_location.append(i)
			else:
				i +=1
				i %= c
				bead_new_location.append(i)

		return self.all_holes[i].standard, bead_new_location

#handles displaying the game
class GameRenderer(object):

	def __init__(self):

		pygame.init()

		self.screen = pygame.display.set_mode((800,400))
		pygame.display.set_caption("Kalah")

		#Creating the background surface
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()

		self.background.fill((255,255,255))

		board = pygame.image.load(os.path.join('data', 'board.png'))
		board = board.convert()

		colorkey = board.get_at((0,0))
		board.set_colorkey(colorkey, RLEACCEL)

		self.background.blit(board, (100,100))
		self.screen.blit(self.background, (0,0))

		#Creating the text layer
		if pygame.font:
			self.label_font = pygame.font.Font(None, 36)
			text = self.label_font.render("Player 1's Turn", 1, (0,0,0))
			text_pos = text.get_rect()
			text_pos.centerx = self.screen.get_rect().centerx
			self.screen.blit(text, text_pos)

		pygame.display.flip()

	def render(self, game, menu=None, display=False):
		self.screen.blit(self.background, (0,0))

		for hole in game.all_holes:		
			hole.draw_beads(self.screen)
	
		for hole in game.player_hands:
			hole.draw_beads(self.screen)
	
		if game.game_over:
			if not game.winner:	
				text = self.label_font.render("It's A Tie!", 1, (0,0,0))
			else:
				text = self.label_font.render("Player "+str(game.winner)+" Wins!", 1, (0,0,0))
		else:
			text = self.label_font.render("Player "+str(game.current_player)+"'s Turn", 1, (0,0,0))

		text_pos = text.get_rect()
		text_pos.centerx = self.screen.get_rect().centerx 
		self.screen.blit(text,text_pos)

		if menu:
			menu.draw()
		
		if display:
			pygame.display.flip()

	def tutorial_render(self, game):
		self.screen.blit(self.background, (0,0))

		for hole in game.all_holes:		
			hole.draw_beads(self.screen)
	
		for hole in game.player_hands:
			hole.draw_beads(self.screen)

	def display_tutorial_text(self, message, font = None, vertical=385, horizontal=0):

		if not font:
			font = self.label_font

		y_value = font.render(message, 1, (0,0,0)).get_rect().centery
		vertical = vertical - 2*y_value

		self.display_text(message, font, vertical, horizontal)

	#used by run tutorial, contains all but the first scene of the tutorial (
	#first scene is skipped becuase it needs to appear before first continue-click
	def display_tutorial(self, game, gameController):
		self.display_tutorial_text("Player 1's pits")
		pygame.draw.lines(self.screen, (0,0,0), False, [(190,280),(200,310),(600,310),(610,280)],5)
		yield True

		self.display_tutorial_text("Player 2's pits",self.label_font,75)
		pygame.draw.lines(self.screen, (0,0,0), False, [(190,120),(200,90),(600,90),(610,120)],5)
		yield True

		self.display_tutorial_text("Player 1's store",self.label_font,385,250)
		pygame.draw.lines(self.screen, (0,0,0), False, [(690,90),(710,100),(710,300),(690,310)],5)
		yield True
			
		self.display_tutorial_text("Player 2's store",self.label_font,385,-250)
		pygame.draw.lines(self.screen, (0,0,0), False, [(110,90),(90,100),(90,300),(110,310)],5)
		yield True
					
		self.display_tutorial_text("On a player's turn, they select on one of their pits and click.")
		pygame.draw.lines(self.screen, (0,0,0), False, [(518,340),(518,300),(528,310),(508,310),(518,300)],3)
		yield True
				
		gameController.make_move(5, game, self)
		yield True	
					
		self.display_tutorial_text("The beads are sown counterclockwise.")
		yield True	
					
		self.display_tutorial_text("The player with the most beads in their store", self.label_font, 345)
		self.display_tutorial_text("at the end of the game wins.")
		yield True

		self.display_tutorial_text("Now, it is the other player's turn.")
		yield True
					
		gameController.make_move(10, game, self)
		yield True
					
		self.display_tutorial_text("Whenever a player's last bead falls into their store,", self.label_font, 345)
		self.display_tutorial_text("they get another turn.")
		yield True
	
		gameController.make_move(9, game, self)
		yield True

		self.display_tutorial_text("This applies to their bonus turn as well.")
		yield True
					
		gameController.make_move(13, game, self)
		yield True

		self.display_tutorial_text("It is player 1's turn again.")
		yield True
					
		gameController.make_move(2, game, self)
		yield True
					
		gameController.make_move(5, game, self)
		yield True
					
		gameController.make_move(6, game, self)
		yield True

		self.display_tutorial_text("With planning, a player can move not just once; but...")
		yield True
					
		gameController.make_move(13, game, self)
		yield True

		self.display_tutorial_text("...again...")
		yield True
			
		gameController.make_move(8, game, self)
		yield True
					
		self.display_tutorial_text("...and again...")
		yield True

		gameController.make_move(13, game, self)
		yield True
					
		self.display_tutorial_text("...and again!")
		yield True
					
		gameController.make_move(12, game, self)
		yield True

		self.display_tutorial_text("The game ends when the current player cannot make a move.")
		yield True

		self.display_tutorial_text("A player's beads are not sown into the opponent's store.")
		yield True

		self.display_tutorial_text("Let's see an example.")

		all_beads = []

		for hole in game.all_holes:
			for bead in hole.beads:
				all_beads.append(bead)
				
			hole.beads = []
			hole.bead_count = 0

		bead_list = []

		for i in xrange(8):
			bead_list.append([6,all_beads.pop()])

		game.reset([1,False,0, bead_list])
		yield True
					
		self.display_tutorial_text("Let's see an example.")
		yield True
					
		gameController.make_move(6, game, self)
		yield True	
					
		self.display_tutorial_text("And that's all there is to it!")
		yield True
					
		self.display_tutorial_text("You can now return to your game.")
		yield True
					
		return

	def display_text(self, message, font=None, vertical=0, horizontal=0):

			if not font:
				font = self.label_font


			step_text = font.render(message, 1, (0,0,0))

			step_text_pos = step_text.get_rect()
			step_text_pos.centerx = self.screen.get_rect().centerx + horizontal
			step_text_pos.centery = step_text_pos.centery + vertical

			self.screen.blit(step_text, step_text_pos)
	
	def move_bead_to(self, game, bead, dest):

		while bead.pos[0] != dest[0] or bead.pos[1] != dest[1]:
			self.render(game)

			if bead.pos[0] == dest[0]:
				i = 1
			elif bead.pos[1] == dest[1]:
				i = 0
			else:
				i = random.randint(0,1)

			j = (i+1)%2
			
			if bead.pos[i] > dest[i]:
				if i < j:
					bead.pos = [bead.pos[i]-1, bead.pos[j]]
				else:
					bead.pos = [bead.pos[j], bead.pos[i]-1]
			else:
				if i < j:
					bead.pos = [bead.pos[i]+1, bead.pos[j]]
				else:
					bead.pos = [bead.pos[j], bead.pos[i]+1]

			bead.draw(self.screen)
			pygame.display.flip()
			

class GameController(object):

	def __init__(self):
		menu_data = (
			'Options',
			'New game',
			'How to play',
			'Quit'
		)

		self.menu = NonBlockingPopupMenu(menu_data)

	def handle_menu(self, event, game, gameRenderer):

		if event.name is None:
			self.menu.hide()
		elif event.name == 'Options':
			if event.text == 'Quit':
				exit(0)
			elif event.text == 'How to play':
				self.menu.hide()

				game_state = game.state()
				game.reset()

				self.run_tutorial(game, gameRenderer)

				game.reset(game_state)
			elif event.text == 'New game':
				self.menu.hide()
				game.reset()
		
	def make_move(self, hole_moved_indice, game, gameRenderer):

		(switch_players, bead_new_location) = game.move(hole_moved_indice)

		player_hand = game.player_hands[game.current_player-1]

		if switch_players:
			game.switch_players()


		moving_bead = None
		destination = None
		dest_hole = None

		while player_hand.beads:
			moving_bead = player_hand.beads.pop()
			player_hand.bead_count -= 1
			index = bead_new_location.pop(0)
			dest_hole = game.all_holes[index]
			destination = (dest_hole.rect.centerx, dest_hole.rect.centery)
			moving_bead.pos = [player_hand.rect.centerx, player_hand.rect.centery]

			gameRenderer.move_bead_to(game, moving_bead, destination)

			dest_hole.beads.append(moving_bead)
			dest_hole.bead_count += 1

		game.game_over = True

		for (i, hole) in enumerate(game.all_holes):
			if hole.standard:
				if hole.player == game.current_player and hole.bead_count > 0:
					game.game_over = False	
			else:
				if hole.player == 1:
					player_1_score = hole.bead_count
				else:
					player_2_score = hole.bead_count

		if game.game_over:
			if   player_1_score > player_2_score:
				game.winner = 1
			elif player_2_score > player_1_score:
				game.winner = 2
			else:
				game.winner = 0

		gameRenderer.render(game, None, True)


	def run_tutorial(self, game, gameRenderer):

		gameRenderer.tutorial_render(game)
	
		title_font = pygame.font.Font(None, 24)
		title_text = "How to Play Kalah - (click to continue, escape to return to your game)"

		gameRenderer.display_text(title_text, title_font)
		gameRenderer.display_tutorial_text("Each player has six pits and one store")

		pygame.display.flip()

		tutorial_screens = gameRenderer.display_tutorial(game, self)

		while True:
			try:
				for event in pygame.event.get():
					if event.type   == KEYDOWN:
						if event.key == pygame.K_ESCAPE:
							return
					elif event.type == QUIT:
						exit(0)
					elif event.type == MOUSEBUTTONDOWN:
					
						gameRenderer.tutorial_render(game)
						gameRenderer.display_text(title_text, title_font)
				
						tutorial_screens.next()	
				
						pygame.display.flip()
			#catching the end of the generative function display_tutorial
			except StopIteration:
				return


	def run(self, gameRenderer, game):
		#used to indicate when a MOUSEBUTTONUP event should not lead to displaying the menu
		move_just_made = False

		while True:

			gameRenderer.render(game, self.menu, True)

			for event in self.menu.handle_events(pygame.event.get()):

				if event.type == MOUSEBUTTONDOWN:
					move_just_made = False

					for i in xrange(0,14):
						if game.all_holes[i].is_clicked(game.current_player):
							self.make_move(i, game, gameRenderer)
							break

					pos = pygame.mouse.get_pos()

					x = pos[0]
					y = pos[1]

					#We do not want the menu to appear when a click occurs inside the board
					if (x >= 100 and x <= 700) and (y >= 100 and y <= 300):
						move_just_made = True
	
				elif event.type == QUIT:
					exit(0)
		        	elif event.type == MOUSEBUTTONUP and not move_just_made:
        			    	self.menu.show()
		        	elif event.type == USEREVENT:
            				if event.code == 'MENU':
                				self.handle_menu(event, game, gameRenderer)


class Bead:

	def __init__(self):
		self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
		self. pos = None

	def draw(self, surface=None):

		pygame.draw.circle(surface, (0,0,0), self.pos, 10)
		pygame.draw.circle(surface, self.color, self.pos, 9)
		pygame.draw.circle(surface, (255,255,255), (self.pos[0]+2, self.pos[1]+2), 1)


class Hole:

	def __init__(self, rect, player, standard, nbeads):
		self.rect = rect
		self.beads = [Bead() for i in xrange(nbeads)]
		self.bead_count = nbeads
		self.player = player
		self.standard = standard


	def draw_beads(self, surface):
		x = self.rect.centerx
		y = self.rect.centery

		standard = self.standard
		beads = self.beads

		if self.bead_count == 0:
			return False
		elif self.bead_count == 1:
			beads[0].pos = (x, y)

			beads[0].draw(surface)
		elif self.bead_count == 2:	
			beads[0].pos = (x, y+20)
			beads[1].pos = (x, y-20)

			beads[0].draw(surface)
			beads[1].draw(surface)
		elif self.bead_count == 3:
			if standard:
				beads[0].pos = (x, y+25)
				beads[1].pos = (x, y-25)
				beads[2].pos = (x, y)
			else:
				beads[0].pos = (x, y+30)
				beads[1].pos = (x, y-30)
				beads[2].pos = (x, y)

			beads[0].draw(surface)
			beads[1].draw(surface)
			beads[2].draw(surface)
		elif self.bead_count == 4:
			if standard:
				beads[0].pos = (x+12, y+12)
				beads[1].pos = (x+12, y-12)
				beads[2].pos = (x-12, y+12)
				beads[3].pos = (x-12, y-12)
			else:
				beads[0].pos = (x, y+45)
				beads[1].pos = (x, y-45)
				beads[2].pos = (x, y+15)
				beads[3].pos = (x, y-15)

			beads[0].draw(surface)
			beads[1].draw(surface)
			beads[2].draw(surface)
			beads[3].draw(surface)
		elif self.bead_count == 5:
			if standard:
				beads[0].pos = (x+15, y+15)
				beads[1].pos = (x+15, y-15)
				beads[2].pos = (x-15, y+15)
				beads[3].pos = (x-15, y-15)
				beads[4].pos = (x, y)
			else:
				beads[0].pos = (x, y+60)
				beads[1].pos = (x, y-60)
				beads[2].pos = (x, y+30)
				beads[3].pos = (x, y-30)
				beads[4].pos = (x, y)

			beads[0].draw(surface)
			beads[1].draw(surface)
			beads[2].draw(surface)
			beads[3].draw(surface)
			beads[4].draw(surface)
		else:
			for bead in beads:
				bead.pos = None

			beads[0].pos = (x, y-20)
			beads[0].draw(surface)

			if pygame.font:
				font = pygame.font.Font(None, 24)
				text = font.render(str(self.bead_count), 1, (0,0,0))
				text_pos = text.get_rect()
				text_pos.centerx = x
				text_pos.centery = y+20
				surface.blit(text, text_pos)

		return True


	def is_clicked(self, player):
		if self.standard and self.player == player and self.bead_count > 0:
			pos = pygame.mouse.get_pos()
			if self.rect.collidepoint(pos):
				return True

		return False

if __name__ == "__main__":

	game = Game()
	renderer = GameRenderer()
	controller = GameController()

	controller.run(renderer,game)
			
				
