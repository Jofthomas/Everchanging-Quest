import pygame
import os
from os import walk

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 750, 600
FPS = 60
# Frame delay to make the animation slower
FRAME_DELAY = 5
# Delay before starting the animation (in frames)
START_DELAY = FPS * 2  # Delay for 2 seconds

# Set up the display
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

def import_folder(path):
    surface_list = []
    
    for _,__,img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            
            # Get the original image size
            original_size = image_surf.get_size()
            
            # Calculate the new size with scaling factor of 1.3
            new_size = (int(original_size[0]*3), int(original_size[1]*3))
            
            # Scale the image
            image_surf = pygame.transform.scale(image_surf, new_size)
            
            surface_list.append(image_surf)

    return surface_list


# Load the images
base_image = pygame.image.load('graphics/UI/Menu/Menu.png')
Title_image=pygame.image.load('graphics/UI/Menu/Title.png')
# Load the images
play_image = pygame.image.load('graphics/UI/Menu/Play col_Button.png')
pause_image= pygame.image.load('graphics/UI/Menu/Exit  col_Button.png')
animation_images = import_folder('graphics/UI/Menu/Portal')
# Get the original image sizes
original_play_size = play_image.get_size()
original_pause_size = pause_image.get_size()

# Calculate the new sizes with scaling factor of 1/6
new_play_size = (int(original_play_size[0]/4), int(original_play_size[1]/4))
new_pause_size = (int(original_pause_size[0]/4), int(original_pause_size[1]/4))

# Scale the images
play_image = pygame.transform.scale(play_image, new_play_size)
pause_image = pygame.transform.scale(pause_image, new_pause_size)

def main():
    clock = pygame.time.Clock()

    # Current frame of the animation
    current_frame = 0
    
    # Define the position of the title
    title_x, title_y = 100, 50
        # Define button positions
    play_button_rect = play_image.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    pause_button_rect = pause_image.get_rect(center=(WIDTH / 2, HEIGHT / 2 + play_button_rect.height +30))


    # Game loop
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Draw the base image
        WINDOW.blit(base_image, (0, 0))

        # Draw the animation image at the specific coordinates
        WINDOW.blit(animation_images[current_frame], (20, -10))

        # Draw the title image on top
        WINDOW.blit(Title_image, (title_x, title_y))
        
        # Draw the buttons
        WINDOW.blit(play_image, play_button_rect)
        WINDOW.blit(pause_image, pause_button_rect)

        # Update the current frame
        current_frame = (current_frame + 1) % len(animation_images)
        
        # Update the display
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()



