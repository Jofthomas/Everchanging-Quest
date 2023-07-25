import pygame
from settings import *

from support import import_folder
class Upgrade:
	def __init__(self,player,level):

		# general setup
		self.display_surface = pygame.display.get_surface()
		self.player = player
		self.attribute_nr = len(player.stats)
		self.attribute_names = list(player.stats.keys())
		self.max_values = list(player.max_stats.values())
		self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
		self.level=level
		#animation
		self.animation_loop=1
		self.import_player_assets()
		self.frame_index = 0
		self.animation_speed = 0.30
		# item creation
		self.height = self.display_surface.get_size()[1] * 0.8
		self.width = self.display_surface.get_size()[0] // 6
		self.create_items()
		self.status = 'Open'
		# selection system 
		self.selection_index = 0
		self.selection_time = None
		self.can_move = True
		#self.book_open = import_folder('graphics/UI/Book/Book Animated/Book Open & Close/Simple Book/Open')
		self.close_time = None
		self.current_left_page_content = None
		self.current_right_page_content = None
		self.turn_finished=True
		self.close_started=False
		self.current_menu = None  # Add this line
		self.unequip_menu = None   # Add this line
		self.last_click_time = 0
		self.last_mousepos=None
		self.previous_level=level.level
	def import_player_assets(self):
		character_path = 'graphics/UI/Book/Book Animated/Book Open & Close/Simple Book/'
		self.animations = {'Open': [],'Close': [],'Left': [],'Right': [],'Tab0': [],'Tab1': [],'Tab2': [],'Tab3': [],'Tab4': [],'Tab5': [],
			}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)
	def get_status(self):
		
		return self.status
	def set_status(self,status):
		
		self.status = status
		self.frame_index=0
		
		
	def input(self):
		keys = pygame.key.get_pressed()

		if self.can_move:
			if keys[pygame.K_DOWN] and self.selection_index < len(self.item_list) - 1:
				self.selection_index += 1
				self.status="Left"
				self.can_move = False
				self.selection_time = pygame.time.get_ticks()
				self.current_left_page_content = self.item_list[self.selection_index].left_page_content
				self.current_right_page_content = self.item_list[self.selection_index].right_page_content
			elif keys[pygame.K_UP] and self.selection_index > 0: # Also ensure it never goes below 0
				self.selection_index -= 1
				self.status="Right"
				self.can_move = False
				self.selection_time = pygame.time.get_ticks()
				self.current_left_page_content = self.item_list[self.selection_index].left_page_content
				self.current_right_page_content = self.item_list[self.selection_index].right_page_content
			        # Add a loop for event checking
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()

				# Check click events for each image on the current pages
				if self.current_left_page_content is not None:
					for item in self.current_left_page_content:
						if isinstance(item, Image):
							item.check_click(event)

				if self.current_right_page_content is not None:
					for item in self.current_right_page_content:
						if isinstance(item, Image):
							item.check_click(event)
				if event.type == pygame.MOUSEBUTTONUP and event.button == 3:  # Right-click
					for item in self.player.inventory:
						menu = item.check_click(event)
						if menu:
							self.current_menu = menu
				if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left-click
					print("Left click")
					if self.current_menu is not None and not self.current_menu.check_click(event):
						self.current_menu = None
					if self.unequip_menu is not None and not self.unequip_menu.check_click(event):
						self.unequip_menu = None  # Close unequip menu if click is not on it



								
	def animate(self):
		
		self.animation_finished=False
		if self.status in ["Left", "Right"]:
			self.turn_finished=False
		if self.status=="Close":
				self.close_started=True
		else:
				self.close_started=False
		animation = self.animations[self.status]
		
		# increment frame index
		self.frame_index += self.animation_speed
		
		# if frame_index is greater than the total frames
		# set it to the last frame index
		if self.frame_index >= len(animation):
			self.frame_index = len(animation) - 1
			if "Tab" in self.status:
				self.turn_finished=True
			if self.status in ["Left", "Right"]:
				self.status=f"Tab{self.selection_index}"
				
			if self.status=="Close":
				self.animation_finished=True
				self.turn_finished=False
				
			if self.status=="Open":
				self.open_finished=True
				self.status=f"Tab{self.selection_index}"
				self.current_left_page_content = self.item_list[self.selection_index].left_page_content
				self.current_right_page_content = self.item_list[self.selection_index].right_page_content

		# set the image
		self.image = animation[int(self.frame_index)]
		
		# display the image on the surface
		self.display_surface.blit(self.image, (-30, -30))
				

	def selection_cooldown(self):
		if not self.can_move:
			current_time = pygame.time.get_ticks()
			if current_time - self.selection_time >= 300:
				self.can_move = True
	def on_click(self, event=None):
		print('Upgrade was clicked.')

	def create_items(self):
		self.item_list = []
		# Create some items (tabs) here
		# An example of creating a tab (you need to fill in the actual parameters)
		# Create some Text and Image objects for the left page
		if self.level.level==0:
			left_page_content = [
				Image("graphics/UI/Book/Book Resources/Decoration/37.png", (4, 81)),
				Text("Story", (180, 180),24),
				#Text(f"{STORY}", (180, 180),24),
				MultilineText(STORY, (130, 220), 250),
				Text("Objective", (180, 380),18),
				Text("*No objectives in Town*", (90, 440),7),

				
			]
		else:
			if self.level.level_story is not None and self.level.level_objective is not None:
				story=self.level.level_story
				obj=story=self.level.level_objective
				left_page_content = [
					Image("graphics/UI/Book/Book Resources/Decoration/37.png", (4, 81)),
					Text("Story", (180, 180),24),
					#Text(f"{STORY}", (180, 180),24),
					MultilineText(f"{self.level.level_story}", (130, 220), 250),
					Text("Objective", (180, 380),18),
					MultilineText(f"{obj}", (130, 400), 250),

					
				]
			else:
				left_page_content = [
					Image("graphics/UI/Book/Book Resources/Decoration/37.png", (4, 81)),
					Text("Story", (180, 180),24),
					#Text(f"{STORY}", (180, 180),24),
					MultilineText("Story display is bugged", (130, 220), 250),
					Text("Objective", (180, 380),18),
					MultilineText("Objective display is bugged", (130, 220), 250),

					
				]
		
		if self.level.minimap is not None:
			
			
			# Create some Text and Image objects for the right page
			right_page_content = [
				Text("Map", (460, 180),24),
				Image("graphics/tilemap/map_1/map.png", (425, 230), size_ratio=0.05),
			]
		else:
			right_page_content = [
				Text("Map", (460, 180),24),
				Text("*Map is not available on level 0*", (415, 250),9),
			]
		tab1 = Tab(0, self.font,left_page_content,right_page_content)
		left_page_content = [
			Image("graphics/UI/Book/Book Resources/Decoration/10.png", (65, 126)),
			Image("graphics/UI/Book/Book Resources/Decoration/37.png", (4, 81)),
			Image("graphics/UI/Side Portrait Medium.png", (122, 156)),
			Image("graphics/UI/Book/Book Resources/Decoration/29.png", (173, 172)),
			Text("Profile", (206, 180),24),
			Text("Health", (180, 260)),
			Text(f"{self.player.stats['health']}", (180, 275)),
			Text(f"Max : {self.player.max_stats['health']}", (285, 275),7),
			Text(f"Cost : {self.player.upgrade_cost['health']}", (285, 285),7),
			Image("graphics/UI/Book/Book Resources/Buttons/12.png", (142, 260), callback=self.on_click),
			Image("graphics/UI/Book/Book Resources/Buttons/13.png", (260, 260), callback=self.on_click),
			Text("Energy", (180, 300)),
			Text(f"{self.player.stats['energy']}", (180, 315)),
			Text(f"Max : {self.player.max_stats['energy']}", (285, 315),7),
			Text(f"Cost : {self.player.upgrade_cost['energy']}", (285, 325),7),
			Image("graphics/UI/Book/Book Resources/Buttons/12.png", (142, 300), callback=self.on_click),
			Image("graphics/UI/Book/Book Resources/Buttons/13.png", (260, 300), callback=self.on_click),
			Text("Magic", (180, 340)),
			Text(f"{self.player.stats['magic']}", (180, 355)),
			Text(f"Max : {self.player.max_stats['magic']}", (285, 355),7),
			Text(f"Cost : {self.player.upgrade_cost['magic']}", (285, 365),7),
			Image("graphics/UI/Book/Book Resources/Buttons/12.png", (142, 340), callback=self.on_click),
			Image("graphics/UI/Book/Book Resources/Buttons/13.png", (260, 340), callback=self.on_click),
			Text("Strength", (180, 380)),	
			Text(f"{self.player.stats['attack']}", (180, 395)),
			Text(f"Max : {self.player.max_stats['attack']}", (285, 395),7),
			Text(f"Cost : {self.player.upgrade_cost['attack']}", (285, 405),7),
			Image("graphics/UI/Book/Book Resources/Buttons/12.png", (142, 380), callback=self.on_click),
			Image("graphics/UI/Book/Book Resources/Buttons/13.png", (260, 380), callback=self.on_click),
			Text("Speed", (180, 420)),
			Text(f"{self.player.stats['speed']}", (180, 435)),
			Text(f"Max : {self.player.max_stats['speed']}", (285, 435),7),
			Text(f"Cost : {self.player.upgrade_cost['speed']}", (285, 445),7),
			Image("graphics/UI/Book/Book Resources/Buttons/12.png", (142, 420), callback=self.on_click),
			Image("graphics/UI/Book/Book Resources/Buttons/13.png", (260, 420), callback=self.on_click),
			 Text("***Stats can't be changed manually yet***", (90, 480),7),
		]

		# Create some Text and Image objects for the right page
		right_page_content = [
			
			Text("Equipment", (460, 180),24),
			
			Image("graphics/UI/Book/Book Resources//Equipments/slot2.png", (454, 224)),
			Image("graphics/UI/Book/Book Resources//Equipments/Hero.png", (519, 255)),
			Image("graphics/UI/Book/Book Resources//Equipments/1.png", (454, 224), size_ratio=2),
			Image("graphics/UI/Book/Book Resources//Equipments/slot2.png", (454, 265)),
			Image("graphics/UI/Book/Book Resources//Equipments/2.png", (454, 265), size_ratio=2),
			Image("graphics/UI/Book/Book Resources//Equipments/slot2.png", (454, 306)),
			Image("graphics/UI/Book/Book Resources//Equipments/3.png", (454, 306), size_ratio=2),
			Image("graphics/UI/Book/Book Resources//Equipments/slot2.png", (582, 224)),
			Image("graphics/UI/Book/Book Resources//Equipments/4.png", (584, 224), size_ratio=2),
			Image("graphics/UI/Book/Book Resources//Equipments/slot2.png", (582, 265)),
			Image("graphics/UI/Book/Book Resources//Equipments/5.png", (584, 265), size_ratio=2),
			Image("graphics/UI/Book/Book Resources//Equipments/slot2.png", (582, 306)),
			Image("graphics/UI/Book/Book Resources//Equipments/7.png", (584, 306), size_ratio=2),
			Text("***This section is still bugged***", (420, 440),7),
			Text("Equipment", (460, 180),24),
			
		]
		tab2 = Tab(1, self.font,left_page_content,right_page_content)
		left_page_content = [
      Image("graphics/UI/Book/Book Resources/Decoration/37.png", (4, 81)),
	  Text("Skills & Magic",  (90, 180),24),
	  Image("graphics/UI/Book/Book Resources//Equipments/Hotbar16x16.png", (122, 236),),
	  Image("graphics/UI/Book/Book Resources//Equipments/Hotbar16x16.png", (122, 334),),
	  
      Text("***This section was not yet implemented***", (90, 440),7),
      
      ]
		right_page_content = [
      
      Text("***This section is still bugged***", (420, 440),7),
      Image("graphics/UI/Book/Book Resources//Equipments/Inventory.png", (425, 252), size_ratio=0.7),
      Text("Inventory", (460, 180),24),
      ]
		tab3 = Tab(2, self.font,left_page_content,right_page_content)
		left_page_content = [Text("***This section was not yet implemented***", (90, 440),7),]
		right_page_content = [Text("***This section was not yet implemented***", (420, 440),7),]
		tab4 = Tab(3, self.font,left_page_content,right_page_content)
		left_page_content = [
      Image("graphics/UI/Book/Book Resources/Decoration/37.png", (4, 81)),
      Text("Controls", (130, 180),24),
      Image("graphics/UI/Book/Book Resources//Equipments/Move.png", (80, 230), size_ratio=2),
		Text("Move ", (220, 230),12),
		Image("graphics/UI/Book/Book Resources//Equipments/E.png", (122, 260), size_ratio=2),
		Text("Attack ", (220, 260),12),
		Image("graphics/UI/Book/Book Resources//Equipments/Q.png", (122, 290), size_ratio=2),
		Text("Magic ", (220, 290),12),
		Image("graphics/UI/Book/Book Resources//Equipments/Tab.png", (118, 320), size_ratio=2),
		Text("Chaneg magic ", (220, 320),12),
		Image("graphics/UI/Book/Book Resources//Equipments/Space.png", (118, 350), size_ratio=2),
		Text("Dash ", (220, 350),12),
		Image("graphics/UI/Book/Book Resources//Equipments/Enter.png", (118, 380), size_ratio=2),
		Text("Interact ", (220, 380),12),
		Image("graphics/UI/Book/Book Resources//Equipments/Y.png", (122, 410), size_ratio=2),
		Text("Enter portal ", (220, 410),12),
		Image("graphics/UI/Book/Book Resources//Equipments/M.png", (122, 450), size_ratio=2),
		Text("Enter portal ", (220, 450),12),
		
      Text("***This section cannot be modified yet***", (90, 480),7),
      
      ]
		right_page_content = []
		tab6 = Tab(5, self.font,left_page_content,right_page_content)
		left_page_content = [Text("***This section was not yet implemented***", (90, 440),7),]
		right_page_content = [Text("*** Please Don't Die !***", (480, 440),7),]
		tab5 = Tab(4, self.font,left_page_content,right_page_content)
		self.item_list.append(tab1)
		self.item_list.append(tab2)
		self.item_list.append(tab3)
		self.item_list.append(tab4)
		self.item_list.append(tab5)
		self.item_list.append(tab6)
		

		# You can create more tabs as needed


	def display(self):
		self.input()
		self.selection_cooldown()
  
	def display_item_info(self, item):
		# Define position, width, and height of the info card
		info_card_pos = (430, 360)
		info_card_width = 150  # Increase the width to accommodate more information
		info_card_height = 150  # Increase the height for the same reason

		# Create a surface for the info card
		info_card_surface = pygame.Surface((info_card_width, info_card_height))

		# Set a background color for the info card
		info_card_surface.fill((200, 200, 200))  # A light gray color

		# Create a font object
		font = pygame.font.Font(None, 18)

		# Render the item's info and blit it onto the info card surface
		info_text = [
			f"Name: {item.name}",
			f"Type: {item.item_type}",
			f"Health Bonus: {item.health_bonus}",
			f"Energy Bonus: {item.energy_bonus}",
			f"Attack Bonus: {item.attack_bonus}",
			f"Magic Bonus: {item.magic_bonus}",
			f"Speed Bonus: {item.speed_bonus}",
		]

		y_offset = 10  # Start 10 pixels from the top
		for text in info_text:
			rendered_text = font.render(text, True, (0, 0, 0))
			info_card_surface.blit(rendered_text, (10, y_offset))
			y_offset += 13  # Move down by 30 pixels for the next line of text

		# Draw a black border around the info card
		border_color = (0, 0, 0)  # Black color
		border_thickness = 1  # You can change this value as needed
		pygame.draw.rect(info_card_surface, border_color, info_card_surface.get_rect(), border_thickness)

		# Blit the info card surface onto the display surface
		self.display_surface.blit(info_card_surface, info_card_pos)  # Assuming 'self.screen' is your display surface

		
	def display_current_content(self):
		if self.current_left_page_content is not None:
			for item in self.current_left_page_content:
				if isinstance(item, Text):
					font = pygame.font.Font(UI_FONT, item.size if item.size is not None else UI_FONT_SIZE)
					text_surface = font.render(item.content, True, pygame.Color('Black'))
					self.display_surface.blit(text_surface, item.position)
				elif isinstance(item, Image):
					self.display_surface.blit(item.image, item.rect.topleft)
				elif isinstance(item, MultilineText):  # New check for MultilineText
					item.draw(self.display_surface)  # Draw MultilineText

		# Right page content
		if self.current_right_page_content is not None:
			for item in self.current_right_page_content:
				
				if isinstance(item, Image):
					self.display_surface.blit(item.image, item.rect.topleft)
				if isinstance(item, Text):
					font = pygame.font.Font(UI_FONT, item.size if item.size is not None else UI_FONT_SIZE)
					text_surface = font.render(item.content, True, pygame.Color('Black'))
					self.display_surface.blit(text_surface, item.position)
					if item.content == "Inventory":
						
						inventory_img_position = (item.position[0]-37 , item.position[1]+70 )  # Adjust as needed
						self.draw_inventory(inventory_img_position)
				
					elif item.content == "Equipment":
						self.draw_equipment()
				elif isinstance(item, MultilineText):  # New check for MultilineText
					item.draw(self.display_surface)  # Draw MultilineText



	def draw_inventory(self, inventory_img_position):
		# Initial size and offset of the inventory grid
		size_ratio=0.7
		initial_size = (int(372 * size_ratio), int(167 * size_ratio))
		initial_offset = (int(22 * size_ratio), int(20 * size_ratio))

		# Cell size and offset
		cell_size = (int(32 * size_ratio), int(32 * size_ratio))
		cell_offset = (int(10 * size_ratio), int(14 * size_ratio))
		# Calculate the number of cells in x and y direction
		grid_size_x = (initial_size[0] - initial_offset[0]) // (cell_size[0] + cell_offset[0])
		grid_size_y = (initial_size[1] - initial_offset[1]) // (cell_size[1] + cell_offset[1])

		# Get the player's inventory
		inventory = self.player.inventory
		
		# Ensure that the number of items in the inventory does not exceed the number of cells
		assert len(inventory) <= grid_size_x * grid_size_y, "Not enough space in the inventory"

		for i, item in enumerate(inventory):
			# Calculate the cell's position in the grid
			cell_x = i % grid_size_x
			cell_y = i // grid_size_x
			
			# Calculate the position of the top-left corner of the cell in the image
			pos_x = inventory_img_position[0] + initial_offset[0] + cell_x * (cell_size[0] + cell_offset[0])
			pos_y = inventory_img_position[1] + initial_offset[1] + cell_y * (cell_size[1] + cell_offset[1])
			item.x=pos_x
			item.y=pos_y
			# Display the item image in the cell
			menu = ContextMenu((pos_x, pos_y), ['Equip', 'Discard'], 
								[lambda: self.addItem(item), lambda: self.discardItem(item)])  
			item.add_menu(menu)
			self.display_surface.blit(item.image, (pos_x, pos_y))
			# If mouse position is over the item, display the info card
			mouse_pos = pygame.mouse.get_pos()
			item_rect = pygame.Rect(pos_x, pos_y, item.image.get_width(), item.image.get_height())
			if item_rect.collidepoint(mouse_pos):
				self.display_item_info(item)
   
	def draw_equipment(self):
    # Define positions for equipment slots
		equipment_positions = {
			'headset': (453, 222),
			'weapon': (580, 222),
			'torso': (453, 263),
			'legs': (453, 305),
			'jewel': (580, 263),
			'boots': (580, 305),
		}

		# Get the player's equipped items
		equipped_items = self.player.equipped_items

		for item_type, item in equipped_items.items():
			if item is not None:   # Only draw the item if the slot is not empty
				# Calculate the position of the item in the image
				pos_x, pos_y = equipment_positions[item_type]
				item.x = pos_x
				item.y = pos_y
				item.update_rect(pos_x,pos_y)	
				# Scale the image to twice its size
				width, height = item.image.get_size()  # Get the size of the image
				scaled_image = pygame.transform.scale(item.image, (width * 2, height * 2))  # Scale the image
				
				self.display_surface.blit(scaled_image, (pos_x, pos_y))  # Blit the scaled image
				 # If mouse position is over the item, display the info card
				mouse_pos = pygame.mouse.get_pos()
				item_rect = pygame.Rect(pos_x, pos_y, item.image.get_width(), item.image.get_height())
				if item_rect.collidepoint(mouse_pos):
					self.display_item_info(item)



   
	def update(self, event):
		self.get_status()
		if self.previous_level!=self.level.level:
			self.create_items()
		
		self.animate()
		if self.turn_finished and not self.close_started:
			self.display_current_content()
		 # Draw the equipment and inventory
	
		
		# Get the player's equipped items and inventory
		equipped_items = self.player.equipped_items
		inventory_items = self.player.inventory

		if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left mouse button released
			mouse_pos = pygame.mouse.get_pos()
			now = pygame.time.get_ticks()
			
			if now - self.player.last_equip_time < 1000 :  # If it's been less than 1s since the last equip/unequip
				return  # Don't process equip/unequip actions
			if self.last_mousepos==mouse_pos:
				return
			# Check if an equipped item is double clicked
			for item_type, item in equipped_items.items():
				if item is not None and item.rect.collidepoint(mouse_pos) and self.status=='Tab1':
					if now - self.last_click_time < 500:  # If it's been less than 500ms since the last click
						print('unequip :', item.name)
						self.unequipItem(item)  # Unequip the item
						self.last_mousepos=mouse_pos
						self.player.last_equip_time = now  # Update the last equip time

					self.last_click_time = now

			# Check if an inventory item is double clicked
			for item in inventory_items:
				if item.rect.collidepoint(mouse_pos)and  self.status=='Tab2':
					if now - self.last_click_time < 500:  # If it's been less than 500ms since the last click
						print('equip :', item.name)
						self.addItem(item)  # Equip the item
						self.last_mousepos=mouse_pos
						self.player.last_equip_time = now  # Update the last equip time

					self.last_click_time = now
		self.previous_level=self.level.level

		if self.current_menu:
			self.current_menu.display()
	def addItem(self,item):
		self.player.equip_item(item)
		self.create_items()
	def unequipItem(self,item):
		ans=self.player.unequip_item(item)
		self.create_items()
		
	def discardItem(self,item):
		self.player.remove_to_inventory(item)
		self.create_items()
class Text:
    def __init__(self, content, position, size=None):
        self.content = content
        self.position = position
        self.size = size  # size is optional
        
class Image:
    def __init__(self, filepath, position, size_ratio=1.0, callback=None):
        self.filepath = filepath
        self.position = position
        self.image = pygame.image.load(filepath)
        self.image = pygame.transform.scale(self.image, 
                                            (int(self.image.get_width() * size_ratio),
                                             int(self.image.get_height() * size_ratio)))
        self.rect = self.image.get_rect(topleft=position)
        self.rect.inflate_ip(10, 10)  # Inflate the rectangle by 10 pixels in both directions
        self.callback = callback

    def check_click(self, event):
        if self.callback and event.type == pygame.MOUSEBUTTONUP and self.rect.collidepoint(event.pos):
            self.callback()

class MultilineText:
    def __init__(self, content, position, width, font_name=None, font_size=14):
        self.content = content
        self.position = position
        self.width = width
        self.font_name = font_name
        self.font_size = font_size
        self.font = pygame.font.Font(font_name, font_size)
        self.rendered_text = []
        self.render()
        

    def render(self):
        x, y = self.position
        words = self.content.split(' ')
        line = ''
        for word in words:
            test_line = line + word + ' '
            text = self.font.render(test_line, True, (0, 0, 0))  # assuming black text color
            if text.get_width() > self.width:
                self.rendered_text.append((self.font.render(line, True, (0, 0, 0)), (x, y)))
                y += self.font.get_linesize()
                line = word + ' '
            else:
                line = test_line
        else:
            self.rendered_text.append((self.font.render(line, True, (0, 0, 0)), (x, y)))

    def draw(self, surface):
        for text, position in self.rendered_text:
            surface.blit(text, position)

   

class Tab:
    def __init__(self, index, font, left_page_content, right_page_content):
        self.index = index
        self.font = font
        self.left_page_content = left_page_content  # list of Text and/or Image objects
        self.right_page_content = right_page_content  # list of Text and/or Image objects
        
class ContextMenu:
    def __init__(self, position, options, callbacks, border=5, bgcolor=(0, 0, 0), bordercolor=(255, 255, 255)):
        self.position = position
        self.options = options
        self.callbacks = callbacks
        self.border = border
        self.bgcolor = bgcolor
        self.bordercolor = bordercolor
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.display_surface = pygame.display.get_surface()
        self.menu_height = len(options) * 20 + 2*border
        self.menu_width = max([self.font.size(option)[0] for option in options]) + 2*border

    def display(self):
        # draw the border
        pygame.draw.rect(self.display_surface, self.bordercolor, (self.position[0] - self.border, self.position[1] - self.border, self.menu_width, self.menu_height))
        
        # draw the background
        pygame.draw.rect(self.display_surface, self.bgcolor, (self.position[0], self.position[1], self.menu_width - self.border, self.menu_height - self.border))

        # draw the text
        for i, option in enumerate(self.options):
            text_surface = self.font.render(option, True, pygame.Color('White'))
            self.display_surface.blit(text_surface, (self.position[0] + self.border, self.position[1] + i * 20))

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            for i, option in enumerate(self.options):
                rect = pygame.Rect(self.position[0]+16, self.position[1] + i * 20, self.menu_width, 20)
                if rect.collidepoint(event.pos):
                    self.callbacks[i]()
                    return True
        return False


