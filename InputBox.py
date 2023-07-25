import pygame, sys
from settings import *

class InputBox:

    def __init__(self, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('white')
        self.bg_color = pygame.Color('#292929')
        
        self.font = font
        self.text = ''
        self.placeholder = "Type here..."  # New attribute to store placeholder text
        self.txt_surface = self.font.render(self.placeholder, True, self.color)
        self.bg_surface = pygame.Surface((w, h))
        self.bg_surface.fill(self.bg_color) 
        self.unable_inputs=True
        self.has_input = False  # New attribute to track whether the user has entered any text

    def handle_event(self,dialog):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if dialog.wait_for_input==True:
                 if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        dialog.y=0
                        dialog.area_surface.fill(dialog.bg_color)  # clear the text area
                        dialog.dirty = 1
                        dialog.wait_for_input=False
            else:      
               if self.unable_inputs:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            dialog.send_text(self.text)
                            dialog.player_answered = True
                            self.text = ''
                            self.has_input = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.text = self.text[:-1]
                            if self.text == '':
                                self.has_input = False
                        else:
                            self.text += event.unicode
                            self.has_input = True
                        # Call a new function here to get the display text
                        display_text = self.get_display_text()
                        self.txt_surface = self.font.render(display_text, True, self.color)

        # New function to get the text that fits the screen
    def get_display_text(self):
        text_width, _ = self.font.size(self.text)
        if text_width > self.rect.w:
            for i in range(len(self.text), 0, -1):
                substring = self.text[-i:]
                substring_width, _ = self.font.size(substring)
                if substring_width <= self.rect.w:
                    return substring
        return self.text
    
    def draw(self, screen):
        # Blit the background color
        screen.blit(self.bg_surface, (self.rect.x, self.rect.y))
        # Draw the rectangle
        pygame.draw.rect(screen, self.color, self.rect, 2)
        # Blit the text
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
