import pygame
import random
import math
from perlin_noise import PerlinNoise

WIDTH, HEIGHT = 800, 600
PLANET_RADIUS = 120
PIXEL_SIZE = 4

pygame.init()
screen = pygame.Surface((WIDTH, HEIGHT))

def random_palette(n=4):
    return [tuple(random.randint(80, 230) for _ in range(3)) for _ in range(n)]

def draw_stars(surface, star_density=0.002, colors=None):
    if colors is None:
        colors = [(255,255,255), (220,210,180)]
    total_stars = int(WIDTH*HEIGHT*star_density)
    for _ in range(total_stars):
        x, y = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
        color = random.choice(colors)
        surface.set_at((x, y), color)

def draw_planet(surface, cx, cy, radius, palette, levels=6, noise=None):
    for y in range(-radius, radius):
        for x in range(-radius, radius):
            if x*x + y*y <= radius*radius:
                nx, ny = (cx + x)/WIDTH, (cy + y)/HEIGHT
                shade = palette[int(((x*x + y*y)**0.5 / radius) * (levels-1))]
                n_val = 0
                if noise:
                    # Mix noise into band selection for pixel-art texture
                    n_raw = noise([nx*3, ny*3])
                    n_val = int(((n_raw+1)/2) * (levels-1))
                idx = min(levels-1, max(0, int((((x*x + y*y)**0.5 / radius) * (levels-1) + n_val)//2)))
                screen.fill(palette[idx], ((cx+x, cy+y, PIXEL_SIZE, PIXEL_SIZE)))

def pixel_quantize(palette, value, levels):
    step = 255 // levels
    v = min(255, max(0, value))
    idx = v // step
    return palette[min(levels-1, idx)]

def draw_background(surface, vertical_bands=6, palette=None):
    if palette is None:
        palette = random_palette(vertical_bands)
    band_height = HEIGHT // vertical_bands
    for i in range(vertical_bands):
        rect = pygame.Rect(0, i*band_height, WIDTH, band_height)
        surface.fill(palette[i], rect)

def draw_moons(surface, planet_cx, planet_cy, planet_r, palette, noise=None):
    moon_count = random.randint(2,5)
    for i in range(moon_count):
        angle = random.uniform(-math.pi/2, math.pi/2)
        dist = planet_r + random.randint(45, 110)
        moon_r = random.randint(18, 36)
        cx = int(planet_cx + math.cos(angle)*dist)
        cy = int(planet_cy + math.sin(angle)*dist)
        levels = len(palette)
        for y in range(-moon_r, moon_r):
            for x in range(-moon_r, moon_r):
                if x*x + y*y <= moon_r*moon_r:
                    nx, ny = (cx + x) / WIDTH, (cy + y) / HEIGHT
                    shade = palette[int(((x*x + y*y)**0.5 / moon_r) * (levels-1))]
                    n_val = 0
                    if noise:
                        n_raw = noise([nx*8, ny*8])
                        n_val = int(((n_raw+1)/2) * (levels-1))
                    idx = min(levels-1, max(0, int((((x*x + y*y)**0.5 / moon_r) * (levels-1) + n_val)//2)))
                    surface.fill(palette[idx], ((cx+x, cy+y, PIXEL_SIZE, PIXEL_SIZE)))

def rim_light(surface, cx, cy, radius, color, thickness):
    for t in range(thickness):
        for theta in range(0,360,int(1.5)):
            r = radius + t
            x = int(cx + r*math.cos(math.radians(theta)))
            y = int(cy + r*math.sin(math.radians(theta)))
            if 0<=x<WIDTH and 0<=y<HEIGHT:
                surface.set_at((x,y), color)

def draw_craters(surface, cx, cy, radius, palette, count=14):
    for _ in range(count):
        angle = random.uniform(0, 2*math.pi)
        dist = random.uniform(radius*0.3, radius*0.93)
        crater_r = random.randint(12,22)
        crater_color = palette[0]
        crater_cx = int(cx + math.cos(angle)*dist)
        crater_cy = int(cy + math.sin(angle)*dist)
        for y in range(-crater_r, crater_r):
            for x in range(-crater_r, crater_r):
                if x*x + y*y <= crater_r**2:
                    px, py = crater_cx + x, crater_cy + y
                    if 0<=px<WIDTH and 0<=py<HEIGHT:
                        surface.set_at((px, py), crater_color)

def nebula_overlay(surface, palette, density=0.001, size=70):
    for _ in range(int(WIDTH*HEIGHT*density)):
        x = random.randint(0, WIDTH-1)
        y = random.randint(0, HEIGHT-1)
        color = random.choice(palette)
        alpha = random.randint(30,100)
        nebula = pygame.Surface((size,size), pygame.SRCALPHA)
        nebula.fill((*color,alpha))
        r = random.randint(18,size//2)
        pygame.draw.circle(nebula, (*color,alpha), (size//2,size//2), r)
        screen.blit(nebula, (x-size//2,y-size//2))

def make_space_scene():
    bg_palette = random_palette(5)
    planet_palette = random_palette(5)
    moon_palette = random_palette(4)
    neb_palette = random_palette(3)
    draw_background(screen,vertical_bands=len(bg_palette),palette=bg_palette)
    draw_stars(screen,star_density=0.002,colors=[(255,255,255),(180,200,250)])
    planet_cx, planet_cy = WIDTH//2 + random.randint(-70,80), HEIGHT//2 + random.randint(-30,40)
    noise = PerlinNoise(octaves=4)
    draw_planet(screen, planet_cx, planet_cy, PLANET_RADIUS, planet_palette, levels=len(planet_palette), noise=noise)
    rim_light(screen,planet_cx,planet_cy,PLANET_RADIUS,random.choice(planet_palette),thickness=5)
    draw_craters(screen,planet_cx,planet_cy,PLANET_RADIUS,planet_palette,count=random.randint(12,18))
    draw_moons(screen,planet_cx,planet_cy,PLANET_RADIUS,moon_palette,noise=noise)
    nebula_overlay(screen,neb_palette)
    pygame.image.save(screen,"pixel_space_wallpaper.png")

def random_rect_palette(n=7):
    return [tuple(random.randint(30, 210) for _ in range(3)) for _ in range(n)]

def draw_horizontal_stripes(surface, bands=6, palette=None):
    if palette is None:
        palette = random_rect_palette(bands)
    band_height = HEIGHT // bands
    for i in range(bands):
        rect = pygame.Rect(0, i*band_height, WIDTH, band_height)
        surface.fill(palette[i], rect)

def generate_noise_grid(w, h, scale, octaves=4):
    noise = PerlinNoise(octaves=octaves)
    grid = []
    for x in range(w):
        row = []
        for y in range(h):
            val = noise([x/scale, y/scale])
            row.append(val)
        grid.append(row)
    return grid

def dither_pixel_art(surface, grid, palette, band_levels):
    rows, cols = len(grid), len(grid[0])
    for x in range(rows):
        for y in range(cols):
            noise_val = grid[x][y]
            idx = int(((noise_val+1)/2) * (band_levels-1))
            rect = pygame.Rect(x*PIXEL_SIZE, y*PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
            pygame.draw.rect(surface, palette[idx], rect)

def draw_planet_dither(surface, cx, cy, radius, palette, bands=8, noise_grid=None):
    for y in range(-radius, radius):
        for x in range(-radius, radius):
            if x*x + y*y < radius*radius:
                rx, ry = cx + x, cy + y
                if 0 <= rx < WIDTH and 0 <= ry < HEIGHT:
                    ridx = int(((x*x + y*y)**0.5 / radius) * (bands-1))
                    nx, ny = (x+radius)//PIXEL_SIZE, (y+radius)//PIXEL_SIZE
                    nidx = ridx
                    if noise_grid:
                        try:
                            nval = noise_grid[nx][ny]
                            offs = int(((nval+1)/2) * (bands-3))
                            nidx = max(0, min(bands-1, (ridx+offs)//2))
                        except:
                            pass
                    col = palette[nidx]
                    surface.fill(col, ((rx, ry, PIXEL_SIZE, PIXEL_SIZE)))

def draw_shadow(surface, cx, cy, radius, intensity, color):
    shadow = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for y in range(radius*2):
        for x in range(radius*2):
            dx, dy = x-radius, y-radius
            dist = math.sqrt(dx*dx+dy*dy)
            if dist < radius:
                alpha = int( intensity * (1-dist/radius) )
                shadow.set_at((x,y), (*color,alpha))
    surface.blit(shadow, (cx-radius, cy-radius))

def random_star_clusters(surface, cluster_count=6, stars_per=23, color_list=None):
    color_list = color_list or [(255,255,255),(255,229,170),(230,210,250),(180,255,230)]
    for _ in range(cluster_count):
        cx = random.randint(80, WIDTH-80)
        cy = random.randint(60, HEIGHT-60)
        for _ in range(stars_per):
            angle = random.uniform(0, 2*math.pi)
            dist = random.randint(0, 38)
            x = int(cx + math.cos(angle)*dist)
            y = int(cy + math.sin(angle)*dist)
            c = random.choice(color_list)
            surface.set_at((x,y), c)

def draw_star_streak(surface, x, y, length, direction, color):
    angle = math.radians(direction)
    for i in range(length):
        px = int(x + i*math.cos(angle))
        py = int(y + i*math.sin(angle))
        if 0<=px<WIDTH and 0<=py<HEIGHT:
            surface.set_at((px, py), color)

def draw_multiple_planets(surface, n, palette, min_r, max_r):
    positions = []
    for _ in range(n):
        r = random.randint(min_r, max_r)
        cx = random.randint(r+20, WIDTH-r-20)
        cy = random.randint(r+20, HEIGHT-r-20)
        positions.append((cx, cy, r))
    for idx, (cx, cy, r) in enumerate(positions):
        band_levels = len(palette)
        grid = generate_noise_grid(r*2//PIXEL_SIZE, r*2//PIXEL_SIZE, scale=r//2, octaves=3)
        draw_planet_dither(surface, cx, cy, r, palette, band_levels, grid)
        if idx % 2 == 0:
            draw_shadow(surface, cx, cy, r, 170, (20,20,30))
        else:
            rim_light(surface, cx, cy, r, palette[-1], 3)
        if r > min_r + 4 and random.random() < 0.5:
            draw_craters(surface, cx, cy, r, palette, count=random.randint(7,14))

def nebula_blobs(surface, palette, count=6):
    for _ in range(count):
        cx = random.randint(50, WIDTH-50)
        cy = random.randint(50, HEIGHT-50)
        r = random.randint(60,180)
        alpha = random.randint(45,150)
        color = random.choice(palette)
        cloud = pygame.Surface((r*2,r*2), pygame.SRCALPHA)
        pygame.draw.circle(cloud, (*color,alpha), (r,r), r)
        surface.blit(cloud, (cx-r, cy-r))

def randomize_scene():
    bg_palette = random_palette(7)
    planet_palette1 = random_palette(5)
    planet_palette2 = random_palette(5)
    moon_palette = random_palette(4)
    nebula_palette = random_palette(3)
    draw_horizontal_stripes(screen, bands=len(bg_palette), palette=bg_palette)
    draw_stars(screen, star_density=0.0018, colors=[(255,255,255),(220,230,210),(190,200,255)])
    random_star_clusters(screen, cluster_count=7, stars_per=16, color_list=[(255,255,255),(255,225,160)])
    nebula_blobs(screen, nebula_palette, count=random.randint(3,7))
    draw_multiple_planets(screen, random.randint(1,3), planet_palette1, min_r=80, max_r=125)
    draw_multiple_planets(screen, random.randint(0,2), planet_palette2, min_r=45, max_r=68)

def seamless_noise_grid(w, h, scale, octaves=5):
    noise = PerlinNoise(octaves=octaves)
    grid = []
    for x in range(w):
        row = []
        for y in range(h):
            sx, sy = x/w, y/h
            val = noise([sx*scale, sy*scale])
            row.append(val)
        grid.append(row)
    return grid

def draw_grid_overlay(surface, grid, palette, opacity=50):
    rows = len(grid)
    cols = len(grid[0])
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for x in range(rows):
        for y in range(cols):
            idx = int(((grid[x][y]+1)/2)*(len(palette)-1))
            rect = pygame.Rect(x*PIXEL_SIZE, y*PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
            overlay.fill((*palette[idx], opacity), rect)
    surface.blit(overlay, (0,0))

def pixelate_art(surface, block_size):
    arr = pygame.surfarray.array3d(surface)
    h, w = arr.shape[:2]
    for x in range(0, w, block_size):
        for y in range(0, h, block_size):
            block = arr[y:y+block_size, x:x+block_size]
            avg = block.mean(axis=(0,1)).astype(int)
            arr[y:y+block_size, x:x+block_size] = avg
    pygame.surfarray.blit_array(surface, arr)

def highlight_edges(surface, cx, cy, r, color, thickness):
    for t in range(thickness):
        for deg in range(0, 360, 1):
            rad = r + t
            x = int(cx + rad*math.cos(deg*math.pi/180))
            y = int(cy + rad*math.sin(deg*math.pi/180))
            if 0<=x<WIDTH and 0<=y<HEIGHT:
                surface.set_at((x,y), color)

def draw_ringed_planet(surface, cx, cy, r, palette, noise_grid):
    draw_planet_dither(surface, cx, cy, r, palette, bands=len(palette), noise_grid=noise_grid)
    for i in range(2):
        angle = random.uniform(0,2*math.pi)
        rx, ry = int(cx+r*0.5*math.cos(angle)), int(cy+r*0.5*math.sin(angle))
        thickness = random.randint(2,5)
        color = random.choice(palette)
        for t in range(thickness):
            for deg in range(0, 360, 1):
                dist = r+28+t
                x = int(cx + dist*math.cos(deg*math.pi/180))
                y = int(cy + dist*math.sin(deg*math.pi/180))
                if 0<=x<WIDTH and 0<=y<HEIGHT:
                    surface.set_at((x,y), color)

def draw_pixel_moons(surface, count, base_palette, noise_grid):
    for i in range(count):
        moon_r = random.randint(22,44)
        cx = random.randint(moon_r+10, WIDTH-moon_r-10)
        cy = random.randint(moon_r+10, HEIGHT-moon_r-10)
        moon_palette = [random.choice(base_palette) for _ in range(random.randint(2,5))]
        draw_planet_dither(surface, cx, cy, moon_r, moon_palette, bands=len(moon_palette), noise_grid=noise_grid)
        if random.random() < 0.7:
            rim_light(surface, cx, cy, moon_r, moon_palette[-1], 2)
        if random.random() < 0.35:
            highlight_edges(surface, cx, cy, moon_r, moon_palette[0], 2)

def main_wallpaper_loop():
    for i in range(3):
        screen.fill((0,0,0))
        randomize_scene()
        p_palette = random_palette(6)
        n_grid = seamless_noise_grid(PLANET_RADIUS*2//PIXEL_SIZE, PLANET_RADIUS*2//PIXEL_SIZE, scale=random.uniform(1.5,2.7))
        draw_ringed_planet(screen, WIDTH//2, HEIGHT//2+random.randint(-40,60), PLANET_RADIUS, p_palette, n_grid)
        moon_n_grid = seamless_noise_grid(44*2//PIXEL_SIZE,44*2//PIXEL_SIZE,random.uniform(1.2,2.2))
        draw_pixel_moons(screen, random.randint(2,5), p_palette, moon_n_grid)
        pixelate_art(screen, block_size=PIXEL_SIZE)
        pygame.image.save(screen,f"space_wallpaper_{i+1}.png")

main_wallpaper_loop()
pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.get_surface().blit(screen,(0,0))
pygame.display.flip()
pygame.time.wait(4000)
pygame.quit()
