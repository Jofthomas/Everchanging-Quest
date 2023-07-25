import pygame 

class Weapon(pygame.sprite.Sprite):
    def __init__(self,player,groups):
        super().__init__(groups)
        self.sprite_type = 'weapon'
        direction = player.status.split('_')[0]

        # graphic
        self.image = pygame.Surface((50, 50))  # Create an empty surface
      
        self.image.set_alpha(0)  # Make it fully transparent
        

        # placement
        if direction == 'right':
            self.rect = self.image.get_rect(midleft = player.rect.midright )
        elif direction == 'left': 
            self.rect = self.image.get_rect(midright = player.rect.midleft )
        elif direction == 'down':
            self.rect = self.image.get_rect(midtop = player.rect.midbottom )
        else:
            self.rect = self.image.get_rect(midbottom = player.rect.midtop )
