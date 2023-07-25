import pygame
class Item:
    def __init__(self, name, description, item_type, image, health_bonus, energy_bonus, attack_bonus, magic_bonus, speed_bonus):
        self.name = name
        self.description = description
        self.item_type = item_type
        # if no image is provided, use the default image
        self.image = pygame.image.load(image) if image else pygame.image.load("graphics/items/default_item.png")
        
        self.health_bonus = health_bonus
        self.energy_bonus = energy_bonus
        self.attack_bonus = attack_bonus
        self.magic_bonus = magic_bonus
        self.speed_bonus = speed_bonus
        self.menu = None
        self.x=0
        self.y=0
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)  # Position the rectangle.
        self.unequip_menu = None
        
        
    def add_menu(self, menu):
        self.menu = menu
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)  # Position the rectangle.
    def update_rect(self,x,y):
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)  # Position the rectangle.
        
    def add_unequip_menu(self, menu):
        self.unequip_menu = menu
        
    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 3 and self.rect.collidepoint(event.pos):  # Right-click
            if self.menu:
                
                return self.menu  # Display the context menu if it exists
        
