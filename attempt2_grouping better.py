import pygame
import random
from perlin_noise import PerlinNoise
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
PIXEL_SIZE = 8
GRID_W = WIDTH // PIXEL_SIZE
GRID_H = HEIGHT // PIXEL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Space Art")

noise = PerlinNoise(octaves=5)
colors = [(25,25,112), (72,61,139), (123,104,238), (255,255,255), (255,215,0), (199,21,133), (0,255,255), (34,139,34)]
contrast_colors = [(255,0,100), (0,255,200), (255,255,0), (255,255,255)]

space_grid = []
for x in range(GRID_W):
    col = []
    for y in range(GRID_H):
        val = noise([x/GRID_W, y/GRID_H])
        idx = int((val+1)/2 * (len(colors) - 1))
        base = colors[idx]
        if random.random() < 0.08:
            base = random.choice(contrast_colors)
        col.append(base)
    space_grid.append(col)

def draw_space_grid(surface, grid):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            c = grid[x][y]
            rect = pygame.Rect(x*PIXEL_SIZE, y*PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
            pygame.draw.rect(surface, c, rect)

clock = pygame.time.Clock()

def random_star(surface, count, star_colors):
    for _ in range(count):
        x = random.randint(0, WIDTH-1)
        y = random.randint(0, HEIGHT-1)
        color = random.choice(star_colors)
        r = random.randint(1, 3)
        pygame.draw.circle(surface, color, (x, y), r)

def animate_nebula(grid, frame):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            fx = math.sin(frame*0.03 + x*0.1)*0.5 + 0.5
            fy = math.cos(frame*0.03 + y*0.1)*0.5 + 0.5
            shift = int(40*fx*fy)
            col = grid[x][y]
            grid[x][y] = (max(0, col[0]-shift), max(0, col[1]-shift), min(255, col[2]+shift))

def pulse_grid(grid, phase):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            amp = int(16*math.sin(phase + x*0.2 + y*0.23))
            c = grid[x][y]
            grid[x][y] = (min(255, max(0, c[0]+amp)), min(255, max(0, c[1]-amp)), min(255, max(0, c[2]+amp)))

def randomize_contrast(grid, intensity):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if random.random() < intensity:
                idx = random.randint(0, len(contrast_colors)-1)
                grid[x][y] = contrast_colors[idx]

def overlay_nebula(grid, freq, amplitude):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            cell = grid[x][y]
            nebval = int(amplitude * math.sin(freq*x + freq*y))
            grid[x][y] = (min(255, cell[0]+nebval), min(255, cell[1]+nebval), min(255, cell[2]+nebval))

def circular_gradient(center, radius, color_a, color_b):
    grad = []
    for x in range(GRID_W):
        col = []
        for y in range(GRID_H):
            dx = x - center[0]
            dy = y - center[1]
            dist = math.sqrt(dx*dx + dy*dy)
            inter = min(1, dist/radius)
            r = int(color_a[0]*(1-inter) + color_b[0]*inter)
            g = int(color_a[1]*(1-inter) + color_b[1]*inter)
            b = int(color_a[2]*(1-inter) + color_b[2]*inter)
            col.append((r,g,b))
        grad.append(col)
    return grad

def blend_grids(grid1, grid2, alpha):
    out = []
    for x in range(len(grid1)):
        row = []
        for y in range(len(grid1[0])):
            c1 = grid1[x][y]
            c2 = grid2[x][y]
            r = int(c1[0]*(1-alpha) + c2[0]*alpha)
            g = int(c1[1]*(1-alpha) + c2[1]*alpha)
            b = int(c1[2]*(1-alpha) + c2[2]*alpha)
            row.append((r,g,b))
        out.append(row)
    return out

def draw_grid(surface, grid):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            c = grid[x][y]
            rect = pygame.Rect(x*PIXEL_SIZE, y*PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
            pygame.draw.rect(surface, c, rect)

def fade_grid(grid, amt):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            r,g,b = grid[x][y]
            grid[x][y] = (max(0,r-amt), max(0,g-amt), max(0,b-amt))

def comet_path(surface, frame, color):
    tail_len = 60
    for i in range(tail_len):
        angle = frame*0.02 + i*0.05
        x = int(WIDTH//2 + (200-i*3)*math.cos(angle))
        y = int(HEIGHT//2 + (200-i*3)*math.sin(angle))
        pygame.draw.circle(surface, color, (x,y), max(1, int(10-i*0.15)))

def twinkle(grid, frame):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if random.random() < 0.01:
                amp = int(50*math.sin(frame*0.05 + x + y))
                r,g,b = grid[x][y]
                grid[x][y] = (min(255,r+amp), min(255,g+amp), min(255,b+amp))

def apply_starburst(surface, cx, cy, rays, radius, color):
    for i in range(rays):
        angle = (2*math.pi/rays)*i
        x = int(cx + radius*math.cos(angle))
        y = int(cy + radius*math.sin(angle))
        pygame.draw.line(surface, color, (cx, cy), (x, y), 2)

def invert_colors(grid):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            r,g,b = grid[x][y]
            grid[x][y] = (255-r, 255-g, 255-b)

def add_ring(surface, center, max_radius, color, thickness):
    for r in range(max_radius-thickness, max_radius+1):
        pygame.draw.circle(surface, color, center, r, thickness)

def sprinkle_comet_tails(surface, frame):
    for _ in range(2):
        cx = random.randint(100, WIDTH-100)
        cy = random.randint(100, HEIGHT-100)
        color = random.choice(contrast_colors)
        add_ring(surface, (cx,cy), random.randint(30,100), color, random.randint(2,7))

def overlay_gradient(grid, grad_grid, alpha):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            base = grid[x][y]
            grad = grad_grid[x][y]
            r = int(base[0]*(1-alpha) + grad[0]*alpha)
            g = int(base[1]*(1-alpha) + grad[1]*alpha)
            b = int(base[2]*(1-alpha) + grad[2]*alpha)
            grid[x][y] = (r,g,b)

def wave_warp(grid, freq, amplitude, frame):
    warped = []
    for x in range(len(grid)):
        col = []
        for y in range(len(grid[0])):
            offset = int(amplitude * math.sin(2 * math.pi * y / GRID_H + freq * frame))
            src_x = (x + offset) % len(grid)
            col.append(grid[src_x][y])
        warped.append(col)
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            grid[x][y] = warped[x][y]

def noise_variance(grid, intensity):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            r,g,b = grid[x][y]
            n = random.randint(-intensity, intensity)
            grid[x][y] = (max(0,min(255,r+n)), max(0,min(255,g+n)), max(0,min(255,b+n)))

def save_image(surface, filename):
    pygame.image.save(surface, filename)

def overlay_star_cluster(surface, n_stars):
    for _ in range(n_stars):
        cx = random.randint(50, WIDTH-50)
        cy = random.randint(50, HEIGHT-50)
        color = random.choice(contrast_colors)
        size = random.randint(10,40)
        for i in range(8):
            ang = 2*math.pi*i/8
            x = int(cx + size*math.cos(ang))
            y = int(cy + size*math.sin(ang))
            pygame.draw.line(surface, color, (cx,cy), (x,y), random.randint(1,4))
        pygame.draw.circle(surface, color, (cx,cy), random.randint(6,14))

def overlay_interstellar_cloud(surface, base_color, frame):
    for i in range(7):
        radius = random.randint(60,180)
        cx = random.randint(0, WIDTH)
        cy = random.randint(0, HEIGHT)
        alpha = max(50, int(80+50*math.sin(frame*0.03 + i)))
        cloud = pygame.Surface((radius*2,radius*2), pygame.SRCALPHA)
        pygame.draw.circle(cloud, (*base_color, alpha), (radius,radius), radius)
        screen.blit(cloud, (cx-radius, cy-radius))

def galaxy_curve(surface, frame, color):
    points = []
    for t in range(0, 360, 8):
        angle = math.radians(t)
        x = int(WIDTH//2 + frame*math.cos(angle)*2 + 180*math.cos(angle)*math.sin(frame*0.03))
        y = int(HEIGHT//2 + frame*math.sin(angle)*2 + 180*math.sin(angle)*math.cos(frame*0.03))
        points.append((x, y))
    if len(points) > 1:
        pygame.draw.aalines(surface, color, False, points)

star_colors = [(255,255,255),(255,246,143),(173,216,230),(255,99,71)]

nebula_grad = circular_gradient((GRID_W//2, GRID_H//2), min(GRID_W,GRID_H)//1.8, (50,10,80), (80,110,255))
space_cloud = blend_grids(space_grid, nebula_grad, 0.4)

frame = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save_image(screen, "space_art.png")
            if event.key == pygame.K_i:
                invert_colors(space_cloud)
            if event.key == pygame.K_f:
                fade_grid(space_cloud, 20)
            if event.key == pygame.K_c:
                randomize_contrast(space_cloud, 0.15)

    if frame % 24 == 0:
        animate_nebula(space_cloud, frame)
    if frame % 50 == 0:
        overlay_nebula(space_cloud, 0.09, 25)
    if frame % 32 == 0:
        pulse_grid(space_cloud, frame*0.07)
    twinkle(space_cloud, frame)
    wave_warp(space_cloud, 0.11, 7, frame)
    noise_variance(space_cloud, 2)

    screen.fill((0,0,0))
    draw_grid(screen, space_cloud)
    random_star(screen, 15, star_colors)
    sprinkle_comet_tails(screen, frame)
    overlay_star_cluster(screen, 2)
    overlay_interstellar_cloud(screen, (50,60,170), frame)
    galaxy_curve(screen, frame, (255,255,255))

    pygame.display.flip()
    clock.tick(30)
    frame += 1