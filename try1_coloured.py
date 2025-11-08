import pygame
import random

# Initialize Pygame
pygame.init()

# Canvas dimensions
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Colored Noise Map - Iteration 2")

# Function to generate a random grayscale noise map as a 2D array
def generate_noise_map_array(width, height):
    noise = []
    for x in range(width):
        column = []
        for y in range(height):
            gray_value = random.randint(0, 255)
            column.append(gray_value)
        noise.append(column)
    return noise

# Function to color the noise map with random hues, preserving brightness (grayscale value)
def color_noise_map(noise_map):
    colored_surface = pygame.Surface((WIDTH, HEIGHT))
    for x in range(WIDTH):
        for y in range(HEIGHT):
            brightness = noise_map[x][y]
            
            # Random hue with the brightness as the value (HSV to RGB)
            hue = random.randint(0, 360)
            color = pygame.Color(0)
            color.hsva = (hue, 100, brightness * 100 / 255, 100)
            
            colored_surface.set_at((x, y), color)
    return colored_surface

# Generate noise array once at start
noise_array = generate_noise_map_array(WIDTH, HEIGHT)
colored_noise_map = color_noise_map(noise_array)

# Main loop
running = True
while running:
    screen.fill((0, 0, 0))  # Clear screen with black
    screen.blit(colored_noise_map, (0, 0))  # Draw colored noise map
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    pygame.display.flip()  # Update display

pygame.quit()
