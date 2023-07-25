import pygame
from settings import *
from entity import Entity
from support import *
from math import sin
import json
from Items import Item
from LLM import function_call_create_item
import random
import threading
import time 
class Chest(pygame.sprite.Sprite):
	def __init__(self,pos,groups,obstacle_sprites, name,log_path):

		# general setup
		super().__init__(groups)
		self.sprite_type = 'enemy'

		# graphics setup
		self.import_graphics()
		self.status = 'Idle'
		self.frame_index=0
		self.image = self.animations[self.status][self.frame_index]
		
		self.animation_speed = 0.30
		# movement
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,-15)
		self.obstacle_sprites = obstacle_sprites

	
		
		self.is_open = False
		self.open_count=0
		

		# sounds
		self.open_sound = pygame.mixer.Sound('audio/chest.mp3')
	
		self.open_sound.set_volume(0.4)
		#logs
		self.log_path=log_path
	

	def import_graphics(self):
		self.animations = {'Idle':[],'Open':[]}
		main_path = f'graphics/objects/Chest/'
		for animation in self.animations.keys():
			self.animations[animation] = import_folder(main_path + animation)


	def animate(self):
		animation = self.animations[self.status]
		
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = len(animation) -1

		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center = self.hitbox.center)



	def open(self, player, level, surface):
		if not self.is_open and self.open_count <= 1:
			self.open_count += 1
			self.status = 'Open'
			self.is_open = True
			self.open_sound.play()
			
			# Create a random number between 'level' and 'level+1'
			new_variable = random.uniform(level, level + 1)
			
			# Create 'rate' which is 'new_variable' divided by 5
			rate = f"{new_variable}/5"
			
			# Start new thread for the function call
			thread = threading.Thread(target=self.create_and_add_item, args=(rate, player, surface))
			thread.start()

	def create_and_add_item(self, rate, player, surface):
		item_json = function_call_create_item(rate)
		print(item_json)
		
		# Parsing values from the json
		name = item_json['name'] # assuming you want to give it a name
		description = item_json['description']
		item_type = item_json['item_type']
		health_bonus = int(item_json['health_bonus'])
		enegy_bonus = int(item_json['enegy_bonus'])
		magic_bonus = int(item_json['magic_bonus'])
		strength_bonus = int(item_json['strength_bonus'])
		speed_bonus = float(item_json['speed_bonus'])
		try:
			# Creating an item object
			item_object = self.create_Item_json(name, description, item_type, health_bonus, enegy_bonus, magic_bonus, strength_bonus, speed_bonus)

			# Adding the item to player's inventory
			player.add_to_inventory(item_object)
			print(self.log_path)
			if self.log_path is not None:
				self.log_self(item_object)
			
		except :
			print("Oups, no item created")

	def show_notification(self, surface, message, x, y):
		# This function should display the notification on the given coordinates
		font = pygame.font.Font(None, 36)  # Use a default font, size 36
		text_surface = font.render(message, True, (255, 255, 255))  # Create a white text surface
		surface.blit(text_surface, (x, y))  # Draw the text on the given coordinates

	def clear_notification(self, surface, x, y):
		# This function should clear the notification from the given coordinates
		rect = pygame.Rect(x, y, 200, 50)  # Create a rectangle over the notification
		surface.fill((0, 0, 0), rect)  # Fill the rectangle with black color
	def update(self):
		self.animate()
	def enemy_update(self,player):
		self.animate()
	
	def create_Item_json(self,name,description, item_type, health_bonus,enegy_bonus,magic_bonus, strength_bonus, speed_bonus):

		# Create a dictionary with character properties
		if item_type=='weapon':
			sprite="graphics/items/sword_of_valor.png"
		if item_type=='torso':
			sprite="graphics/items/torso.png"
		if item_type=='legs':
			sprite="graphics/items/pants.png"
		if item_type=='boots':
			sprite="graphics/items/boots.png"
		if item_type=='headset':
			sprite="graphics/items/headset.png"
		if item_type=='jewel':
			sprite="graphics/items/jewel.png"
		item=Item(name,description, item_type, sprite, health_bonus, enegy_bonus, strength_bonus, magic_bonus, speed_bonus)

		return item
	def log_self(self, item):
		with open(self.log_path, 'a') as log_file:
			log_file.write(f"player opened chest and obtained {item.name} 777 \n")
