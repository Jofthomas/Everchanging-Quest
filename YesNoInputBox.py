import pygame
from pygame.locals import *
import time

class YesNoInputBox:
    def __init__(self, x, y, width, height, text, portal, player=None,font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color('white')
        self.choice_color = pygame.Color('#292929')
        self.text = text
        self.player=player
        self.portal=portal
        self.font = pygame.font.Font(None, font_size)
        self.txt_surface = self.font.render(text, True, self.color)
        self.display_surface = pygame.display.get_surface()
        self.color_highlight = pygame.Color('white')
        self.dialog_image = pygame.image.load("graphics/UI/dialog_background2.png")
        self.dialog_image_rect = self.dialog_image.get_rect()  # Get image rect
        self.value = True
        self.is_visible = False

        self.option_width = width // 4  # Smaller width
        self.option_height = height // 4  # Smaller height
        self.right_margin = width // 8  # Margin from the right
        
         # Rectangles' positions will be calculated in draw method
        self.rect_yes = pygame.Rect(0, 0, self.option_width, self.option_height)
        self.rect_no = pygame.Rect(0, 0, self.option_width, self.option_height)
        self.txt_surface_yes = self.font.render("Yes", True, self.color)
        self.txt_surface_no = self.font.render("No", True, self.color)

    def handle_input(self,player):
        keys = pygame.key.get_pressed()
       
        if keys[pygame.K_ESCAPE]:
            self.close(player)
        if keys[pygame.K_y]:
            if self.value:
                self.close(player)
                time.sleep(0.1)
                self.portal.increase_level()
            else:
                self.close(player)
            
    
            
           
        elif keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            time.sleep(0.15)
            self.value = not self.value
            
    def close(self,player):
        
        self.is_visible = False
        player.can_move=True
        time.sleep(0.2)

        player.portal_interracting=False
    def draw(self):
        if self.is_visible:
            dialog_image_rect = self.dialog_image.get_rect()
            dialog_image_rect.midbottom = self.display_surface.get_rect().midbottom
            offset = 50
            dialog_image_rect.y -= offset
            # Update positions of yes and no options
            self.rect_yes.topleft = (dialog_image_rect.right - self.option_width - self.right_margin, 
                                     dialog_image_rect.top - 2 * self.option_height - 3
                                     )
            self.rect_no.topleft = (dialog_image_rect.right - self.option_width - self.right_margin, 
                                    dialog_image_rect.top - self.option_height)

            # Draw the dialog image (background container) first
            self.display_surface.blit(self.dialog_image, dialog_image_rect)
            y = dialog_image_rect.y + 10
            snip = self.font.render("Do you wish to enter?", True, "white")
            self.display_surface.blit(snip, (dialog_image_rect.x + 10, y))

            pygame.draw.rect(pygame.display.get_surface(), self.choice_color, self.rect_yes)
            pygame.draw.rect(pygame.display.get_surface(), self.choice_color, self.rect_no)

            if self.value:
                pygame.draw.rect(pygame.display.get_surface(), self.color_highlight, self.rect_yes)
                pygame.display.get_surface().blit(self.txt_surface_yes, (self.rect_yes.x + 5, self.rect_yes.y + 5))
                pygame.display.get_surface().blit(self.txt_surface_no, (self.rect_no.x + 5, self.rect_no.y + 5))
                self.txt_surface_yes = self.font.render("Yes", True, self.choice_color)
                self.txt_surface_no = self.font.render("No", True, self.color)
                
            else:
                pygame.draw.rect(pygame.display.get_surface(), self.color_highlight, self.rect_no)
                pygame.display.get_surface().blit(self.txt_surface_yes, (self.rect_yes.x + 5, self.rect_yes.y + 5))
                pygame.display.get_surface().blit(self.txt_surface_no, (self.rect_no.x + 5, self.rect_no.y + 5))
                self.txt_surface_no = self.font.render("No", True, self.choice_color)
                self.txt_surface_yes = self.font.render("Yes", True, self.color)
    def update(self,player):
        self.handle_input(player)
