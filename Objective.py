import pygame
from support import *

class TextObject:
    def __init__(self, text, font, color, pos, timer, background_image):
        self.text = text
        self.font = pygame.font.Font(font, 20)
        self.color = color
        self.pos = pos
        self.timer = timer
        self.animation_playing = False
        self.animation_finished = False

        # graphics setup
        self.import_player_assets()
        self.status = 'Idle'
        self.frame_index = 0
        self.animation_speed = 0.40
        

        self.text_surfaces = self.split_text_into_lines()

    def split_text_into_lines(self):
        lines = []
        words = [word.split(' ') for word in self.text.splitlines()]
        space = self.font.size(' ')[0]  # The width of a space.
        for line in words:
            if not line:
                continue  # If the line is blank, skip it.
            # Create a new line of text
            text_line = []
            for word in line:
                word_surface = self.font.render(word, True, self.color)
                word_width, word_height = word_surface.get_size()
                # If the line of text will be too wide with this word added, finish this line and start a new one.
                if sum(width for _, width, _ in text_line) + len(text_line) * space + word_width > self.get_width() - 40:
                    lines.append(text_line)
                    text_line = [(word_surface, word_width, word_height)]
                # Add the word to the current line
                else:
                    text_line.append((word_surface, word_width, word_height))
            # Finish the last line of text
            if text_line:
                lines.append(text_line)
        return lines

    def draw(self, screen):
        # Draw the background
        animation = self.animations[self.status]
        self.image = animation[int(self.frame_index)]
        screen.blit(self.image, self.pos)

        # Draw the text if the status is Idle
        if self.status == 'Idle':
            y = self.pos[1] + 40
            for line in self.text_surfaces:
                x = self.pos[0] + 40
                for word_surface, word_width, _ in line:
                    screen.blit(word_surface, (x, y))
                    x += word_width + self.font.size(' ')[0]
                y += self.font.get_linesize()

    def update(self):
        if self.timer.active:
            self.timer.update()
        else:
            if not self.animation_playing:
                self.status = 'Close'
                self.animation_playing = True
            else:
                self.animate()

    def import_player_assets(self):
        character_path = 'graphics/UI/Objective/7 Dialogue Box/'
        self.animations = {'Idle': [], 'Close': [], }

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        
        if self.frame_index >= len(animation):
            self.frame_index = len(animation) - 1
            if self.status == "Close":
                self.animation_finished = True

    def get_width(self):
        return self.animations[self.status][0].get_width()

    def get_height(self):
        return self.animations[self.status][0].get_height()
