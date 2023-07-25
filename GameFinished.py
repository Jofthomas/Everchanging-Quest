import pygame
import os
from os import walk
import sys

# Set up some constants
WIDTH, HEIGHT = 750, 600
FPS = 60
# Frame delay to make the animation slower
FRAME_DELAY = 5
# Delay before starting the animation (in frames)
START_DELAY = FPS * 2  # Delay for 2 seconds

# Function to import images from a folder
def import_folder(path):
    surface_list = []
    
    for _,__,img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            
            # Get the original image size
            original_size = image_surf.get_size()
            
            # Calculate the new size
            new_size = (original_size[0]*2, original_size[1]*2)
            
            # Scale the image
            image_surf = pygame.transform.scale(image_surf, new_size)
            
            surface_list.append(image_surf)

    return surface_list



def game_won_screen(WINDOW,event,music):
    clock = pygame.time.Clock()
    # Current frame of the animation
    current_frame = 0
    # Counter for the animation plays
    animation_plays = 0
    # Frame counter to delay the animation
    frame_counter = 0
    # Counter for the start delay
    start_delay = START_DELAY
    # Load the images
    base_image = pygame.image.load('graphics/UI/Win/Win.png')
    animation_images = import_folder('graphics/UI/Win/Win')
    running = True
    music.play()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Clear the screen by filling it with black color
        WINDOW.fill((0, 0, 0))
        
        # Draw the base image
        WINDOW.blit(base_image, (0, 0))
        
        # If the start delay has finished
        if start_delay <= 0:
            # If the animation has played less than twice, draw the animation image at the specific coordinates
            if animation_plays < 2:
                WINDOW.blit(animation_images[current_frame], (330, 440))

                # Only increment the current frame and frame counter every FRAME_DELAY frames
                if frame_counter % FRAME_DELAY == 0:
                    current_frame += 1

                    # If we've gone past the last frame of the animation
                    if current_frame >= len(animation_images):
                        current_frame = len(animation_images) - 1  # Keep the last frame active
                        animation_plays += 1

                frame_counter += 1

            else:
                # After the animation has played twice, keep displaying the last frame
                WINDOW.blit(animation_images[current_frame], (330, 440))
        
        else:
            # Display the first frame of the animation during the delay
            WINDOW.blit(animation_images[0], (330, 440))
            # Decrement the start delay counter
            start_delay -= 1

        # Update the display
        pygame.display.update()
        # Control the frame rate
        clock.tick(FPS)
    
     # Once the loop is over, it's time to quit pygame
    music.stop()
    pygame.quit()


