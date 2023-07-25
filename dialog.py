# Importing required libraries and modules
import pygame
from settings import *  # Importing all the global variables from settings module
from InputBox import InputBox  # Importing InputBox class

import time
from random import gauss
from collections import deque
# Definition of Dialog class
import threading

# 40 WPM (Words per min)  converted to CPS (chars per second)
CPS_40WPM = 5 * 40 / 60
BASE_DELAY_MS = 1000/CPS_40WPM  # default time between chars in ms for 40 WPM

def _type_delay(word_per_min=40.0):  # set speed as words per minute
    """Returns a random millisecond delay value that is based on a
    normal random curve of a person typing at the
    optional parameter value Words Per Minute
    """

    # Humans max typing record is about 215
    #  Average is 35, To get a job typing, you need 60 to 80 WPM

    speed_factor = 40/word_per_min
    mean = BASE_DELAY_MS * speed_factor   # adjust the mean time

    v = gauss(mean, mean/2)  # random time between chars to normal curve
    return min(max(0.0, v), 3000.0 * speed_factor)  # max delay is 3000 ms


class Dialog:
    # Initialization method for Dialog class
    def __init__(self, npc, text, font, color=(255, 255, 255), bg_color=(0, 0, 0), speed=3,wps=20):
        self.npc = npc  # NPC with which the player interacts
        self.text = """what can I help you with ?"""  # Text for the dialog
        self.font = pygame.font.Font(None, 12)
        self.color = pygame.Color('white')  # Color of the text
        self.bg_color =  pygame.Color('#292929')  # Background color of the dialog box
        self.speed = speed  # Speed at which the dialog text is revealed
        self.display_surface = pygame.display.get_surface()  # Get the current window surface
        self.dialog_image = pygame.image.load("graphics/UI/dialog_background2.png")  # Load the image for dialog box
        self.is_visible = False  # Visibility state of the dialog box
        self.input_box = InputBox(100, 100, 450, 32, font)  # Instance of InputBox class 
        self.text_rendered = False  # State of whether the text has been rendered or not
        self.player_answered=False
        self.char_queue = deque(self.text)  # used for queue of text to display
        self.rect = pygame.display.get_surface()
        self.font = font
        self.fg_color = color
        self.bk_color = bg_color
        self.is_rendering = True
        self.enable_input=True
        self.size =self.dialog_image.get_rect().size
        self.player=None
        # Adjust these values to control the size of the text area within the dialog box
        self.text_area_width_offset = 20  # How much smaller the text area is than the dialog box in width
        self.text_area_height_offset = 20  # How much smaller the text area is than the dialog box in height
        self.wait_for_input = False
        # Create the text area surface
        dialog_size = self.dialog_image.get_rect().size
        text_area_size = (dialog_size[0] - self.text_area_width_offset, dialog_size[1] - self.text_area_height_offset)
        self.area_surface = pygame.Surface(text_area_size, flags=pygame.SRCALPHA)
        self.player_image = pygame.image.load('graphics/UI/Character Portrait Enlarged.png')
        self.mood="Mood : None"
        self.wps = wps
        self.y = 0  # keep track of vertical position of next line of text
        self.y_delta = self.font.size("M")[1]  # get height of line from a char

        self.line = ""  # current string buffer being rendered on line
        self.next_time = time.time()  # trigger time for next action
        self.dirty = 0  # set to signal draw method to copy to screen
        self.is_processing=False

    # Method to draw the dialog box on the surface
        # Method to draw the dialog box on the surface
    def draw(self):
        if self.is_visible :
            
            dialog_image_rect = self.dialog_image.get_rect()  # Get the rect object for the dialog image
            dialog_image_rect.midbottom = self.display_surface.get_rect().midbottom  # Position the dialog image rect at the middle bottom of the display surface
            offset = 50
            dialog_image_rect.y -= offset  # Adjust the vertical position with an offset
            # Calculate the position of the input box within the dialog box
            self.display_surface.blit(self.player_image, (dialog_image_rect.x+30, dialog_image_rect.y-90))
            self.input_box.rect.x = dialog_image_rect.x + (dialog_image_rect.width - self.input_box.rect.width) // 2
            self.input_box.rect.y = dialog_image_rect.y + dialog_image_rect.height
            self.show_mood(self.mood, dialog_image_rect.x+dialog_image_rect.width-150,dialog_image_rect.y -20)
            # Draw the dialog image (background container) first
            self.display_surface.blit(self.dialog_image, dialog_image_rect)
            
            # Draw the input box on the display surface
            self.input_box.draw(self.display_surface)
            pos=(dialog_image_rect.x+10,dialog_image_rect.y+10)
            
           
            # Draw the text surface (self.area_surface) on top of the dialog image
            self.display_surface.blit(self.area_surface, pos)
            self.dirty = 0

            
            
    
    def _render_new_line(self):  # advance down or scroll up on '\n'
        self.y += self.y_delta  # advance position down in area
        self.line = ""  # reset line buffer
        if self.y + self.y_delta > self.size[1]:  # space for new line?
            # Create a new area_surface
            dialog_size = self.dialog_image.get_rect().size
            text_area_size = (dialog_size[0] - self.text_area_width_offset, dialog_size[1] - self.text_area_height_offset)
            self.area_surface = pygame.Surface(text_area_size, flags=pygame.SRCALPHA)
            self.area_surface.fill(self.bg_color)
            self.y = 0  # Reset y position
            self.dirty = 1

            
    def _render_char(self, c):  # render next char
        if self.wait_for_input:
            return
        if c == '\n':
            self._render_new_line()
        else:
            self.line += c  # add new character to line buffer
            temp_text = self.font.render(self.line, True, self.fg_color)
            if self.y + temp_text.get_height() > self.area_surface.get_height():  # space for new line?
                # pause for user input before clearing the text
                self.wait_for_input = True
            else:
                self.area_surface.blit(temp_text, (0, self.y))  # render line
                self.dirty = 1

    def empty_dequeue(self):
        while self.char_queue:
            self.char_queue.pop()
    # Method to send text to the NPC and print the response
    def send_text(self, text):
        if len(self.char_queue) > 0:
        # If there are, then return without doing anything else
            return
            # Clear existing text
        self.input_box.unable_inputs=False
        self.char_queue.clear()
        dialog_size = self.dialog_image.get_rect().size
        text_area_size = (dialog_size[0] - self.text_area_width_offset, dialog_size[1] - self.text_area_height_offset)
        self.area_surface = pygame.Surface(text_area_size, flags=pygame.SRCALPHA)
        self.area_surface.fill(self.bg_color)
        self.y = 0
        self.line = ""

        # Set text to 'Thinking ...'
        self.is_processing = True
        self.text = 'Thinking ...'
        self.char_queue = deque(self.text)
        self.dirty = 1  # Mark the surface as dirty to ensure it gets redrawn

       
        threading.Thread(target=self.get_npc_response_thread, args=(text,)).start()

        

    def get_npc_response_thread(self, text):
        # The method running in the new thread
        
        answer,mood = self.npc.get_npc_response(text)
        self.mood=f'Mood : {mood}'
        self.text = answer
        # Set the processing status to False after the response is received
        self.is_processing = False
        
        # Temporarily stop rendering
        self.is_rendering = False
        
        # Create a new area_surface
        dialog_size = self.dialog_image.get_rect().size
        text_area_size = (dialog_size[0] - self.text_area_width_offset, dialog_size[1] - self.text_area_height_offset)
        self.area_surface = pygame.Surface(text_area_size, flags=pygame.SRCALPHA)
        self.area_surface.fill(self.bg_color)
        # Reset the vertical position of the next line of text
        # Reset char_queue with the new text
        words = self.text.split(' ')
        line = ''
        lines = []
        for word in words:
            test_line = line + word + ' '
            test_line_width = self.font.size(test_line)[0]
            if test_line_width < text_area_size[0]:
                line = test_line
            else:
                lines.append(line)
                line = word + ' '
        lines.append(line)
        self.text = '\n'.join(lines)
        
        self.char_queue = deque(self.text)
        # Mark the surface as dirty to ensure it gets redrawn
        self.dirty = 1
        self.y=0
        self.line=""
        

        # Resume rendering
        self.is_rendering = True
        self.input_box.unable_inputs=True
        
        
    def show_mood(self, mood,x,y):
        text_surf = self.font.render(mood, False, self.fg_color)
      
        text_rect = text_surf.get_rect(topleft=(x, y))

        pygame.draw.rect(self.display_surface, self.bg_color, text_rect.inflate(10, 10))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, self.fg_color, text_rect.inflate(10, 10), 1)

    # Method to handle the input in the dialog box
    def handle_input(self):
        
        keys = pygame.key.get_pressed()  # Get the state of all keyboard buttons
        if keys[pygame.K_ESCAPE]:  # If escape key is pressed
            self.close()  # Close the dialog box
        else:
            self.input_box.handle_event(self)  # Handle the event in the input box

    # Method to close the dialog box
    def close(self):
        self.is_visible = False  # Set visibility of dialog box to False
        self.npc.end_interaction()  # End the interaction with the NPC
        self.text_rendered = False  # Set text as not rendered

    # Method to update the dialog box
    def update(self):
        self.handle_input()  # Handle the input in the dialog box
        if self.is_rendering:
            while self.char_queue and self.next_time <= time.time():
                self._render_char(self.char_queue.popleft())  # render it
                self.next_time += _type_delay(self.wps)/1000.0
            self.next_time = time.time()  # no chars, reset next_time to now
            
