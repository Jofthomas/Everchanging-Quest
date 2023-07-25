import pygame 
from settings import *
from support import import_folder
from math import sin
from Items import Item
class Player(pygame.sprite.Sprite):
	def __init__(self,pos,groups,obstacle_sprites,create_attack,destroy_attack,create_magic):
		super().__init__(groups)
		self.image = pygame.image.load('graphics/test/player.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = pygame.Rect(self.rect.topleft, (16, 24))

		# graphics setup
		self.import_player_assets()
		self.status = 'down'
		self.frame_index = 0
		self.animation_speed = 0.10
		self.attack_animation_speed = 0.10

		# movement 
		self.direction = pygame.math.Vector2()
		
		self.attacking = False
		self.attack_cooldown = 400
		self.attack_time = None
		self.dashing = False
		
		self.dash_time = pygame.time.get_ticks()-5000
		self.dash_distance = 400
		self.can_dash=None
		self.dash_cooldown=5000
		self.can_move=True
		self.portal_interracting=False
		self.obstacle_sprites = obstacle_sprites
  
		# stats
		self.stats = {'health': 100,'energy':60,'attack': 10,'magic': 4,'speed': 4.5}
		self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic' : 10, 'speed': 10}
		self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic' : 100, 'speed': 100}
		self.health = self.stats['health'] 
		self.energy = self.stats['energy'] 
		self.exp = 0
		self.speed = self.stats['speed']
		self.dash_speed = self.speed *2
  
		# weapon
		self.create_attack = create_attack
		self.destroy_attack = destroy_attack
		# magic 
		self.create_magic = create_magic
		self.magic_index = 0
		self.magic = list(magic_data.keys())[self.magic_index]
		self.can_switch_magic = True
		self.magic_switch_time = None
		self.switch_duration_cooldown = 200
		# damage timer
		self.vulnerable = True
		self.hurt_time = None
		self.invulnerability_duration = 500

		# import a sound
		self.weapon_attack_sound = pygame.mixer.Sound('audio/sword.wav')
		self.weapon_attack_sound.set_volume(0.1)
  
		# inventory and equipped items
		self.inventory = []
		self.equipped_items = {'weapon': None, 'headset': None, 'torso': None, 'legs': None, 'boots': None, 'jewel': None}
		self.last_equip_time = 0  # Add this new attribute
		
		
	def reset_groups(self, new_groups):
		# Remove from current groups
		self.kill()
		# Add to new groups
		self.add(new_groups)
	def set_position(self, pos):
		self.rect.topleft = pos
		
		self.hitbox = pygame.Rect(self.rect.topleft, (16, 24))

	def import_player_assets(self):
		character_path = 'graphics/player/'
		self.animations = {'up': [],'down': [],'left': [],'right': [],
			'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
			'down_attack':[],'up_attack':[],'left_attack':[],'right_attack':[],
			'down_dash':[],'up_dash':[],'left_dash':[],'right_dash':[],
			}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)

	def input(self,event):
		
		if not self.attacking and not self.dashing and self.can_move:
			keys = pygame.key.get_pressed()

			# movement input
			if keys[pygame.K_UP] or keys[pygame.K_w]:
				self.direction.y = -1
				self.status = 'up'
			elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
				self.direction.y = 1
				self.status = 'down'
			else:
				self.direction.y = 0

			if keys[pygame.K_RIGHT]or keys[pygame.K_d]:
				self.direction.x = 1
				self.status = 'right'
			elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
				self.direction.x = -1
				self.status = 'left'
			else:
				self.direction.x = 0

			# attack input 
			if keys[pygame.K_e]:
				if not self.attacking:
					self.attacking = True
					self.attack_time = pygame.time.get_ticks()
					
					self.create_attack()
					self.weapon_attack_sound.play()

			# magic input 
			if keys[pygame.K_q]:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
				style = list(magic_data.keys())[self.magic_index]
				strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
				cost = list(magic_data.values())[self.magic_index]['cost']
				self.create_magic(style,strength,cost)
			# dash input 
			if keys[pygame.K_SPACE] and not self.dashing and pygame.time.get_ticks() - self.dash_time >= self.dash_cooldown:
				self.dashing = True
				self.dash_time = pygame.time.get_ticks()
				
				if 'idle' in self.status:
					self.status = self.status.replace('_idle','_dash')
				else:
					self.status = self.status + '_dash'
			if keys[pygame.K_TAB] and self.can_switch_magic:
				self.can_switch_magic = False
				self.magic_switch_time = pygame.time.get_ticks()
				
				if self.magic_index < len(list(magic_data.keys())) - 1:
					self.magic_index += 1
				else:
					self.magic_index = 0

				self.magic = list(magic_data.keys())[self.magic_index]
			
			
	def get_status(self):
		
		# idle status
		if self.direction.x == 0 and self.direction.y == 0:
			if not 'idle' in self.status and not 'attack' in self.status and not "dash" in self.status:
				self.status = self.status + '_idle'

		if self.attacking:
			self.direction.x = 0
			self.direction.y = 0
			if not 'attack' in self.status:
				if 'idle' in self.status:
					self.status = self.status.replace('_idle','_attack')
				else:
					self.status = self.status + '_attack'
		else:
			if 'attack' in self.status:
				self.status = self.status.replace('_attack','')


		if self.dashing:
			
			if not 'dash' in self.status:
				if 'idle' in self.status:
					self.status = self.status.replace('_idle','_dash')
				else:
					self.status = self.status + '_dash'
		else:
			if 'dash' in self.status:
				self.status = self.status.replace('_dash','')

	def move(self,speed):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()
		if self.dashing:
			speed = self.dash_speed

		self.hitbox.x += self.direction.x * speed
		self.collision('horizontal')
		self.hitbox.y += self.direction.y * speed
		self.collision('vertical')
		self.rect.center = self.hitbox.center

	def collision(self,direction):
		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.x > 0: # moving right
						self.hitbox.right = sprite.hitbox.left
					if self.direction.x < 0: # moving left
						self.hitbox.left = sprite.hitbox.right

		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.y > 0: # moving down
						self.hitbox.bottom = sprite.hitbox.top
					if self.direction.y < 0: # moving up
						self.hitbox.top = sprite.hitbox.bottom

	def cooldowns(self):
		current_time = pygame.time.get_ticks()

		if self.attacking:
			if current_time - self.attack_time >= self.attack_cooldown:
				self.attacking = False
				self.destroy_attack()
		if not self.vulnerable:
			if current_time - self.hurt_time >= self.invulnerability_duration:
				self.vulnerable = True
		if not self.can_switch_magic:
			if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
				self.can_switch_magic = True

	def dash_distances(self):
		current_time = pygame.time.get_ticks()

		if self.dashing:
			
			if current_time - self.dash_time >= self.dash_distance:
				
				self.dashing = False
				if '_dash' in self.status:
					self.status = self.status.replace('_dash', '')
				if self.direction.magnitude() == 0:
					self.status += '_idle'



	def animate(self):
		
		animation = self.animations[self.status]
		
		if "attack" in self.status:
			self.animation_speed=0.5
		else:
			self.animation_speed=0.1
		# loop over the frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		# set the image
  
		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center = self.hitbox.center)
  
				# flicker 
		if not self.vulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)
	def get_full_weapon_damage(self):
		base_damage = self.stats['attack']
		#weapon_damage = weapon_data[self.weapon]['damage']
		return base_damage 

	def get_full_magic_damage(self):
		base_damage = self.stats['magic']
		spell_damage = magic_data[self.magic]['strength']
		return base_damage + spell_damage

	def energy_recovery(self):
		if self.energy < self.stats['energy']:
			self.energy += 0.01 * self.stats['magic']
		else:
			self.energy = self.stats['energy']
	def wave_value(self):
		value = sin(pygame.time.get_ticks())
		if value >= 0: 
			return 255
		else: 
			return 0

 
	def equip_item(self, item):
		if item in self.inventory:
			# unequip the current item of the same type, if there is one
			current_item = self.equipped_items[item.item_type]
			if current_item is not None:
				self.unequip_item(current_item)
			
			# remove the item from the inventory
			self.inventory.remove(item)

			# equip the new item and apply its bonuses
			self.equipped_items[item.item_type] = item
			self.apply_item_bonuses(item)
	
	def unequip_item(self, item):
		# remove the item's bonuses from the player's stats
		self.remove_item_bonuses(item)
		
		self.equipped_items[item.item_type] = None
		print(self.equipped_items[item.item_type])
		self.inventory.append(item)
		return "OK"
		

	def apply_item_bonuses(self, item):
		self.max_stats['health'] += item.health_bonus
		self.max_stats['energy'] += item.energy_bonus
		self.max_stats['attack'] += item.attack_bonus
		self.max_stats['magic'] += item.magic_bonus
		self.max_stats['speed'] += item.speed_bonus
		self.stats['health'] += item.health_bonus
		self.stats['energy'] += item.energy_bonus
		self.stats['attack'] += item.attack_bonus
		self.stats['magic'] += item.magic_bonus
		self.stats['speed'] += item.speed_bonus
		

	def remove_item_bonuses(self, item):
		try:
			self.max_stats['health'] -= item.health_bonus
			self.max_stats['energy'] -= item.energy_bonus
			self.max_stats['attack'] -= item.attack_bonus
			self.max_stats['magic'] -= item.magic_bonus
			self.max_stats['speed'] -= item.speed_bonus
			self.stats['health'] -= item.health_bonus
			self.stats['energy'] -= item.energy_bonus
			self.stats['attack'] -= item.attack_bonus
			self.stats['magic'] -= item.magic_bonus
			self.stats['speed'] -= item.speed_bonus
		except:
			print("already removed")
		
  
	def add_to_inventory(self, item):
		self.inventory.append(item)
  
	def remove_to_inventory(self, item):
		try:
			self.inventory.remove(item)
		except:
			print("already removed")
  
	def get_value_by_index(self,index):
		return list(self.stats.values())[index]

	def get_cost_by_index(self,index):
		return list(self.upgrade_cost.values())[index]
	def update(self,event=None):
		self.input(event)
		self.cooldowns()
		self.dash_distances()
		self.get_status()
		self.animate()
		self.move(self.speed)
		self.energy_recovery()
