import pygame
from settings import * 
import time
class UI:
	def __init__(self):
		
		# general 
		self.display_surface = pygame.display.get_surface()
		self.font = pygame.font.Font(UI_FONT,UI_FONT_SIZE)

		# bar setup 
		self.health_bar_rect = pygame.Rect(50,20,HEALTH_BAR_WIDTH,BAR_HEIGHT)
		self.energy_bar_rect = pygame.Rect(50,34,ENERGY_BAR_WIDTH,BAR_HEIGHT)
		self.player_image = pygame.image.load('graphics/UI/Side Portrait Small.png')
		self.timer = Timer()
		# convert magic dictionary
		self.magic_graphics = []
		for magic in magic_data.values():
			magic = pygame.image.load(magic['graphic']).convert_alpha()
			self.magic_graphics.append(magic)
	
	def show_bar(self,current,max_amount,bg_rect,color):
		# draw bg 
		pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect)

		# converting stat to pixel
		ratio = current / max_amount
		current_width = bg_rect.width * ratio
		current_rect = bg_rect.copy()
		current_rect.width = current_width

		# drawing the bar
		pygame.draw.rect(self.display_surface,color,current_rect)
		pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,2)
	
	def show_exp(self,exp):
		text_surf = self.font.render(str(int(exp)),False,TEXT_COLOR)
		x = self.display_surface.get_size()[0] - 20
		y = self.display_surface.get_size()[1] - 20
		text_rect = text_surf.get_rect(bottomright = (x,y))

		pygame.draw.rect(self.display_surface,UI_BG_COLOR,text_rect.inflate(10,10))
		self.display_surface.blit(text_surf,text_rect)
		pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,text_rect.inflate(10,10),3)
  
	def show_Timer(self):
		elapsed_time = self.timer.get_elapsed_time()
		text_surf = self.font.render("Time : " + str(int(elapsed_time)), False, TEXT_COLOR)
		x = WIDTH / 2
		y = 20
		text_rect = text_surf.get_rect(center=(x, y))

		pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(10, 10))
		self.display_surface.blit(text_surf, text_rect)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(10, 10), 3)


	def magic_overlay(self,magic_index,has_switched):
		bg_rect = self.selection_box(10,520,has_switched)
		magic_surf = self.magic_graphics[magic_index]
		magic_rect = magic_surf.get_rect(center = bg_rect.center)

		self.display_surface.blit(magic_surf,magic_rect)
  
	def selection_box(self,left,top, has_switched):
		bg_rect = pygame.Rect(left,top,ITEM_BOX_SIZE,ITEM_BOX_SIZE)
		pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect)
		if has_switched:
			pygame.draw.rect(self.display_surface,UI_BORDER_COLOR_ACTIVE,bg_rect,3)
		else:
			pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,3)
		return bg_rect
	def display(self,player):
     	 # draw player image
		self.display_surface.blit(self.player_image, (10, 10))
		self.show_bar(player.health,player.stats['health'],self.health_bar_rect,HEALTH_COLOR)
		self.show_bar(player.energy,player.stats['energy'],self.energy_bar_rect,ENERGY_COLOR)

		self.show_exp(player.exp)
		self.show_Timer()
		self.magic_overlay(player.magic_index,not player.can_switch_magic)




class Timer:
    def __init__(self):
        self._start_time = None
        self._elapsed_time = 0
        self._paused = False

    def start(self):
        if self._start_time is not None:
            raise RuntimeError('Timer is already running')
        self._start_time = time.time()

    def stop(self):
        if self._start_time is None:
            raise RuntimeError('Timer is not running')
        stop_time = time.time()
        elapsed_time = stop_time - self._start_time
        self._start_time = None
        self._elapsed_time = 0
        return elapsed_time

    def pause(self):
        if self._start_time is None:
            raise RuntimeError('Timer is not running')
        self._elapsed_time += time.time() - self._start_time
        self._start_time = None
        self._paused = True

    def resume(self):
        if not self._paused:
            raise RuntimeError('Timer is not paused')
        self._start_time = time.time()
        self._paused = False

    def get_elapsed_time(self):
        if self._start_time is not None:
            return self._elapsed_time + time.time() - self._start_time
        return self._elapsed_time

