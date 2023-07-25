import pygame 
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, image_path, groups):
        super().__init__(groups)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)