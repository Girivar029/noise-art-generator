import pygame
import random
import math
from perlin_noise import PerlinNoise

WIDTH, HEIGHT = 900, 680
PLANET_RADIUS = 130
PIXEL_SIZE = 3

pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
screen = pygame.Surface((WIDTH, HEIGHT))

def lerp(a, b, t):
    return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))

def rand_space_gradient():
    top = tuple(random.randint(10,60) for _ in range(3))
    bottom = tuple(random.randint(70,140) for _ in range(3))
    return top, bottom

def draw_gradient_bg(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = lerp(top_color, bottom_color, t)
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))

def background_noise_overlay(surface, intensity=17):
    noise = PerlinNoise(octaves=3)
    for y in range(0, HEIGHT, PIXEL_SIZE):
        for x in range(0, WIDTH, PIXEL_SIZE):
            val = (noise([x/WIDTH, y/HEIGHT])+1)/2
            bright = min(255, max(0, int(val*intensity)))
            col = (bright, bright, bright)
            surface.fill(col, ((x, y, PIXEL_SIZE, PIXEL_SIZE)))

def scatter_stars(surface, count, color_palette):
    for _ in range(count):
        x, y = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
        color = random.choice(color_palette)
        surface.set_at((x, y), color)
        if random.random()<0.14:
            # Small cluster
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                if 0<=x+dx<WIDTH and 0<=y+dy<HEIGHT:
                    surface.set_at((x+dx, y+dy), color)

def cluster_star_bursts(surface, clusters, stars_per=15):
    colors = [(255,255,255), (255,240,180), (210,190,255)]
    for _ in range(clusters):
        cx = random.randint(60, WIDTH-60)
        cy = random.randint(40, HEIGHT-40)
        for _ in range(stars_per):
            angle = random.uniform(0, 2*math.pi)
            dist = random.randint(0, 22)
            x = int(cx + math.cos(angle)*dist)
            y = int(cy + math.sin(angle)*dist)
            col = random.choice(colors)
            if 0<=x<WIDTH and 0<=y<HEIGHT:
                surface.set_at((x, y), col)
                if random.random() < 0.14:
                    surface.set_at((x+1, y), col)

def planet_palette_gradient(base_color, bands, highlight=40):
    r, g, b = base_color
    cols = []
    for i in range(bands):
        step = highlight*i
        cols.append( ( max(0, min(255, r-step)),
                       max(0, min(255, g-step)),
                       max(0, min(255, b-step)) ) )
    return cols

def draw_textured_planet(surface, cx, cy, radius, palette, noise, bands):
    for y in range(-radius, radius):
        for x in range(-radius, radius):
            if x*x + y*y <= radius*radius:
                nx = (cx + x)/WIDTH
                ny = (cy + y)/HEIGHT
                n_raw = noise([nx*3, ny*3])
                radial = math.sqrt(x*x + y*y)/radius
                value = 0.6*radial + 0.4*((n_raw+1)/2)
                idx = int(value * (bands-1))
                color = palette[max(0,min(bands-1,idx))]
                screen.fill(color, ((cx+x, cy+y, PIXEL_SIZE, PIXEL_SIZE)))
                # Rim highlight
                if abs(radial-1)<0.05:
                    screen.fill((255,255,255), ((cx+x, cy+y, PIXEL_SIZE, PIXEL_SIZE)))
                # Crater (noise threshold)
                if n_raw < -0.3 and radial < 0.88:
                    screen.fill((40,44,55), ((cx+x, cy+y, PIXEL_SIZE, PIXEL_SIZE)))
                # Light spots
                if n_raw > 0.45 and radial < 0.73:
                    screen.fill((230,230,255), ((cx+x, cy+y, PIXEL_SIZE, PIXEL_SIZE)))

def rim_lighting(surface, cx, cy, radius, color, thickness):
    for t in range(thickness):
        for deg in range(0, 360, 1):
            rad = radius + t
            x = int(cx + rad*math.cos(deg*math.pi/180))
            y = int(cy + rad*math.sin(deg*math.pi/180))
            if 0<=x<WIDTH and 0<=y<HEIGHT:
                surface.set_at((x,y), color)

def draw_planet_shadow(surface, cx, cy, radius, offset=(30,16)):
    shadow = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for y in range(radius*2):
        for x in range(radius*2):
            dx, dy = x-radius-offset[0], y-radius+offset[1]
            dist = math.sqrt(dx*dx+dy*dy)
            if dist < radius:
                alpha = int(60 * (1-dist/radius))
                shadow.set_at((x,y), (10,10,20,alpha))
    surface.blit(shadow, (cx-radius, cy-radius))

def draw_pixel_moons(surface, cx, cy, count, max_r, parent_r, noise, base_palette):
    for i in range(count):
        angle = random.uniform(-math.pi/4, math.pi/4)
        dist = parent_r + 38 + random.randint(0, 36)
        mx = int(cx + math.cos(angle)*dist)
        my = int(cy + math.sin(angle)*dist)
        moon_r = random.randint(14, max_r)
        moon_col = [lerp(base_palette, (200,200,220), i/count) for i in range(random.randint(2,4))]
        draw_textured_planet(surface, mx, my, moon_r, moon_col, noise, len(moon_col))
        rim_lighting(surface, mx, my, moon_r, (230,230,240), 2)

def draw_craters(surface, cx, cy, radius, count):
    for _ in range(count):
        angle = random.uniform(0, 2*math.pi)
        dist = random.uniform(radius*0.19, radius*0.89)
        crater_r = random.randint(8,15)
        crater_color = (60,60,64)
        crater_cx = int(cx + math.cos(angle)*dist)
        crater_cy = int(cy + math.sin(angle)*dist)
        for y in range(-crater_r, crater_r):
            for x in range(-crater_r, crater_r):
                if x*x + y*y <= crater_r**2:
                    px, py = crater_cx + x, crater_cy + y
                    if 0<=px<WIDTH and 0<=py<HEIGHT:
                        surface.set_at((px, py), crater_color)

def draw_nebula_overlay(surface, color1, color2, alpha=95):
    nebula = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    noise = PerlinNoise(octaves=5)
    for y in range(0, HEIGHT, PIXEL_SIZE*3):
        for x in range(0, WIDTH, PIXEL_SIZE*3):
            nval = (noise([x/WIDTH, y/HEIGHT])+1)/2
            color = lerp(color1, color2, nval)
            nebula.fill((*color,alpha), ((x, y, PIXEL_SIZE*3, PIXEL_SIZE*3)))
    surface.blit(nebula,(0,0))

def draw_highlights(surface, cx, cy, radius, highlight_color):
    for deg in range(70,112):
        rad = radius
        x = int(cx + rad*math.cos(deg*math.pi/180))
        y = int(cy + rad*math.sin(deg*math.pi/180))
        for t in range(3):
            if 0<=x+t<WIDTH and 0<=y+t<HEIGHT:
                surface.set_at((x+t, y+t), highlight_color)

def draw_planet():
    top_color, bottom_color = rand_space_gradient()
    draw_gradient_bg(screen, top_color, bottom_color)
    background_noise_overlay(screen, intensity=random.randint(8,19))
    scatter_stars(screen, random.randint(400,540), [(255,255,255),(245,220,200),(220,210,250)])
    cluster_star_bursts(screen, clusters=random.randint(7,12))
    draw_nebula_overlay(screen, lerp(top_color, (128,130,176), 0.5), lerp(bottom_color, (72,72,90), 0.6), alpha=60)

    planet_base = tuple(random.randint(85,155) for _ in range(3))
    planet_palette = planet_palette_gradient(planet_base, bands=11, highlight=19)
    planet_noise = PerlinNoise(octaves=4)
    pcx = WIDTH//2 + random.randint(-80,80)
    pcy = HEIGHT//2 + random.randint(-30,40)
    draw_textured_planet(screen, pcx, pcy, PLANET_RADIUS, planet_palette, planet_noise, bands=len(planet_palette))
    rim_lighting(screen, pcx, pcy, PLANET_RADIUS, lerp(planet_palette[-1], (230,230,240), 0.7), 4)
    draw_planet_shadow(screen, pcx, pcy, PLANET_RADIUS)
    draw_craters(screen, pcx, pcy, PLANET_RADIUS, count=random.randint(12,18))
    draw_highlights(screen, pcx, pcy, PLANET_RADIUS, (250,250,240))
    moon_noise = PerlinNoise(octaves=3)
    draw_pixel_moons(screen, pcx, pcy, count=random.randint(2,4), max_r=28, parent_r=PLANET_RADIUS, noise=moon_noise, base_palette=planet_base)

draw_planet()
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
