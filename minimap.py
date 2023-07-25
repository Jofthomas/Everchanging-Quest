import csv
from PIL import Image
import random
import os
import glob

from support import import_folder
import pygame

class MiniMap:
	def __init__(self, map_image, display_surface, position, size):
		# map_image is already an Image object, no need to open it again.
		# Load the image using PIL and scale it to the desired size
		self.image = map_image
		self.image.thumbnail(size) # this keeps aspect ratio, for forced scale use resize()

		# Convert PIL Image to Pygame Surface
		self.image = pygame.image.fromstring(self.image.tobytes(), self.image.size, self.image.mode)

		self.display_surface = display_surface
		self.position = position  # A tuple (x, y)
		self.show_map = False
		#animation
		self.animation_loop=1
		self.import_player_assets()
		self.frame_index = 0
		self.animation_speed = 0.30
		self.status = 'Open'
		self.openning=False
		self.opening_finished=False
		self.finished_closed=False

	def update(self):
	
		if self.show_map:
			# increment frame index
			self.animation_finished=False
			animation = self.animations[self.status]
			self.frame_index += self.animation_speed
			

			# if frame_index is greater than the total frames
			# set it to the last frame index
			if self.frame_index >= len(animation):
				self.frame_index = len(animation) - 1
				
				if self.status=="Close":
					self.animation_finished=True
					self.show_map=False
					
					
				if self.status=="Open":
					self.open_finished=True
					self.status="Static"
				
			
		
			self.anim_image = animation[int(self.frame_index)]

			# compute the new position
			shift_value = 70  # replace with the value you want
		
			new_position = (self.position[0] - shift_value, self.position[1]-30)

			# display the image on the surface at the new position
			self.display_surface.blit(self.anim_image, new_position)

			self.display_surface.blit(self.image, self.position)
			
	
	def import_player_assets(self):
		character_path = 'graphics/UI/Map/'
		self.animations = {'Open': [],'Close': [],'Static': [],
			}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)
			print(len(self.animations[animation]))
		
	def get_status(self):
		
		return self.status
	def set_status(self,status):
		
		self.status = status
		self.frame_index=0
		

def create_image_from_csv(csv_file, output_file):
	# Specific image for '1'
	one_image = Image.open('map/graphics_1/Collisions/1.png')

	# Gathering all images in the specified folder
	random_images = []
	for filename in glob.glob('map/graphics_1/Floor/*.png'): 
		im=Image.open(filename)
		random_images.append(im)
	with open(csv_file, 'r') as file:
		reader = csv.reader(file)
		data = list(reader)

	# assuming all rows are of the same length
	image_width = len(data[0]) * one_image.width
	image_height = len(data) * one_image.height

	output_image = Image.new('RGBA', (image_width, image_height))

	for i, row in enumerate(data):
		for j, cell in enumerate(row):
			if cell == '1':
				output_image.paste(one_image, (j * one_image.width, i * one_image.height))
			else:
				output_image.paste(random.choice(random_images), (j * one_image.width, i * one_image.height))

	output_image.save(output_file)
	return output_image
