import pygame
import random
import math
from perlin_noise import PerlinNoise

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel-Art Space Scene")

def draw_planet(surface, cx, cy, r, palette):
    for y in range(-r, r):
        for x in range(-r, r):
            if x*x + y*y <= r*r:
                px = cx + x
                py = cy + y
                shade = int(255 * (1 - math.sqrt(x*x+y*y)/r))
                color = palette[shade//64]
                surface.set_at((px, py), color)

def draw_bg_gradient(surface, palette):
    for y in range(HEIGHT):
        t = y / HEIGHT
        idx = int(t * (len(palette)-1))
        rect = pygame.Rect(0, y, WIDTH, 1)
        pygame.draw.rect(surface, palette[idx], rect)

def scatter_stars(surface, n, color):
    for _ in range(n):
        x = random.randint(0, WIDTH-1)
        y = random.randint(0, HEIGHT-1)
        surface.set_at((x, y), color)

def draw_nebula(surface, cx, cy, r, palette, noise, alpha=90):
    cloud = pygame.Surface((r*2,r*2), pygame.SRCALPHA)
    for y in range(r*2):
        for x in range(r*2):
            dx = x - r
            dy = y - r
            dist = math.sqrt(dx*dx+dy*dy)
            if dist < r:
                nval = noise([(cx+dx)/WIDTH, (cy+dy)/HEIGHT])
                idx = int(((nval+1)/2) * (len(palette)-1))
                cloud.set_at((x,y), (*palette[idx], alpha))
    surface.blit(cloud, (cx-r, cy-r))

bg_palette = [(10,28,48), (30,36,80), (44,17,80), (12,12,48)]
planet_palette = [(180,87,68), (220,133,106), (199,199,180), (246,190,135)]
nebula_palette = [(20,45,99),(47,150,255),(155,80,255),(255,150,255)]

noise = PerlinNoise(octaves=3)
draw_bg_gradient(screen, bg_palette)
draw_planet(screen, 430, 340, 85, planet_palette)
draw_planet(screen, 190, 170, 38, planet_palette[::-1])
scatter_stars(screen, 460, (255,255,255))
draw_nebula(screen, 400, 260, 116, nebula_palette, noise, 120)

pygame.image.save(screen, "space_final.png")
pygame.display.flip()
pygame.time.wait(5000)
pygame.quit()
