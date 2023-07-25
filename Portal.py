import pygame 
from settings import *
from support import import_folder
from YesNoInputBox import YesNoInputBox  
from LLM import function_call_Grant_Portal_Acces
class Portal(pygame.sprite.Sprite):
	def __init__(self,pos,groups,obstacle_sprites, name):
		super().__init__(groups)
		self.image =  pygame.image.load(f'graphics/Portal/idle/Portal_100x100px1.png').convert_alpha()
		self.rect = self.image.get_rect(topleft=pos)
		self.hitbox = self.image.get_rect(topleft=pos).inflate(-30, -30)
		self.frame_index = 0
		self.animation_speed = 100
		self.last_update = pygame.time.get_ticks()  # time when the frame was last updated
		self.is_interacting=False
		self.import_npc_assets()
		self.status = 'idle'
		self.dialog=YesNoInputBox(100, 100, 200, 100, 'Do you want to proceed?',self)
		
  
	def animate(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > self.animation_speed:
			self.last_update = now
			self.frame_index = (self.frame_index + 1) % len(self.animations[self.status])

			
			self.image = self.animations[self.status][int(self.frame_index)]
			self.rect = self.image.get_rect(center = self.hitbox.center)
	def interact(self,player,level,event=None):
		# Now you can access the name of the NPC in your interactions
		print('LEVEL',level.level)
		self.level=level
		self.player=player
		player.can_move=False
		self.isinteracting=True
		player.portal_interracting=True
		print(f"Interaction with portal to level 1!")
		## start dialog box here
		
		self.dialog==YesNoInputBox(100, 100, 200, 100, 'Do you want to proceed?',self,player)
		self.dialog.is_visible = True # Dialog becomes visible when interaction happens
  
	def increase_level(self):
		if self.level.level==0:
			self.level.change_map()
		else :
			#check portal completion
			LLM_answer=function_call_Grant_Portal_Acces(self.level.logs_path, self.level.level_objective)
			print("LLM_answer",LLM_answer)
			answer=LLM_answer['acces']
			if answer=="Yes":
				self.level.change_map()
			else:
				pass
		
				


	def import_npc_assets(self):
		character_path = f'graphics/Portal/'
		self.animations = {'idle': [],
		}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)

	def update(self):
		if self.is_interacting:
			self.interact()
		
		self.animate()
		if self.dialog.is_visible:
			self.dialog.draw()
			self.dialog.update(self.player)
