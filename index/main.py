import pygame
import random
import math
from perlin_noise import PerlinNoise
import asyncio

WIDTH, HEIGHT = 1600, 1100
BLOCK_SIZE = 8
LOW_W, LOW_H = WIDTH//BLOCK_SIZE, HEIGHT//BLOCK_SIZE

pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))

def lerp_color(a, b, t):
    return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))

def get_palette(type_name):
    palettes = {
        "red": [
            (32, 5, 8),
            (60, 10, 14),
            (90, 18, 22),
            (120, 24, 27),
            (150, 34, 35),
            (180, 44, 46),
            (210, 58, 63),
        ],
        "purple": [
            (18, 5, 30),
            (32, 10, 50),
            (50, 18, 75),
            (64, 24, 95),
            (85, 35, 120),
            (110, 50, 150),
            (140, 65, 190),
        ],
        "blue": [
            (7, 13, 23),
            (14, 23, 38),
            (22, 32, 54),
            (33, 47, 80),
            (46, 69, 104),
            (60, 90, 138),
            (80, 120, 178),
        ],
        "dark_brown": [
            (14, 9, 6),
            (19, 13, 9),
            (29, 20, 13),
            (38, 26, 16),
            (48, 33, 22),
            (59, 40, 28),
            (80, 55, 40),
        ]
    }



    return random.choice(list(palettes.values()))

def random_palette(count, vibrance=0.8, from_type=None):
    if from_type:
        base = get_palette(from_type)
        chosen = []
        for i in range(count):
            idx = int(i*len(base)/count)
            chosen.append(base[idx])
        return chosen
    return [tuple(int(vibrance*random.randint(128,255)+(1-vibrance)*random.randint(0,60)) for _ in range(3)) for _ in range(count)]

def upscale_px(surf):
    return pygame.transform.scale(surf, (WIDTH, HEIGHT))

def random_safe_planet_positions(n, low_w, low_h, min_r, max_r):
    poses = []
    for loop in range(n*6):
        r = random.randint(min_r, max_r)
        cx = random.randint(r+16, low_w-r-16)
        cy = random.randint(r+16, low_h-r-16)
        if all(math.hypot(cx-x, cy-y)>r2+r+28 for (x, y, r2) in poses):
            poses.append((cx, cy, r))
            if len(poses) == n: break
    return poses

def draw_px_gradient_bg(surf, stops):
    for y in range(LOW_H):
        t = y / LOW_H
        if len(stops)==2:
            col = lerp_color(stops[0], stops[1], t)
        else:
            sec = t*(len(stops)-1)
            base = int(sec)
            frac = sec-base
            col = lerp_color(stops[base],stops[min(len(stops)-1,base+1)],frac)
        for x in range(LOW_W):
            surf.set_at((x,y), col)

def draw_px_stars(surf, density=0.004, palette=None):
    if palette is None: palette = [(255,255,255),(238,230,255),(220,240,180)]
    ct = int(density * LOW_W * LOW_H)
    for _ in range(ct):
        x,y = random.randint(0,LOW_W-1), random.randint(0,LOW_H-1)
        surf.set_at((x,y), random.choice(palette))
        if random.random()<0.1:
            for dx,dy in [(1,0),(0,1),(-1,0),(0,-1)]:
                if 0<=x+dx<LOW_W and 0<=y+dy<LOW_H:
                    surf.set_at((x+dx,y+dy), random.choice(palette))
        if random.random()<0.02:
            r = random.randint(1,2)
            for xx in range(-r,r+1):
                for yy in range(-r,r+1):
                    if 0<=x+xx<LOW_W and 0<=y+yy<LOW_H:
                        surf.set_at((x+xx,y+yy), (255,255,255))

def draw_px_nebula(surf, palette, octaves=5, alpha=0.49):
    noise = PerlinNoise(octaves=octaves)
    for y in range(LOW_H):
        for x in range(LOW_W):
            val = (noise([x/LOW_W, y/LOW_H])+1)/2
            if val>0.62:
                idx = int(val*(len(palette)-1))
                neb = tuple(int((1-alpha)*surf.get_at((x,y))[i]+alpha*palette[idx][i]) for i in range(3))
                surf.set_at((x,y), neb)
            if random.random()<0.001 and val>0.66 and x%4==0 and y%4==0:
                surf.set_at((x,y), (220,130,255))

def draw_cluster_nebula(surf, clusters, palette, max_size=42):
    for _ in range(clusters):
        cx = random.randint(42,LOW_W-42)
        cy = random.randint(37,LOW_H-37)
        size = random.randint(int(max_size*0.6),max_size)
        color = random.choice(palette)
        for y in range(-size,size):
            for x in range(-size,size):
                dist = math.sqrt(x*x+y*y)
                if dist<size and random.random()<0.71*(1-dist/size):
                    px, py = cx+x, cy+y
                    if 0<=px<LOW_W and 0<=py<LOW_H:
                        surf.set_at((px,py), color)

def draw_px_planet(surf, cx, cy, r, palette, noise, bands):
    for y in range(-r, r):
        for x in range(-r, r):
            if x*x + y*y <= r*r:
                rx, ry = cx+x, cy+y
                if 0<=rx<LOW_W and 0<=ry<LOW_H:
                    norm = math.sqrt(x*x+y*y)/r
                    idx = int(norm * (bands-1))
                    col = palette[idx]
                    surf.set_at((rx, ry), col)

                    if abs(norm-1)<0.08:
                        surf.set_at((rx, ry), lerp_color(col, (255,255,255), 0.92))

def draw_planet_shadow(surf, cx, cy, r, shade=(0,0,0), alpha=0.31):
    for y in range(-r, r):
        for x in range(-r, r):
            if x*x + y*y <= r*r and x>0:
                rx, ry = cx+x, cy+y
                if 0<=rx<LOW_W and 0<=ry<LOW_H:
                    col = surf.get_at((rx,ry))
                    shad = tuple(int(col[i]*(1-alpha)+shade[i]*alpha) for i in range(3))
                    surf.set_at((rx,ry), shad)

"""def draw_px_craters(surf, cx, cy, r, min_r, max_r, count):
    for _ in range(count):
        angle = random.uniform(0,2*math.pi)
        dist = random.uniform(r*0.13, r*0.93)
        cr = random.randint(min_r,max_r)
        crater_cx = int(cx + math.cos(angle)*dist)
        crater_cy = int(cy + math.sin(angle)*dist)
        for y in range(-cr, cr):
            for x in range(-cr, cr):
                if x*x + y*y <= cr*cr:
                    px, py = crater_cx + x, crater_cy + y
                    if 0<=px<LOW_W and 0<=py<LOW_H:
                        surf.set_at((px, py), (50,46,32))"""

def draw_px_highlight(surf, cx, cy, r, highlight_col):
    for theta in range(72,114,1):
        dx = int(r*math.cos(math.radians(theta)))
        dy = int(r*math.sin(math.radians(theta)))
        for t in range(2,8):
            x = cx+dx//t
            y = cy+dy//t
            if 0<=x<LOW_W and 0<=y<LOW_H:
                surf.set_at((x,y), highlight_col)

def draw_px_rings(surf, cx, cy, r, palette, rings=3, fade=17):
    wave_freq = 13
    wave_amp = 2
    for ring in range(rings):
        cr = r + ring*random.randint(8,13)
        col = tuple(min(255,max(0,palette[-1][i]-(fade*ring))) for i in range(3))
        for theta in range(0,360,1):
            wav = int(math.sin(theta/wave_freq+ring)*wave_amp) if ring>0 else 0
            x = int(cx + (cr+wav)*math.cos(math.radians(theta)))
            y = int(cy + (cr+wav)*math.sin(math.radians(theta)))
            if 0<=x<LOW_W and 0<=y<LOW_H:
                surf.set_at((x,y), col)
                if random.random()<0.07 and 0<=x+1<LOW_W and 0<=y+1<LOW_H:
                    surf.set_at((x+1,y+1), col)

def draw_px_moons(surf, planet_x, planet_y, planet_r, count, min_r, max_r, palette, noise):
    moon_positions = set()
    for _ in range(count):
        r = random.randint(min_r,max_r)
        angle = random.uniform(0,2*math.pi)
        dist = planet_r + r + random.randint(9,16)
        mx = int(planet_x + math.cos(angle)*dist)
        my = int(planet_y + math.sin(angle)*dist)
        moon_positions.add((mx,my,r))
        moon_col = [lerp_color(palette[random.randint(0,len(palette)-1)], (180,180,206), 0.19) for _ in range(random.randint(2,5))]
        moon_noise = PerlinNoise(octaves=random.randint(2,3))
        draw_px_planet(surf,mx,my,r,moon_col,moon_noise,len(moon_col))
        draw_planet_shadow(surf, mx,my,r,shade=(0,0,0),alpha=random.uniform(0.1,0.44))
        #draw_px_craters(surf,mx,my,r,2,6,random.randint(5,15))

def draw_planet_atmosphere(light_surf, cx, cy, r, color,max_width=9,fade=0.12):
    for i in range(1,max_width+1):
        alpha = int(150 * (1-fade*i))
        col = tuple(min(255, max(0,int(color[j]*(1-fade*i))))for j in range(3))
        pygame.draw.circle(light_surf, col+(alpha,),(cx,cy),r+i,1)

def draw_cosmic_haze(surf, palette, haze_count=6, max_rad_range=(30,90), alpha=60):
    for _ in range(haze_count):
        cx = random.randint(0, LOW_W-1)
        cy = random.randint(0, LOW_H-1)
        rad = random.randint(*max_rad_range)
        color = random.choice(palette)
        # Prevent overly white haze
        color = tuple(int(c*0.75 + random.choice(palette)[i]*0.25) for i, c in enumerate(color))
        haze = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA)
        for r in range(rad, 0, -1):
            cr = tuple(int((r/rad) * color[i]) for i in range(3))
            haze_alpha = int((min(alpha, 90) * r) / rad)  # never more than 90
            pygame.draw.circle(haze, cr+(haze_alpha,), (rad, rad), r)
        surf.blit(haze, (cx-rad, cy-rad), special_flags=pygame.BLEND_RGBA_ADD)


def blend_layers(base, overlays):
    result = base.copy()
    for layer in overlays:
        result.blit(layer,(0,0), special_flags=pygame.BLEND_RGBA_ADD)
    return result

"""def add_noise_texture(surf, intensity=0, octaves=0):
    noise = PerlinNoise(octaves=octaves)
    for y in range(LOW_H):
        for x in range(LOW_W):
            val = (noise([x/LOW_W,y/LOW_H]) +1)/2
            delta = int((val-0.5)*intensity * 2)
            old = surf.get_at((x,y))
            new_col = tuple(max(0,min(255,old[i]+delta))for i in range(3))
            surf.set_at((x,y), new_col)"""

def soften_artifact_edges(surf, radius=1):
    arr = pygame.surfarray.pixels3d(surf)
    for y in range(radius, LOW_H-radius):
        for x in range(radius, LOW_W-radius):
            values = []
            for dx in range(-radius, radius+1):
                for dy in range(-radius, radius+1):
                    values.append(arr[x+dx,y+dy])
            mean = [int(sum(col)/len(col))for col in zip(*values)]
            arr[x,y] = mean
    del arr

"""def paint_deep_space_patches(surf, palette, patch_count=4, min_size=38, max_size=110):
    for _ in range(patch_count):
        cx = random.randint(min_size, LOW_W-min_size-1)
        cy = random.randint(min_size, LOW_H-min_size-1)
        rad = random.randint(min_size,max_size)
        color = random.choice(palette)
        valpha = 30 + random.randint(0,90)
        patch = pygame.Surface((rad*2, rad*2),pygame.SRCALPHA)
        for r in range(rad,0,-1):
            c = tuple(int((r/rad)*color[i])for i in range(3))
            a = int(valpha * (r/rad))
            pygame.draw.circle(patch, c+(a,), (rad, rad),r)
        surf.blit(patch, (cx-rad,cy-rad),special_flags=pygame.BLEND_RGBA_ADD)"""

def procedural_lensflare(surf, cx,cy,palette, size=26, intensity=0.54):
    flare = pygame.Surface((size*2,size*2), pygame.SRCALPHA)
    center_color = palette[0]
    for r in range(size,0,-1):
        t = r/size
        base = tuple(int(center_color[i]*(t**intensity)) for i in range(3))
        alpha = int(120 * t)
        pygame.draw.circle(flare, base+(alpha,), (size,size),r)
    surf.blit(flare,(cx-size,cy-size), special_flags=pygame.BLEND_RGBA_ADD)

def draw_rich_px_scene(surf, planet_palette_type='nebula', nebula_palette_type='nebula', extra_deep=None):
    stops = random_palette(random.randint(2,4),0.93, nebula_palette_type)
    draw_px_gradient_bg(surf, stops)
    #add_noise_texture(surf, intensity=6 + random.randint(0,8), octaves=random.randint(2,4))
    draw_px_stars(surf, density=0.005, palette=[(255,255,255),(220,234,234),(160,220,225)])
    neb_col = random_palette(random.randint(4,7),0.97,nebula_palette_type)
    #draw_px_nebula(surf, neb_col, octaves=random.randint(2,5),alpha=0.5+random.random()*0.2)
    haze_col = random_palette(random.randint(4,7),0.7,nebula_palette_type)
    draw_cosmic_haze(surf, haze_count=random.randint(2,5), max_rad_range=(60,125),alpha=random.randint(44,120))
    deep_pal = random_palette(random.randint(3,6),0.9,extra_deep) if extra_deep else random_palette(3,0.9)
    #paint_deep_space_patches(surf, deep_pal, patch_count=random.randint(3,6), min_size=36,max_size=135)
    cluster_p = random.palette(random.randint(3,5),0.82)
    #draw_cluster_nebula(surf, clusters=random.randint(7,15), palette=cluster_p, max_size=random.randint(23,54))

def generate_px_planets(surf, n, min_r, max_r, shadow_degrees=(95,290)):
    ptypes = ["sunset","ocean","forest","nebula","gold"]
    palettes = [random_palette(random.randint(5,11), 0.94, random.choice(ptypes)) for _ in range(n)]
    positions = random_safe_planet_positions(n, LOW_W, LOW_H, min_r, max_r)
    planet_infos = []
    for idx, (cx, cy, r) in enumerate(positions):
        planet_noise = PerlinNoise(octaves=random.randint(2,6))
        draw_px_planet(surf, cx, cy, r, palettes[idx], planet_noise, len(palettes[idx]))
        #draw_px_craters(surf, cx, cy,r, 2, max(int(r*0.44),4), random.randint(5,9))
        highlight_col = lerp_color((255,255,255), palettes[idx][0], 0.5)
        #draw_px_craters(surf, cx, cy, r, 2, max(int(r*0.44),4), random.randint(5,9))
        highlight_col = lerp_color((255,255,255), palettes[idx][0], 0.5)
        draw_px_highlight (surf, cx, cy, r, highlight_col)
        draw_px_rings(surf, cx, cy, r, palettes[idx], rings=random.randint(1,3), fade=random.randint(13,25))
        atoms_col = lerp_color(palettes[idx][0],(255,255,255), 0.06)
        # will be rendered as a separate overlay layer for blending

        planet_infos.append({"cx":cx, "cy":cy, "r":r, "rings":random.randint(1,3),"atoms_mcol": atoms_col})
        return positions, palettes, planet_infos

def generate_moons(surf, positions, min_r=5, max_r=12):
    moon_all_palettes = []
    moons_by_planet = []
    for cx, cy, r in positions:
        moon_count = random.randint(1,3)
        moons = []
        moon_pal = random_palette(random.randint(2,4),0.84)
        moon_all_palettes.append(moon_pal)
        moon_noise = PerlinNoise(octaves=random.randint(2,3))
        for _ in range(moon_count):
            angle = random.uniform(0,2*math.pi)
            dist = r + random.randint(min_r+7,max_r+16)
            mx = int(cx + math.cos(angle) * dist)
            my = int(cy + math.sin(angle) * dist)
            m_r = random.randint(min_r,max_r)
            draw_px_planet(surf, mx,my, m_r,moon_pal,moon_noise,len(moon_pal))
            draw_planet_shadow(surf, mx,my,m_r, shade=(0,0,0),alpha = random.uniform(0.18,0.34))
            #draw_px_craters(surf, mx,my, m_r, 2, m_r // 2,random.randint(3,7))
            moons.append((mx,my,m_r))
        moons_by_planet.append(moons)
    return moon_all_palettes, moons_by_planet

def planet_atmospheres_layer(planet_data, atmos_alpha=105, blur_rad=13):
    atmos_surf = pygame.Surface((LOW_W, LOW_H), pygame.SRCALPHA)
    for planet in planet_data:
        for i in range(blur_rad, 1, -1):
            alpha = int(atmos_alpha * (1 / blur_rad))
            col = planet["atmcol"] + (alpha,)
            pygame.draw.circle(atmos_surf, col,(planet["cx"], planet["cy"]), planet["r"]+1, 0)
            return atmos_surf
        
def draw_lensflares(surf, planet_data):
    for planet in planet_data:
        for _ in range(random.randint(2, 6)):
            angle =random.uniform(0, 2*math.pi)
            dist = planet["r"] + 12 + random.randint(10,80)
            fx = int(planet["cx"] + math.cos(angle)*dist)
            fy = int(planet["cy"] + math.sin(angle)*dist)
            procedural_lensflare(surf, fx, fy, [planet["atmcol"], (255,255,255)], size=random.randint(14,38), intensity=0.44+random.randint()*0.52)

def merge_pixel_layers(base, overlays, blend_flag=pygame.BLEND_RGBA_ADD):
    composite = base.copy()
    for layer in overlays:
        composite.blit(layer, (0, 0), special_flags=blend_flag)
        return composite

def draw_loose_particles(surf, regions, palette, count_per_region=26, max_dist=86):
    for cx, cy, r in regions:
        region_ct = random.randint(count_per_region//2, count_per_region)
        for _ in range(region_ct):
            angle = random.uniform(0, 2 * math.pi)
            dist = r + random.randint(int(r*0.7), max_dist)
            px = int(cx + math.cos(angle)*dist)
            py = int(cy + math.sin(angle)*dist)
            if 0<=px<LOW_W and 0<=py<LOW_H:
                color = random.choice(palette)
                surf.set_at((px, py), color)

def paint_light_trils(surf, planet_positions, n=2, max_len=48, palette=None):
    if palette is None: palette = [(255,255,240),(200,200,130),(255,255,255)]
    for (cx, cy, r) in planet_positions:
        for _ in range(n):
            angle = random.uniform(0, 2*math.pi)
            for t in range(10, max_len, random.randint(7,14)):
                tx = int(cx + (r+t)*math.cos(angle))
                ty = int(cy + (r+t)*math.sin(angle))
                if 0<=tx<LOW_W and 0<=ty<LOW_H:
                    surf.set_at((tx, ty), random.choice(palette))
                    if random.random()<0.04 and 0<=tx+1<LOW_W and 0<=ty+1<LOW_H:
                        surf.set_at((tx+1, ty+1),(255,255,252))

def cosmic_noise_overlay(surf, pal, alpha=16, octaves=6):
    noise = PerlinNoise(octaves=octaves)
    for y in range(LOW_H):
        for x in range(LOW_W):
            v = (noise([x/LOW_W,y/LOW_H])+1)/2
            if v>0.6:
                idx = int(v*(len(pal)-1))
                base = surf.get_at((x,y))
                col = tuple((base[i]*(255-alpha) + pal[idx][i]*alpha)//255 for i in range(3))
                surf.set_at((x,y),col)

def soften_high_contrast_pixel_edges(surf, passes=2):
    for _ in range(passes):
        soften_artifact_edges(surf, radius = 1)

def add_random_monochrome_noise(surf, strength=14):
    for y in range(LOW_H):
        for x in range(LOW_W):
            delta = random.randint(-strength, strength)
            col = surf.get_at((x,y))
            newc = tuple(max(0,min(255, col[i]+delta))for i in range(3))
            surf.set_at((x,y),newc)

def add_cosmic_sparkles(surf, count=150):
    for _ in range(count):
        x = random.randint(0,LOW_W-1)
        y = random.randint(0, LOW_H-1)
        c = (255,255,random.randint(180,255))
        surf.set_at((x,y),c)
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            if random.random() < 0.13:
                tx, ty = x+dx, y+dy
                if 0<=tx<LOW_W and 0<=ty<LOW_H:
                    surf.set_at((tx,ty),c)

def halo_about_planets(surf, planets, layer_color=(220,220,225),blur_width=4):
    for cx,cy,r in planets:
        for i in range(1,blur_width+1):
            bcol = tuple(min(255,int(layer_color[j] * (1 - (i/blur_width)*0.8))) for j in range(3))
            alpha = int(80 * (1*i/blur_width))
            pygame.draw.circle(surf, bcol+(alpha,),(cx,cy),r+i,1)

def paint_planet_gas_bands(surf, cx, cy, r, palette, bands_min=3, bands_max=9, strength=0.27):
    bands = random.randint(bands_min, bands_max)
    for b in range(bands):
        angle = random.uniform(0, 2*math.pi)
        width = random.uniform(r*0.13, r*0.5)
        thickness = random.randint(2, int(max(2, .14*r)))
        color = lerp_color(palette[0], palette[-1], random.random())
        for t in range(-thickness, thickness+1):
            for theta in range(0, 360, 1):
                wx = int((width+t)*math.cos(math.radians(theta+math.degrees(angle))))
                wy = int((width+t)*math.sin(math.radians(theta+math.degrees(angle))))
                px = cx + wx
                py = cy + wy
                dist = math.sqrt((px-cx)**2 + (py-cy)**2)
                if abs(dist - width) < 2 and 0<=px<LOW_W and 0<=py<LOW_H:
                    surf.set_at((px, py), color)

def add_stray_stardust(surf, count=55, palette=None):
    if palette is None: palette = [(230,222,222),(255,255,224),(210,230,190)]
    for _ in range(count):
        idx = random.randint(0, len(palette)-1)
        for _ in range(random.randint(16,33)):
            angle = random.uniform(0,2*math.pi)
            dist = random.uniform(12, LOW_W//2)
            cx = random.randint(0, LOW_W-1)
            cy = random.randint(0, LOW_H-1)
            px = int(cx + math.cos(angle)*dist)
            py = int(cy + math.sin(angle)*dist)
            if 0<=px<LOW_W and 0<=py<LOW_H:
                surf.set_at((px, py), palette[idx])

def draw_debris_fields(surf, regions, debris_ct=15, max_len=70, spread=2):
    palette = [(80,85,85),(150,140,120),(200,214,220)]
    for cx, cy, r in regions:
        for _ in range(debris_ct):
            angle = random.uniform(0,2*math.pi)
            for l in range(random.randint(r//2, max_len), random.randint(r+8, max_len*2)):
                x = int(cx + (r+l)*math.cos(angle) + random.randint(-spread,spread))
                y = int(cy + (r+l)*math.sin(angle) + random.randint(-spread,spread))
                if 0<=x<LOW_W and 0<=y<LOW_H:
                    cidx = random.randint(0, len(palette)-1)
                    surf.set_at((x, y), palette[cidx])

def glow_effect_over_layer(surf, planets, glow_col=(255,255,240), size_mult=1.07, strength=5):
    for cx, cy, r in planets:
        for s in range(1, strength+1):
            a = int(180 / (s+2))
            color = tuple(int(glow_col[i] * (1-s/strength) + 220*s/strength) for i in range(3))
            pygame.draw.circle(surf, color+(a,), (cx, cy), int(r*size_mult)+s, width=2)

def fake_galaxy_arms(surf, center, rad, arms=3, thickness=9, palette=None, fade=0.4):
    if palette is None: palette = [ (255,255,255), (230,218,255), (120,200,245) ]
    for a in range(arms):
        angle0 = 2*math.pi*a/arms + random.random()*math.pi/5
        arm_angles = [ angle0 + 0.34*i for i in range(random.randint(7,13)) ]
        for t in range(thickness):
            for i, arm_angle in enumerate(arm_angles):
                length = random.randint(int(rad*0.43), int(rad*1.2))
                cx, cy = center
                for d in range(8, length, 4):
                    fadefac = (i+1)/len(arm_angles) * fade
                    x = int(cx + (d+t*2)*math.cos(arm_angle+0.61*d/rad))
                    y = int(cy + (d+t*2)*math.sin(arm_angle+0.55*d/rad))
                    if 0<=x<LOW_W and 0<=y<LOW_H:
                        cidx = random.randint(0, len(palette)-1)
                        col = tuple( int(fadefac*palette[cidx][ii] + (1-fadefac)*surf.get_at((x,y))[ii]) for ii in range(3) )
                        surf.set_at((x, y), col)

def quantize_colors(surf, palette, dither=False):
    arr = pygame.surfarray.pixels3d(surf)
    for x in range(arr.shape[0]):
        for y in range(arr.shape[1]):
            orig = tuple(arr[x, y])
            idx = min(range(len(palette)), key=lambda i: sum((orig[j]-palette[i][j])**2 for j in range(3)))
            c = palette[idx]
            if dither:
                # Floyd-Steinberg
                error = [orig[j]-c[j] for j in range(3)]
                arr[x,y] = c
                if x+1<arr.shape[0]: arr[x+1,y] = [min(255,max(0,arr[x+1,y][j]+error[j]*7/16)) for j in range(3)]
                if x-1>=0 and y+1<arr.shape[1]: arr[x-1,y+1] = [min(255,max(0,arr[x-1,y+1][j]+error[j]*3/16)) for j in range(3)]
                if y+1<arr.shape[1]: arr[x,y+1] = [min(255,max(0,arr[x,y+1][j]+error[j]*5/16)) for j in range(3)]
                if x+1<arr.shape[0] and y+1<arr.shape[1]: arr[x+1,y+1] = [min(255,max(0,arr[x+1,y+1][j]+error[j]*1/16)) for j in range(3)]
            else:
                arr[x,y] = c
    del arr

def make_big_palette(size, bases=[(36,40,100), (220,190,111), (145,228,155), (65,65,215), (179,36,148)], jitter=13):
    result = []
    while len(result) < size:
        base = random.choice(bases)
        for j in range(3):
            c = tuple(min(255,max(0,base[i]+random.randint(-jitter,jitter))) for i in range(3))
            result.append(c)
            if len(result) >= size:
                break
    return result

def radial_mask(center, rad, width):
    mask = pygame.Surface((LOW_W, LOW_H), pygame.SRCALPHA)
    cx, cy = center
    for y in range(LOW_H):
        for x in range(LOW_W):
            dist = math.sqrt((x-cx)**2 + (y-cy)**2)
            if rad-width < dist < rad+width:
                mask.set_at((x,y), (255,255,255,int(255*(1-abs(dist-rad)/width))))
    return mask

def blend_mask_overlay(surf, overlay, alpha=100):
    arr = pygame.surfarray.pixels3d(surf)
    arr_mask = pygame.surfarray.pixels3d(overlay)
    for x in range(min(arr.shape[0], arr_mask.shape[0])):
        for y in range(min(arr.shape[1], arr_mask.shape[1])):
            src = arr_mask[x,y]
            arr[x,y] = [int(arr[x,y][i]*(255-alpha)/255 + src[i]*alpha/255) for i in range(3)]
    del arr
    del arr_mask

def nebula_ring_pattern(surf, center, r, width, palette, blur=5):
    for b in range(blur):
        alpha = int(180 / (b+2))
        col = lerp_color(palette[0], palette[-1], b/blur)
        pygame.draw.circle(surf, col+(alpha,), center, r+width-b, width=width-b)

def draw_radial_galaxy(surf, cx,cy,rad_min,rad_max,arm_count,palette,fade=0.7):
    for arm in range(arm_count):
        base_angle = random.uniform(0,2*math.pi)
        for sweep in range(rad_min, rad_max, 3):
            theta = base_angle + random.uniform(-0.06,0.06)+sweep/rad_max*2*math.pi/arm_count
            x = int(cx + sweep*math.cos(theta))
            y = int(cy + sweep*math.sin(theta))
            if 0<=x<LOW_W and 0<=y<LOW_H:
                col = lerp_color(palette[0],palette[-1],sweep/(rad_max-rad_min)*fade)
                surf.set_at((x,y),col)

def generate_star_clusters(surf, cluster_count=6,cluster_size_range=(14,44),star_palette=None):
    if star_palette is None:
        star_palette = [(255,255,255),(220,230,220),(255,220,210)]
    for _ in range(cluster_count):
        center_x = random.randint(0,LOW_W-1)
        center_y = random.randint(0,LOW_H-1)
        size = random.randint(*cluster_size_range)
        for _ in range(random.randint(18,43)):
            angle = random.uniform(0,2*math.pi)
            dist = random.uniform(0,size)
            x = int(center_x + math.cos(angle)*dist)
            y = int(center_y + math.sin(angle)*dist)
            if 0<=x<LOW_W and 0<=y<LOW_H:
                surf.set_at((x,y),random.choice(star_palette))
            if random.random()<0.13:
                sx = x + random.randint(-2,2)
                sy = y + random.randint(-2,2)
                if 0<=sx<LOW_W and 0<=sy<LOW_H:
                    surf.set_at((sx,sy),random.choice(star_palette))

def draw_faint_belt(surf, center, angle, width, length, palette, fade=0.08):
    cx,cy = center
    for t in range(-width//2,width//2):
        for l in range(length):
            dx = int(math.cos(angle)*(l+t))
            dy = int(math.sin(angle)*(l+t))
            x = cx+dx
            y = cy+dy
            if 0<=x<LOW_W and 0<=y<LOW_H:
                fade_amt = min(1, l/length*fade)
                col = lerp_color(palette[0],palette[-1], fade_amt)
                surf.set_at((x,y),col)

def draw_pixel_linescape(surf, y_start, y_stop, color, scatter=0.03):
    for y in range(y_start,y_stop):
        for x in range(LOW_W):
            if random.random()< scatter:
                surf.set_at((x,y),color)
            elif random.random()<0.01:
                dx = x+random.randint(1,4)
                if 0<=dx<LOW_W:
                    surf.set_at((dx,y),color)

def add_galactic_center(surf,cx,cy,radius,palette, bright_col=(255,255,255)):
    for r in range(radius,0,-1):
        factor = r / radius
        base = lerp_color(palette[0],palette[-1],factor)
        a = int(160*factor)
        pygame.draw.circle(surf, base+(a,),(cx,cy),r)

def draw_perlin_twinkle(surf, palette,octaves=5,threshold=0.88):
    noise = PerlinNoise(octaves=octaves)
    for y in range(LOW_H):
        for x in range(LOW_W):
            val = (noise([x/LOW_W,y/LOW_H])+1)/2
            if val>threshold:
                surf.set_at((x,y),random.choice(palette))
                if random.random()<0.2:
                    dx,dy = random.randint(-1,1), random.randint(-1,1)
                    tx,ty = x+dx,y+dy
                    if 0<=x<LOW_W and 0<=ty<LOW_H:
                        surf.set_at((tx,ty),random.choice(palette))

def cosmic_field_overlay(surf, centers, palette, n_lines=44):
    for cx,cy in centers:
        for _ in range(n_lines):
            angle = random.uniform(0,2*math.pi)
            length = random.randint(14,68)
            color = random.choice(palette)
            for l in range(length):
                x = int(cx + math.cos(angle)*l)
                y = int(cy + math.sin(angle)*l)
                if 0<=x<LOW_W and 0<=y<LOW_H:
                    surf.set_at((x,y),color)

def draw_galazy_cluster_overlay(surf, n_clusters=4,star_pal=None):
    if star_pal==None:
        star_pal = [(255,255,255),(220,230,210),(190,240,255)]
    for _ in range(n_clusters):
        cx,cy = random.randint(0,LOW_W-1)
        for k in range(random.randint(31,66)):
            angle = random.uniform(0,2*math.pi)
            dist = random.uniform(0, random.randint(13,29))
            x = int(cx + math.cos(angle)*dist)
            y = int(cy + math.sin(angle)*dist)
            if 0<=x<LOW_W and 0<y<=LOW_H:
                surf.set_at((x,y),random.choice(star_pal))

def draw_cosmic_dust(surf,density=0.021,palette=None):
    if palette is None:
        palette = [(190,180,170),(180,170,200),(220,213,180),(213,180,220)]
        count = int(density * LOW_W * LOW_H)
        for _ in range(count):
            x = random.randint(0,LOW_W-1)
            y = random.randint(0, LOW_H-1)
            surf.set_at((x,y), random.choice(palette))

def build_overlay_layers(base_surf, planet_data, moons_data):
    atmosphere_layer = pygame.Surface((LOW_W,LOW_H),pygame.SRCALPHA)
    draw_planet_atmosphere(atmosphere_layer,base_surf,planet_data)
    lensflare_layer = pygame.Surface((LOW_W,LOW_H), pygame.SRCALPHA)
    draw_lensflares(lensflare_layer, planet_data)
    deep_cosmic_layer = pygame.Surface((LOW_W,LOW_H),pygame.SRCALPHA)
    draw_cosmic_haze(deep_cosmic_layer, random_palette(6,0.75),haze_count=5, max_rad_range=(85,115),alpha=95)
    #paint_deep_space_patches(deep_cosmic_layer,random_palette(4,0.9),patch_count=4,min_size=50,max_size=95)
    final_img = blend_layers(base_surf,[atmosphere_layer, lensflare_layer, deep_cosmic_layer])
    return final_img

def draw_planet_atmosphere(surf,base,planets, atmos_alpha=130, blur_rad=12):
    cx,cy,r = 0,0,0
    for planet in planets:
        cx,cy,r = planet["cx"], planet["cy"],planet["r"]
        color = planet["atmcol"]
        for i in range(blur_rad,0,-1):
            a = int(atmos_alpha * (i/blur_rad))
            col = tuple(min(255,max(0,int(color[j]*(1-i/blur_rad))))for j in range(3)) + (a,)
            pygame.draw.circle(surf, col, (cx,cy),r+i)
    surf.blit(base,(0,0))

def draw_lensflares(surf, planets):
    for planet in planets:
        count = random.randint(1,5)
        for _ in range(count):
            angle = random.uniform(0,2*math.pi)
            dist = planet["r"] + random.randint(9,55)
            fx = int(planet["cx"] + math.cos(angle)*dist)
            fy = int(planet["cy"] + math.sin(angle)*dist)
            procedural_lensflare(surf, fx, fy, [planet["atmcol"],(240,240,240)], size = random.randint(13,34), intensity=0.46 + random.random()*0.54)

def procedural_lensflare(surf, cx,cy, palette, size=25,intensity=0.56):
    flare = pygame.Surface((size*2,size*2), pygame.SRCALPHA)
    base_color = palette[0]
    for r in range(size,0,-1):
        fade_factor = (r/size) ** intensity
        color = tuple(int(base_color[i]*fade_factor)for i in range(3))
        alpha = int(120 * fade_factor)
        pygame.draw.circle(flare, color+(alpha,),(size,size),r)
    surf.blit(flare, (cx-size,cy-size),special_flags=pygame.BLEND_RGBA_ADD)

def generate_and_draw_scene():
    low_res_surface = pygame.Surface((LOW_W,LOW_H))
    paltype = random.choice(["nebula","sunset","ocean","forest", "gold"])
    bg_colors = random_palette(random.randint(2,4),0.9,paltype)
    draw_px_gradient_bg(low_res_surface,bg_colors)
    #add_noise_texture(low_res_surface,intensity=8,octaves=3)
    draw_px_stars(low_res_surface, density=0.004,palette=[(255,255,255),(210,230,230),(170,220,225)])
    #draw_px_nebula(low_res_surface, random_palette(random.randint(3,7),0.85,paltype), octaves=4,alpha=0.54)
    #draw_cluster_nebula(low_res_surface,clusters=random.randint(7,15),palette=random_palette(random.randint(3,5),0.83),max_size=random.randint(24,53))
    planet_palette = [random_palette(random.randint(5,10),0.92,paltype)for _ in range(random.randint(2,3))]
    planet_positions = random_safe_planet_positions(len(planet_palette),LOW_W, LOW_H,15,32)

    planet_infos = []
    for idx, (cx,cy,rad) in enumerate(planet_positions):
        noise = PerlinNoise(octaves=random.randint(3,6))
        draw_px_planet(low_res_surface,cx,cy,rad,planet_palette[idx],noise,len(planet_palette[idx]))
        draw_planet_shadow(low_res_surface,cx,cy,rad,shade=(0,0,0),alpha=random.uniform(0.26,0.45))
        #draw_px_craters(low_res_surface,cx,cy.rad,random.randint(2,6),random.randint(5,15),random.randint(6,19))
        highlight_col = lerp_color((255,255,255),planet_palette[idx][0],0.55)
        draw_px_rings(low_res_surface,cx,cy,rad,planet_palette[idx],rings=random.randint(1,4),fade=random.randint(12,23))
        atmos_col = lerp_color(planet_palette[idx][0],(245,245,250),0.60)
        planet_infos.append({"cx":cx,"cy":cy,"r":rad,"atmcol":atmos_col})

        moons_palettes, moons_info = generate_moons(low_res_surface, planet_positions,min_r=6,max_r=13)
        atmosphere_layer = planet_atmospheres_layer(planet_infos)
        final_img = blend_layers(low_res_surface,[atmosphere_layer])
        draw_lensflares(final_img, planet_infos)

        hi_res_surface = upscale_px(final_img)
        window.blit(hi_res_surface,(0,0))
        pygame.display.flip()

class WallpaperCreator:
    def __init__(self, width=1600, height=1100, block_size=8):
        self.width = width
        self.height = height
        self.block_size = block_size
        self.low_w = width // block_size
        self.low_h = height // block_size
        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Perlin Noise Pixel Art Space Wallpaper Creator")
        self.low_surface = pygame.Surface((self.low_w, self.low_h))
        self.clock = pygame.time.Clock()
        self.running = True
        self.planet_data = []
        self.moons_data = []

    def clear_surface(self):
        self.low_surface.fill((0, 0, 0))

    def generate_scene(self):
        self.clear_surface()
        paltype = random.choice(["nebula", "sunset", "ocean", "forest", "gold"])
        bg_colors = random_palette(random.randint(2, 4), 0.9, paltype)
        draw_px_gradient_bg(self.low_surface, bg_colors)
        #add_noise_texture(self.low_surface, intensity=8, octaves=3)
        draw_px_stars(self.low_surface, density=0.004, palette=[(255, 255, 255), (210, 230, 230), (170, 220, 255)])
        #draw_px_nebula(self.low_surface, random_palette(random.randint(3, 7), 0.85, paltype), octaves=4, alpha=0.54)
        #draw_cluster_nebula(self.low_surface, clusters=random.randint(7, 15), palette=random_palette(random.randint(3, 5), 0.83), max_size=random.randint(24, 53))
        planet_count = random.randint(2, 3)
        self.planet_palette = [random_palette(random.randint(5, 10), 0.92, paltype) for _ in range(planet_count)]
        self.planet_positions = random_safe_planet_positions(planet_count, self.low_w, self.low_h, 15, 32)
        self.planet_data.clear()

        for idx, (cx, cy, rad) in enumerate(self.planet_positions):
            noise = PerlinNoise(octaves=random.randint(3, 6))
            draw_px_planet(self.low_surface, cx, cy, rad, self.planet_palette[idx], noise, len(self.planet_palette[idx]))
            draw_planet_shadow(self.low_surface, cx, cy, rad, shade=(0, 0, 0), alpha=random.uniform(0.26, 0.45))
            #draw_px_craters(self.low_surface, cx, cy, rad, random.randint(2, 6), random.randint(5, 15), random.randint(6, 19))
            highlight_col = lerp_color((255, 255, 255), self.planet_palette[idx][0], 0.55)
            draw_px_highlight(self.low_surface, cx, cy, rad, highlight_col)
            draw_px_rings(self.low_surface, cx, cy, rad, self.planet_palette[idx], rings=random.randint(1, 4), fade=random.randint(12, 23))
            atmos_col = lerp_color(self.planet_palette[idx][0], (245, 245, 250), 0.69)
            self.planet_data.append({"cx": cx, "cy": cy, "r": rad, "atmcol": atmos_col})

        self.moons_palettes, self.moons_data = generate_moons(self.low_surface, self.planet_positions, min_r=6, max_r=13)

    def render_final(self):
        #atmosphere_layer = planet_atmospheres_layer(self.planet_data)
        final_img = blend_layers(self.low_surface, [])
        #draw_lensflares(final_img, self.planet_data)
        hi_res_surface = upscale_px(final_img)
        self.window.blit(hi_res_surface, (0, 0))
        pygame.display.flip()

    def save_wallpaper(self, filename='space_wallpaper.png'):
        #atmosphere_layer = planet_atmospheres_layer(self.planet_data)
        final_img = blend_layers(self.low_surface, [])
        #draw_lensflares(final_img, self.planet_data)
        hi_res_surface = upscale_px(final_img)
        pygame.image.save(hi_res_surface, filename)

    def event_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_s:
                        self.save_wallpaper()

            self.render_final()
            self.clock.tick(30)
        pygame.quit()


async def main():
    creator = WallpaperCreator()
    creator.generate_scene()
    while creator.running:
        creator.render_final()
        await asyncio.sleep(1/30)  # 30fps, no blocking

if __name__ == "__main__":
    asyncio.run(main())