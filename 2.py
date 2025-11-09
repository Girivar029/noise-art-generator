import pygame
import random
import math
from perlin_noise import PerlinNoise

WIDTH, HEIGHT = 1200, 900
BLOCK_SIZE = 10
LOW_W, LOW_H = WIDTH//BLOCK_SIZE, HEIGHT//BLOCK_SIZE
window = pygame.display.set_mode((WIDTH, HEIGHT))


def random_palette(count, vibrance=0.5):
    return [tuple(int(vibrance*random.randint(128,255)+(1-vibrance)*random.randint(0,100)) for _ in range(3)) for _ in range(count)]

def upscale_px(surf):
    return pygame.transform.scale(surf, (WIDTH, HEIGHT))

def random_safe_planet_positions(n, low_w, low_h, min_r, max_r):
    poses = []
    for _ in range(n):
        valid = False
        attempts = 0
        while not valid and attempts<40:
            r = random.randint(min_r, max_r)
            cx = random.randint(r+4, low_w-r-4)
            cy = random.randint(r+4, low_h-r-4)
            valid = all(math.hypot(cx-x, cy-y)>r2+r+12 for (x, y, r2) in poses)
            attempts += 1
        poses.append((cx, cy, r))
    return poses

def draw_px_planet(surf, cx, cy, r, palette, noise, bands):
    for y in range(-r, r):
        for x in range(-r, r):
            if x*x + y*y <= r*r:
                rx, ry = cx+x, cy+y
                if 0<=rx<LOW_W and 0<=ry<LOW_H:
                    norm = math.sqrt(x*x+y*y)/r
                    nval = noise([rx/LOW_W, ry/LOW_H])
                    idx = int(((0.45*norm+0.55*((nval+1)/2)))*bands)
                    idx = min(bands-1, max(0, idx))
                    surf.set_at((rx, ry), palette[idx])
                    if abs(norm-1)<0.07:
                        surf.set_at((rx, ry), (255,255,255))
                    if nval< -0.2 and norm<0.85:
                        surf.set_at((rx, ry), (52,52,52))
                    if nval>0.7 and norm<0.7:
                        surf.set_at((rx, ry), (230,230,255))
                    if random.random()<0.003 and abs(norm-0.55)<0.24:
                        surf.set_at((rx,ry), (180,90,10))

def draw_px_moons(surf, planet_x, planet_y, planet_r, count, min_r, max_r, palette, noise):
    moon_positions = set()
    for _ in range(count):
        r = random.randint(min_r, max_r)
        angle = random.uniform(0,2*math.pi)
        dist = planet_r + r + random.randint(8,18)
        mx = int(planet_x + math.cos(angle)*dist)
        my = int(planet_y + math.sin(angle)*dist)
        moon_positions.add((mx,my,r))
        moon_col = [tuple(min(255,max(0,c+random.randint(-40,40))) for c in palette[random.randint(0,len(palette)-1)]) for _ in range(random.randint(2,4))]
        moon_noise = PerlinNoise(octaves=random.randint(2,3))
        draw_px_planet(surf, mx, my, r, moon_col, moon_noise, len(moon_col))

def draw_px_gradient_bg(surf, top, bottom):
    for y in range(LOW_H):
        t = y / LOW_H
        tc = tuple(int(top[i]*(1-t)+bottom[i]*t) for i in range(3))
        for x in range(LOW_W):
            surf.set_at((x,y), tc)

def draw_px_stars(surf, density, palette):
    ct = int(density * LOW_W * LOW_H)
    for _ in range(ct):
        x,y = random.randint(0,LOW_W-1), random.randint(0,LOW_H-1)
        surf.set_at((x,y), random.choice(palette))
        if random.random()<0.09:
            for dx,dy in [(1,0),(0,1),(-1,0),(0,-1)]:
                if 0<=x+dx<LOW_W and 0<=y+dy<LOW_H:
                    surf.set_at((x+dx,y+dy), random.choice(palette))
        if random.random()<0.01:
            r = random.randint(1,3)
            for xx in range(-r,r+1):
                for yy in range(-r,r+1):
                    if 0<=x+xx<LOW_W and 0<=y+yy<LOW_H:
                        surf.set_at((x+xx,y+yy), (255,255,255))

def draw_px_nebula(surf, palette, octaves=4, alpha=0.52):
    noise = PerlinNoise(octaves=octaves)
    for y in range(LOW_H):
        for x in range(LOW_W):
            val = (noise([x/LOW_W, y/LOW_H])+1)/2
            if val>0.62:
                idx = int(val*(len(palette)-1))
                neb = tuple(int((1-alpha)*surf.get_at((x,y))[i]+alpha*palette[idx][i]) for i in range(3))
                surf.set_at((x,y), neb)
            if random.random()<0.001 and val>0.66 and x%3==0 and y%3==0:
                surf.set_at((x,y), (220,130,255))

def draw_px_rings(surf, cx, cy, r, palette, rings=3, fade=22):
    for ring in range(rings):
        cr = r + ring*random.randint(7,11)
        col = tuple(min(255,max(0,palette[-1][i]-(fade*ring))) for i in range(3))
        for theta in range(0,360,1):
            x = int(cx + cr*math.cos(math.radians(theta)))
            y = int(cy + cr*math.sin(math.radians(theta)))
            if 0<=x<LOW_W and 0<=y<LOW_H:
                surf.set_at((x,y), col)
                if random.random()<0.11 and 0<=x+1<LOW_W and 0<=y+1<LOW_H:
                    surf.set_at((x+1,y+1), col)

def draw_px_craters(surf, cx, cy, r, min_r, max_r, count):
    for _ in range(count):
        angle = random.uniform(0,2*math.pi)
        dist = random.uniform(r*0.15, r*0.88)
        cr = random.randint(min_r,max_r)
        crater_cx = int(cx + math.cos(angle)*dist)
        crater_cy = int(cy + math.sin(angle)*dist)
        for y in range(-cr, cr):
            for x in range(-cr, cr):
                if x*x + y*y <= cr*cr:
                    px, py = crater_cx + x, crater_cy + y
                    if 0<=px<LOW_W and 0<=py<LOW_H:
                        surf.set_at((px, py), (50,46,32))

def draw_px_shadow(surf, cx, cy, r, shade=(0,0,0), alpha=0.34):
    for y in range(-r, r):
        for x in range(-r, r):
            if x*x + y*y <= r*r and x>0:
                rx, ry = cx+x, cy+y
                if 0<=rx<LOW_W and 0<=ry<LOW_H:
                    col = surf.get_at((rx,ry))
                    shad = tuple(int(col[i]*(1-alpha)+shade[i]*alpha) for i in range(3))
                    surf.set_at((rx,ry), shad)

def draw_cluster_nebula(surf, clusters, palette, max_size=38):
    for _ in range(clusters):
        cx = random.randint(40,LOW_W-40)
        cy = random.randint(30,LOW_H-30)
        size = random.randint(int(max_size*0.6),max_size)
        color = random.choice(palette)
        for y in range(-size,size):
            for x in range(-size,size):
                dist = math.sqrt(x*x+y*y)
                if dist<size and random.random()<0.77*(1-dist/size):
                    px, py = cx+x, cy+y
                    if 0<=px<LOW_W and 0<=py<LOW_H:
                        surf.set_at((px,py), color)

def draw_px_highlight(surf, cx, cy, r, highlight_col=(254,254,200)):
    for theta in range(70,110,1):
        dx = int(r*math.cos(math.radians(theta)))
        dy = int(r*math.sin(math.radians(theta)))
        for t in range(2,7):
            x = cx+dx//t
            y = cy+dy//t
            if 0<=x<LOW_W and 0<=y<LOW_H:
                surf.set_at((x,y), highlight_col)

pygame.init()
low = pygame.Surface((LOW_W, LOW_H))

def make_wallpaper():
    top_col = random_palette(1,0.6)[0]
    bot_col = random_palette(1,0.58)[0]
    draw_px_gradient_bg(low, top_col, bot_col)
    draw_px_stars(low, density=0.002, palette=[(255,255,255),(220,230,250),(120,170,255)])
    draw_px_nebula(low, random_palette(6,0.85), octaves=random.randint(2,4), alpha=random.uniform(0.55,0.66))
    draw_cluster_nebula(low, clusters=random.randint(6,10), palette=random_palette(3,0.65), max_size=random.randint(19,49))
    planet_pals = [random_palette(random.randint(4,8),0.88) for _ in range(random.randint(2,4))]
    positions = random_safe_planet_positions(len(planet_pals), LOW_W, LOW_H, 15, 30)
    noises = [PerlinNoise(octaves=random.randint(3,5)) for _ in planet_pals]
    for idx, (cx,cy,r) in enumerate(positions):
        draw_px_planet(low, cx, cy, r, planet_pals[idx], noises[idx], len(planet_pals[idx]))
        draw_px_shadow(low,cx,cy,r,shade=(0,0,0),alpha=random.uniform(0.18,0.42))
        draw_px_rings(low,cx,cy, r, planet_pals[idx], rings=random.randint(1,3), fade=random.randint(8,24))
        draw_px_craters(low,cx,cy,r,2,7,random.randint(7,17))
        draw_px_highlight(low,cx,cy,r,highlight_col=random.choice(planet_pals[idx]))
        moons_pal = random_palette(random.randint(2,5),0.81)
        moons_noise = PerlinNoise(octaves=random.randint(2,4))
        draw_px_moons(low, cx, cy, r, random.randint(1,3), 4,12, moons_pal, moons_noise)

make_wallpaper()
ups = upscale_px(low)
window.blit(ups,(0,0))
pygame.display.flip()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                pygame.image.save(ups,"space_wallpaper.png")
pygame.quit()
