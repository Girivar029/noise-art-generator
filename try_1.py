import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600 , 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Generate Noise Map")


def generate_noise_map(width, height):
    noise_surface = pygame.Surface((width, height))
    for x in range(width):
        for y in range(height):
            gray_value = random.randint(0,255)
            noise_surface.set_at((x,y), (gray_value,gray_value,gray_value))
    return noise_surface

noise_map = generate_noise_map(WIDTH, HEIGHT)

running = True
while running:
    screen.fill((0,0,0))
    screen.blit(noise_map,(0,0))

    for event in pygame.event.get():
        if pygame.QUIT == True:
            running = False
    
    pygame.display.flip()

pygame.quit()