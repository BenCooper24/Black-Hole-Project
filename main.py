# main.py

# Import necessary modules
import pygame
from camera import Camera

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Black Hole Simulation")

# Set up clock for controlling frame rate
clock = pygame.time.Clock()
camera = Camera()

running = True
while running:

    # Delta time in seconds
    dt = clock.tick(60) / 1000  

    # Event handling and game exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        camera.handle_event(event)

    camera.update(dt)

    # Delta time in seconds
    screen.fill((0, 0, 0))

    # Draw the black hole disk
    camera.draw_disk(screen, WIDTH, HEIGHT) 
    
    # Draw camera information
    camera.draw(screen, WIDTH, HEIGHT)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()

    
