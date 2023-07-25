import pygame
import pytmx
from settings import *
from player import Player
from npc import NPC
from enemy import Enemy
from debug import debug
from support import *
from weapon import Weapon
from pytmx.util_pygame import load_pygame
from Portal import Portal
from ui import UI
from maps_creation import generate_game_maps,generate_dungeon,draw_dungeon
import time 
from random import choice, randint
import random
from LLM import place_LLM_tiles,Create_story_LLM,Create_Level_objective_LLM
from distances import Point,find_closest_walkable, dijkstra_distance,mark_positions,place_characters,find_closest_room_center,find_biggest_room_center
from minimap import MiniMap,create_image_from_csv
from threading import Thread
from particles import AnimationPlayer
from magic import MagicPlayer
from GameOver import game_over_screen
from GameFinished import game_won_screen
from upgrade import Upgrade
from Objective import TextObject
from My_timer import Timer
from Chest import Chest
class Tile(pygame.sprite.Sprite):
	def __init__(self, pos, image_surface, groups, layer_name):
		super().__init__(groups)
		self.image = image_surface
		self.rect = self.image.get_rect(topleft=pos)
		self.hitbox = self.rect.inflate(0, -10)
		self.layer_name = layer_name
		

class Level:
	def __init__(self,music):
		# get the display surface 
		self.display_surface = pygame.display.get_surface()
		self.game_paused = False
		self.npcs = []
		self.portals = []
		self.chests = []
		self.level=0
		self.style=1
		self.font = pygame.font.Font(None, 50)
		#logs
		self.logs_path=None
		#timer
		self.timer_started=False
		# sprite group setup
		self.visible_sprites = YSortCameraGroup(self)
		self.obstacle_sprites = pygame.sprite.Group()
		self.attackable_sprites = pygame.sprite.Group()
		self.attack_sprites = pygame.sprite.Group()
  
		self.ui =UI()
		self.ui.timer.start()
		self.player = Player((0, 0), [self.visible_sprites], self.obstacle_sprites,self.create_attack,
                             self.destroy_attack, self.create_magic)
		self.player.set_position((200, 200))
		# sprite setup
		self.create_map()
		self.player_placed=False
		self.height=300
		self.width=300
		self.min_room_size=30
		self.min_room_ratio=0.5
		self.previous_level=0
		self.current_attack = None
		# Threading
		self.loading_finished = False
		self.loading_progress = 10
		self.loading_bar_width = 8
		self.loading_bar = pygame.image.load("graphics/UI/loading_bar/Loading Bar.png")
		self.loading_bar_rect = self.loading_bar.get_rect(midleft=(151, 300))
		#minimap
		self.minimap=None
		# Loading BG
		self.loading_bg = pygame.image.load("graphics/UI/loading_bar/Loading Bar Background.png")
		self.loading_bg_rect = self.loading_bg.get_rect(center=(375, 300))
		# Finished text
		self.finished=self.font.render("Loading ...", True, "black")

		self.finished_rect = self.finished.get_rect(center=(375, 450))
		# particles
		self.animation_player = AnimationPlayer()
		self.magic_player = MagicPlayer(self.animation_player)
		self.game_over = False
		self.upgrade = Upgrade(self.player,self)
		#sound
		self.main_sound =music
		self.dungeon_sound = pygame.mixer.Sound('audio/xDeviruchi - Mysterious Dungeon.wav')
		self.dungeon_sound.set_volume(0.1)	
		self.death_sound= pygame.mixer.Sound('audio/mixkit-game-over-trombone-1940.wav')
		self.death_sound.set_volume(0.3)	
		self.win_sound= pygame.mixer.Sound('audio/Victory.mp3')
		self.win_sound.set_volume(0.3)	
		
		# story
		self.level_story=None
		#objective
		self.level_objective=None
		self.already_set=False
		self.max_level=1
		self.event=None
	def update_info_text(self,text):
		self.finished=self.font.render(text, True, "black")
		self.finished_rect = self.finished.get_rect(center=(375, 450))
		self.display_surface.blit(self.finished, self.finished_rect)
	def damage_player(self,amount,attack_type):
		if self.player.vulnerable:
			self.player.health -= amount
			self.player.vulnerable = False
			self.player.hurt_time = pygame.time.get_ticks()
		if self.player.health<=0:
			self.game_over=True

	def trigger_death_particles(self,pos,particle_type):

		self.animation_player.create_particles(particle_type,pos,self.visible_sprites)

	def add_exp(self,amount):

		self.player.exp += amount
  
	def create_attack(self):
		
		self.current_attack = Weapon(self.player,[self.visible_sprites,self.attack_sprites])

	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None
  
	def create_magic(self,style,strength,cost):
		if style == 'heal':
			self.magic_player.heal(self.player,strength,cost,[self.visible_sprites])

		if style == 'flame':
			self.magic_player.flame(self.player,cost,[self.visible_sprites,self.attack_sprites])
  
	def player_attack_logic(self):
		if self.attack_sprites:
			for attack_sprite in self.attack_sprites:
				collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
				if collision_sprites:
					for target_sprite in collision_sprites:
						target_sprite.get_damage(self.player,attack_sprite.sprite_type)
      
	def toggle_menu(self):
		if not self.game_paused:
			self.upgrade.set_status('Open')
			self.game_paused = not self.game_paused
		else:
			self.upgrade.set_status('Close')
			
				




	def run(self, event):
		# update and draw the game
		self.event=event
		if self.game_over:
			self.dungeon_sound.stop()
			game_over_screen(self.display_surface,event,self.death_sound)
			
			return
		
		if self.level == 0:
			self.visible_sprites.custom_draw(self.player)
			
			self.ui.display(self.player)
			if self.objective_text:
				self.objective_text.update()
				self.objective_text.draw(self.display_surface)
				if self.objective_text.animation_finished and not self.already_set:
					self.already_set=True
					self.player.can_move = True
				

			if self.game_paused:
				self.upgrade.display()
				self.upgrade.update(event)
				if self.upgrade.animation_finished:
					self.game_paused = not self.game_paused
			else:
				self.player.update(event)
				self.visible_sprites.update()
				keys = pygame.key.get_pressed()
				if keys[pygame.K_RETURN]:
					for npc in self.npcs:
						if pygame.sprite.collide_rect(self.player, npc):
							npc.interact(self.player, event)  # Do whatever interaction you want to do here.
					for port in self.portals:
						if pygame.sprite.collide_rect(self.player, port):
							if not self.player.portal_interracting:
								self.player.portal_interracting=True
								port.interact(self.player, self, event)  # Do whatever interaction you want to do here.
					for chest in self.chests:
						if pygame.sprite.collide_rect(self.player, chest):
								
								chest.open(self.player,self.level,self.display_surface)
				self.visible_sprites.enemy_update(self.player)
				self.player_attack_logic()
		else:
			
			if not self.loading_finished:
				self.display_surface.fill("#FEFDF0")

				self.loading_bar_width = self.loading_progress / 100 * 448  # assuming 100 is the max progress
				
				
				self.loading_bar = pygame.transform.scale(self.loading_bar, (int(self.loading_bar_width), 80))
				

				self.loading_bar_rect = self.loading_bar.get_rect(midleft=(151, 300))
				self.display_surface.blit(self.loading_bar, self.loading_bar_rect)
				self.display_surface.blit(self.loading_bg, self.loading_bg_rect)
				self.display_surface.blit(self.finished, self.finished_rect)

				pygame.display.update()

				
			else:
				self.main_sound.stop()
				self.visible_sprites.custom_draw(self.player)
				self.ui.display(self.player)
				if self.game_paused:
					self.upgrade.display()
					self.upgrade.update(event)
					if self.upgrade.animation_finished:
						self.game_paused = not self.game_paused
				else:
					self.player.update(event)
					self.visible_sprites.update()
					if self.objective_text:
						self.objective_text.update()
						self.objective_text.draw(self.display_surface)
						if self.objective_text.animation_finished:
							if  not self.already_set:
								self.already_set=True
								self.player.can_move = True
							self.minimap.show_map=True
							self.minimap.update()
							self.visible_sprites.enemy_update(self.player)
							self.player_attack_logic()
						else:
							self.player.can_move = False
					keys = pygame.key.get_pressed()
					if keys[pygame.K_RETURN]:
						for npc in self.npcs:
							if pygame.sprite.collide_rect(self.player, npc):
								npc.interact(self.player, event)  # Do whatever interaction you want to do here.
						for port in self.portals:
							if pygame.sprite.collide_rect(self.player, port):
								
								if not self.player.portal_interracting:
									self.player.portal_interracting=True
									port.interact(self.player, self, event)  # Do whatever interaction you want to do here.
						for chest in self.chests:
							if pygame.sprite.collide_rect(self.player, chest):
									
									chest.open(self.player,self.level,self.display_surface)

			
        
		
	def create_map(self):
		
		print("Loading level :", self.level)
		self.already_set=False
		self.player.can_move=False
		# load the tmx map
		self.player_placed=False
		self.visible_sprites.set_camera_level(self.level,0)
		if self.level==0:
		
			tmx_data = load_pygame('map/Town.tmx')
			# iterate over the layers of the tmx map 
			for layer in tmx_data.layers:
				if isinstance(layer, pytmx.TiledTileLayer):  # Check if this is a tile layer
					if layer.name == 'NPC':  
						
						pass
					else:
						for x, y, image in layer.tiles():
							if image:
								Tile((x * TILESIZE, y * TILESIZE), image, [self.visible_sprites], layer.name)
				elif isinstance(layer, pytmx.TiledObjectGroup):  # Check if this is an object layer
					if layer.name == 'colissions':
						for object in layer:
							# Assuming the object is a rectangle, create a new Tile at its position
							# You might need to adjust this if the objects in your layer are not rectangles or if you need to handle other types of shapes
							pos = (object.x, object.y)
							image = pygame.Surface((object.width, object.height))  # Create an empty Surface for the collision tile
							image.set_alpha(0)
							Tile(pos, image, [self.visible_sprites, self.obstacle_sprites],'colissions')
					if layer.name == 'interactions':
						for object in layer:
							# assuming each object in 'interactions' layer has a 'name' property 
							pos = (object.x, object.y)
							npc_name = object.properties.get('npc_name ')  # Extract the name property of the object
							print(npc_name)
							if npc_name:
								npc = NPC(pos, [self.visible_sprites], self.obstacle_sprites, npc_name) 
								self.npcs.append(npc) 
					if layer.name == 'Portal':
						for object in layer:
							# assuming each object in 'interactions' layer has a 'name' property 
							pos = (object.x, object.y)
							portal_name = object.properties.get('portal_name ')  # Extract the name property of the object
							print("Portal:",portal_name)
							portal = Portal(pos, [self.visible_sprites], self.obstacle_sprites, portal_name) 
							self.portals.append(portal) 
			self.player.reset_groups([self.visible_sprites])
			chest=Chest((880, 880),	[self.visible_sprites,self.obstacle_sprites],self.obstacle_sprites,'Interactions',self.logs_path)
			self.player.set_position((860, 880))
			
			self.chests.append(chest)
						# create text object
			my_timer = Timer(10000) # 10 seconds timer
			my_text = TextObject("This game is generating content from LLM. For more info visit this game's page.", None, (0, 0, 0), (100, 200), my_timer, "graphics/UI/Objective/7 Dialogue Box/Idle/1.png")
			self.timer=my_timer
			self.objective_text=my_text
			my_timer.obj = my_text
   
			my_timer.activate()
			if self.ui.timer:
				
		
				self.ui.timer.pause()
		else:
			self.loading_thread = Thread(target=self._create_map_async)
			self.loading_thread.start()

			
	def _create_map_async(self):
		print("Loading level :", self.level)
		self.main_sound.stop()
		
#generate_game_maps("map/", self.level, self.width, self.height)
		  # increase as appropriate
		wall_csv=f'map/Floor_{self.level}/map_{self.level}_Collisions.csv'
		self.update_info_text("Generating map")
		logs_path=generate_game_maps("map/",self.level,self.width, self.height)
		self.logs_path=logs_path
		self.loading_progress = 10  # increase as appropriate
		dungeon_tree = generate_dungeon(self.width, self.height,self.min_room_size,self.min_room_ratio)
		self.update_info_text("Map Generated")
		rooms=draw_dungeon(dungeon_tree,  wall_csv,3,self.width, self.height,self.min_room_size,self.min_room_ratio)
		new_rooms = []
		for rect in rooms:
			new_rect = pygame.Rect(rect.y, rect.x, rect.height, rect.width)
			new_rooms.append(new_rect)
		print("Rooms :",new_rooms )
		self.loading_progress = 40
		min_distance = self.width*1  # Minimum distance between player and boss
		file_path = f'map/Floor_{self.level}/map_{self.level}_Collisions.csv'
		self.update_info_text("Placing Hero ")
		player_position, boss_position = place_characters(file_path, min_distance)
		print('Boss before moving :', boss_position.x, boss_position.y)
		player_position=find_closest_room_center(player_position,new_rooms)
		self.update_info_text("Hero placed ")
		print('player :', player_position.x, player_position.y)
		self.update_info_text("Placing Boss ")
		boss_position=find_biggest_room_center(boss_position,new_rooms)
  
		print('Boss after moving :', boss_position.x, boss_position.y)
		# Mark the player's and boss's positions on the map
		mark_positions(player_position, boss_position, file_path)
		self.update_info_text("Boss placed ")
		self.loading_progress = 60
		# Compute the shortest distance from the player to the boss
		#print("distance form player to boss : ",dijkstra_distance(player_position, boss_position, file_path))
		level_story=LEVEL_STORIES["roguelike"]
		map_image=create_image_from_csv(f"map/floor_{self.level}/map_{self.level}_Collisions.csv",f'graphics/tilemap/map_{self.style}/map.png')
		self.update_info_text("Create level story from LLM")
		story=Create_story_LLM(level_story,self.width,"Roguelike")
		self.level_story=story
		self.loading_progress = 70
		self.update_info_text("Create level Objective from LLM")
		objective=Create_Level_objective_LLM(story,self.width,"Roguelike")
		self.level_objective=objective
		my_timer = Timer(10000) # 10 seconds timer
		my_text = TextObject(objective, None, (0, 0, 0), (100, 200), my_timer, "graphics/UI/Objective/7 Dialogue Box/Idle/1.png")
		self.timer=my_timer
		self.objective_text=my_text
		my_timer.obj = my_text
		
		self.loading_progress = 80
		self.update_info_text("Placing tiles from LLM")
		place_LLM_tiles(story,player_position,boss_position,"raccoon",self.width,"Roguelike",self.level,new_rooms,objective)
		self.visible_sprites.set_camera_level(self.level,self.style)
		self.loading_progress = 90
		layouts = {
		'Collisions': import_csv_layout(f'map/Floor_{self.level}/map_{self.level}_Collisions.csv'),
		'Interactions': import_csv_layout(f'map/Floor_{self.level}/map_{self.level}_Interactions.csv'),
		'Monsters': import_csv_layout(f'map/Floor_{self.level}/map_{self.level}_Monsters.csv'),
					
	}
		graphics = {
			'Collisions': import_folder(f'map/graphics_{self.style}/Collisions'),
			'Floor': import_folder(f'map/graphics_{self.style}/Floor'),
			'Object': import_folder(f'map/graphics_{self.style}/Object'),
				
		}
		self.update_info_text("Displaying")
		for style,layout in layouts.items():
			for row_index,row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '0':
						x = col_index * TILESIZE
						y = row_index * TILESIZE
						if style == 'Collisions':
							if col =="88":
								if self.player_placed==False:
									self.player.reset_groups([self.visible_sprites])
									self.player.set_position((x, y))
									self.player_placed=True
		
							if col in ["2","3","4","5","6","7","8","9"]:
								wall_image =graphics['Collisions'][int(col)]
								Tile(
									(x, y),
									wall_image,
									[self.visible_sprites,self.obstacle_sprites],
									'Collisions')
							if col=="666":
								monster_name = 'raccoon'
								print("Boss ????")
								Enemy(
									monster_name,
									(x,y),
									[self.visible_sprites,self.attackable_sprites],
									self.obstacle_sprites,
									self.damage_player,
									self.trigger_death_particles,
									self.add_exp,
									self.logs_path ,
         							True)
							
						if style == 'Interactions':
							if col  in ["777"]:
							
								chest=Chest(
									(x, y),
									
									[self.visible_sprites,self.obstacle_sprites],
									self.obstacle_sprites,
									'Interactions',self.logs_path)
								self.chests.append(chest)
								print(self.chests)
							if col=="82":
								monster_name = 'spirit'
							
								Enemy(
									monster_name,
									(x,y),
									[self.visible_sprites,self.attackable_sprites],
									self.obstacle_sprites,
									self.damage_player,
									self.trigger_death_particles,
									self.add_exp,
         							self.logs_path,False)
							

								
							if col =="444":
								# assuming each object in 'interactions' layer has a 'name' property 
								pos = (x,y)
								portal = Portal(pos, [self.visible_sprites,self.obstacle_sprites], self.obstacle_sprites, "Portal") 
								self.portals.append(portal) 
		minimap = MiniMap(map_image, self.display_surface, (550, 10), (100, 100))
		self.minimap=minimap
		my_timer.activate()
		self.dungeon_sound.play(loops = -1) 
		self.loading_finished = True		
		self.ui.timer.resume()

	def change_map(self):
		# Clear current objects and sprites
		self.visible_sprites.empty()
		self.obstacle_sprites.empty()
		self.npcs.clear()
		self.portals.clear()
		# Increment level and create new map
		if self.level != 0:
			print("self.level,self.max_level",self.level,self.max_level)
			if self.level==self.max_level:
				print("YOUHOU")
				self.dungeon_sound.stop()
				game_won_screen(self.display_surface,self.event,self.win_sound)
			else:
				self.previous_level=self.level
				self.level=0
				self.dungeon_sound.stop()
				self.main_sound.play()
		else:
			print("self.level,self.max_level",self.level,self.max_level)
			if self.level==self.max_level:
				print("YOUHOU")
				self.dungeon_sound.stop()
				game_won_screen(self.display_surface,self.event,self.win_sound)
			else:
				if self.previous_level!= 0:
					self.level=self.previous_level+1
				
				else:
					self.level += 1
		self.create_map()

class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self,Level):
		# general setup 
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_width = self.display_surface.get_size()[0] // 2
		self.half_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2()
		self.level_num=0
		self.style=1
		

	def custom_draw(self, player):
		# getting the offset 
		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.rect.centery - self.half_height
		self.player=player
		
		
		
		floor_offset_pos = self.floor_rect.topleft - self.offset
		self.display_surface.blit(self.floor_surf,floor_offset_pos)
		
		# sort sprites so the player is always drawn last
		sorted_sprites = sorted(self.sprites(), key=lambda sprite: getattr(sprite, 'layer_name', '') == 'Top')
		for sprite in sorted_sprites:
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image, offset_pos)
		
   
	def enemy_update(self,player):
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
		for enemy in enemy_sprites:
			enemy.enemy_update(player)

	def set_camera_level(self,level,style):
     
		self.level=level
		self.style=style
		# creating the floor
		self.floor_surf = pygame.image.load(f'graphics/tilemap/map_{self.style}/map.png').convert()
		self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))
