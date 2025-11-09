import pygame
import random
import math
from perlin_noise import PerlinNoise

WIDTH, HEIGHT = 800,600
PLANET_RADIUS = 120
PIXEL_SIZE = 4

pygame.init()
window = pygame.display.set_mode((WIDTH,HEIGHT))
screen = pygame.Surface((WIDTH,HEIGHT))

def draw_gradient_bg(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top_color[0]*(1-t) + bottom_color[0]*t)
        g = int(top_color[1]*(1-t) + bottom_color[1]*t)
        b = int(top_color[2]*(1-t) + bottom_color[2]*t)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def planet_color_gradient(base_color, bands):
    r, g, b = base_color
    step = 30
    return [
        (max(0, min(255, r - step*i)),
         max(0, min(255, g - step*i)),
         max(0, min(255, b - step*i)))
        for i in range(bands)
    ]

def draw_planet(surface, cx,cy,radius,palette, levels=6, noise=None):
    for y in range(-radius,radius):
        for x in range(-radius,radius):
            if x*x + y*y <= radius*radius:
                nx,ny = (cx+x)/WIDTH,(cy+y)/HEIGHT
                band = int(((x*x+y*y)**0.5/radius) * (levels-1))
                n_val = 0
                if noise:
                    n_raw = noise([nx*3,ny*3])
                    n_val = int(((n_raw+1)/2)*2)
                idx = min(levels-1,max(0,band + n_val))
                surface.fill(palette[idx], ((cx+x,cy+y,PIXEL_SIZE,PIXEL_SIZE)))

def draw_stars(surface, star_density=0.002,colors=None):
    if colors is None:
        colors = [(255,255,255),(220,210,180)]
    total_stars = int(WIDTH*HEIGHT*star_density)
    for _ in range(total_stars):
        x,y = random.randint(0, WIDTH-1), random.randint(0,HEIGHT-1)
        color = random.choice(colors)
        surface.set_at((x,y),color) 

def draw_wallpaper():
    top_color = tuple(random.randint(10,80) for _ in range(3))
    bottom_color = tuple(random.randint(70,180) for _ in range(3))
    draw_gradient_bg(screen, top_color,bottom_color)
    draw_stars(screen,star_density=0.002)
    planet_base_color = tuple(random.randint(100,230) for _ in range(3))
    planet_palette = planet_color_gradient(planet_base_color,6)
    planet_noise = PerlinNoise(octaves=4)
    pcx, pcy = WIDTH//2 + random.randint(-100,100), HEIGHT//2+ random.randint(-50,50)
    draw_planet(screen, pcx, pcy, PLANET_RADIUS, planet_palette, levels=len(planet_palette), noise=planet_noise)

draw_wallpaper()
window.blit(screen,(0,0))
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                pygame.image.save(screen,"space_wallpaper.png")
pygame.quit()