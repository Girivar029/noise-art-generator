import pygame
import random
import math
import sys
import time

pygame.init()
WIDTH, HEIGHT = 600, 480
PIXEL_SIZE = 10
GRID_WIDTH = WIDTH // PIXEL_SIZE
GRID_HEIGHT = HEIGHT // PIXEL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Layered Pixel Art Noise v1")

def rand_gray(low, high):
    return random.randint(low, high)

def gen_noise(width, height):
    grid = []
    for i in range(width):
        col = []
        for j in range(height):
            val = rand_gray(80, 180)
            col.append(val)
        grid.append(col)
    return grid

def hsv_color(h, s, v):
    color = pygame.Color(0)
    color.hsva = (h, s, v, 100)
    return color

def draw_pixel(surface, x, y, color):
    rect = pygame.Rect(x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
    pygame.draw.rect(surface, color, rect)

def random_hue():
    return random.randint(0, 360)

noise_grid = gen_noise(GRID_WIDTH, GRID_HEIGHT)
colored_grid = [[None] * GRID_HEIGHT for _ in range(GRID_WIDTH)]

def apply_color_layer(grid):
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            brightness = grid[x][y]
            hue = random_hue()
            col = hsv_color(hue, 100, brightness * 100 // 255)
            colored_grid[x][y] = col

def update_colored_grid(grid, colored_grid):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            b = grid[i][j]
            h = (colored_grid[i][j].hsva[0] + 5) % 360
            s = colored_grid[i][j].hsva[1]
            v = colored_grid[i][j].hsva[2]
            colored_grid[i][j].hsva = (h, s, v, 100)

apply_color_layer(noise_grid)
clock = pygame.time.Clock()

def fade_in_surface(surface, target, speed):
    alpha = 0
    while alpha < 255:
        surface.set_alpha(alpha)
        target.blit(surface, (0, 0))
        pygame.display.flip()
        alpha += speed
        clock.tick(60)

def fade_out_surface(surface, target, speed):
    alpha = 255
    while alpha > 0:
        surface.set_alpha(alpha)
        target.blit(surface, (0, 0))
        pygame.display.flip()
        alpha -= speed
        clock.tick(60)

def noise_cell_pattern(grid, color_grid, scale):
    for cx in range(0, len(grid), scale):
        for cy in range(0, len(grid[0]), scale):
            avg = 0
            count = 0
            for ix in range(cx, min(cx + scale, len(grid))):
                for iy in range(cy, min(cy + scale, len(grid[0]))):
                    avg += grid[ix][iy]
                    count += 1
            avg = avg // count
            hue = random_hue()
            col = hsv_color(hue, 100, avg * 100 // 255)
            for ix in range(cx, min(cx + scale, len(grid))):
                for iy in range(cy, min(cy + scale, len(grid[0]))):
                    color_grid[ix][iy] = col

def edge_detect(grid):
    edges = [[0] * len(grid[0]) for _ in range(len(grid))]
    for x in range(1, len(grid) - 1):
        for y in range(1, len(grid[0]) - 1):
            diff = abs(grid[x][y] - grid[x-1][y]) + abs(grid[x][y] - grid[x+1][y]) + \
                   abs(grid[x][y] - grid[x][y-1]) + abs(grid[x][y] - grid[x][y+1])
            edges[x][y] = min(diff, 255)
    return edges

def color_edges(edges, threshold):
    edge_colors = [[None] * len(edges[0]) for _ in range(len(edges))]
    for i in range(len(edges)):
        for j in range(len(edges[0])):
            if edges[i][j] > threshold:
                hue = 0
                val = edges[i][j] * 100 // 255
                edge_colors[i][j] = hsv_color(hue, 100, val)
            else:
                edge_colors[i][j] = None
    return edge_colors

def merge_layers(base, overlay):
    for i in range(len(base)):
        for j in range(len(base[0])):
            if overlay[i][j]:
                base[i][j] = overlay[i][j]

def draw_grid(surface, color_grid):
    for x in range(len(color_grid)):
        for y in range(len(color_grid[0])):
            col = color_grid[x][y]
            if col:
                draw_pixel(surface, x, y, col)

def random_walk_noise(grid, steps):
    x, y = random.randint(0, len(grid)-1), random.randint(0, len(grid[0])-1)
    for _ in range(steps):
        grid[x][y] = min(grid[x][y] + random.randint(-20, 20), 255)
        x += random.choice([-1, 0, 1])
        y += random.choice([-1, 0, 1])
        x = max(0, min(x, len(grid)-1))
        y = max(0, min(y, len(grid[0])-1))

def smooth_noise(grid):
    temp = [[0]*len(grid[0]) for _ in range(len(grid))]
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            neighbors = []
            for nx in range(max(0, x-1), min(len(grid), x+2)):
                for ny in range(max(0, y-1), min(len(grid[0]), y+2)):
                    neighbors.append(grid[nx][ny])
            temp[x][y] = sum(neighbors)//len(neighbors)
    return temp

def invert_colors(color_grid):
    for x in range(len(color_grid)):
        for y in range(len(color_grid[0])):
            c = color_grid[x][y]
            if c:
                h, s, v, a = c.hsva
                color_grid[x][y].hsva = ((h+180) % 360, s, 100 - v, a)

def shift_hue(color_grid, shift):
    for x in range(len(color_grid)):
        for y in range(len(color_grid[0])):
            c = color_grid[x][y]
            if c:
                h, s, v, a = c.hsva
                color_grid[x][y].hsva = ((h + shift) % 360, s, v, a)

def scale_brightness(color_grid, scale):
    for x in range(len(color_grid)):
        for y in range(len(color_grid[0])):
            c = color_grid[x][y]
            if c:
                h, s, v, a = c.hsva
                nv = min(100, max(0, int(v * scale)))
                color_grid[x][y].hsva = (h, s, nv, a)

def random_color_grid(width, height):
    grid = []
    for x in range(width):
        col = []
        for y in range(height):
            c = pygame.Color(random.randint(0,255), random.randint(0,255), random.randint(0,255))
            col.append(c)
        grid.append(col)
    return grid

def pattern_blocks(grid, block_size):
    for x in range(0, len(grid), block_size):
        for y in range(0, len(grid[0]), block_size):
            color_val = random.randint(60, 200)
            hue = random_hue()
            col = hsv_color(hue, 100, color_val * 100 // 255)
            for bx in range(x, min(x+block_size, len(grid))):
                for by in range(y, min(y+block_size, len(grid[0]))):
                    grid[bx][by] = col

def random_walk_apply(grid, colored_grid, steps):
    x, y = random.randint(0, len(grid)-1), random.randint(0, len(grid[0])-1)
    for _ in range(steps):
        val = grid[x][y] + random.randint(-15, 15)
        val = max(80, min(val, 180))
        h = (colored_grid[x][y].hsva[0] + random.randint(-10,10)) % 360
        s = colored_grid[x][y].hsva[1]
        v = val * 100 // 255
        colored_grid[x][y].hsva = (h, s, v, 100)
        x += random.choice([-1,0,1])
        y += random.choice([-1,0,1])
        x = max(0, min(x, len(grid)-1))
        y = max(0, min(y, len(grid[0])-1))

def checkerboard_pattern(size1, size2):
    cb_grids = []
    for i in range(size1):
        row = []
        for j in range(size2):
            val = 120 if (i+j) % 2 == 0 else 180
            row.append(val)
        cb_grids.append(row)
    return cb_grids

def blend_colors(c1, c2, alpha):
    r = int(c1.r * (1-alpha) + c2.r * alpha)
    g = int(c1.g * (1-alpha) + c2.g * alpha)
    b = int(c1.b * (1-alpha) + c2.b * alpha)
    return pygame.Color(r, g, b)

def animate_color_shift(color_grid, shift_val):
    for x in range(len(color_grid)):
        for y in range(len(color_grid[0])):
            col = color_grid[x][y]
            if col:
                h, s, v, a = col.hsva
                color_grid[x][y].hsva = ((h + shift_val) % 360, s, v, a)

def noise_to_color_map(grid):
    color_map = []
    for x in range(len(grid)):
        col = []
        for y in range(len(grid[0])):
            gray = grid[x][y]
            hue = (gray*360//255) % 360
            c = hsv_color(hue, 100, gray * 100 // 255)
            col.append(c)
        color_map.append(col)
    return color_map

def overlay_pattern(base_grid, overlay_grid):
    for x in range(len(base_grid)):
        for y in range(len(base_grid[0])):
            o_val = overlay_grid[x][y]
            if o_val:
                base_grid[x][y] = o_val

def pixelate(surface, size):
    arr = pygame.surfarray.array3d(surface)
    w, h = arr.shape[0], arr.shape[1]
    for x in range(0, w, size):
        for y in range(0, h, size):
            block = arr[x:x+size, y:y+size]
            avg_color = block.mean(axis=(0,1)).astype(int)
            arr[x:x+size, y:y+size] = avg_color
    return pygame.surfarray.make_surface(arr)

def create_base_surface(width, height, color):
    surf = pygame.Surface((width, height))
    surf.fill(color)
    return surf

def generate_striped_pattern(width, height, stripe_width):
    pattern = []
    for x in range(width):
        col = []
        for y in range(height):
            if (x // stripe_width) % 2 == 0:
                col.append(140)
            else:
                col.append(220)
        pattern.append(col)
    return pattern

def threshold_noise(grid, thresh_low, thresh_high):
    thresh_grid = []
    for x in range(len(grid)):
        col = []
        for y in range(len(grid[0])):
            val = grid[x][y]
            if val < thresh_low:
                col.append(thresh_low)
            elif val > thresh_high:
                col.append(thresh_high)
            else:
                col.append(val)
        thresh_grid.append(col)
    return thresh_grid

def wrap_around(i, max_i):
    if i < 0:
        return max_i - 1
    elif i >= max_i:
        return 0
    else:
        return i

def spiral_pattern(radius, max_radius):
    points = []
    angle = 0
    while radius < max_radius:
        x = int(radius * math.cos(angle)) + GRID_WIDTH // 2
        y = int(radius * math.sin(angle)) + GRID_HEIGHT // 2
        points.append((wrap_around(x, GRID_WIDTH), wrap_around(y, GRID_HEIGHT)))
        radius += 0.5
        angle += math.pi / 16
    return points

def apply_spiral_to_grid(grid, points, val):
    for (x, y) in points:
        grid[x][y] = val

def invert_grid(grid):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            grid[x][y] = 255 - grid[x][y]

def generate_checker_grid(width, height, block):
    grid = []
    for x in range(width):
        row = []
        for y in range(height):
            row.append(180 if ((x // block) + (y // block)) % 2 == 0 else 100)
        grid.append(row)
    return grid

def random_walk_with_bounds(grid, steps):
    x = random.randint(0, len(grid) - 1)
    y = random.randint(0, len(grid[0]) - 1)
    for _ in range(steps):
        grid[x][y] = random.randint(90, 170)
        x = (x + random.choice([-1, 0, 1])) % len(grid)
        y = (y + random.choice([-1, 0, 1])) % len(grid[0])

def dim_grid(grid, amount):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            val = max(0, grid[x][y] - amount)
            grid[x][y] = val

def brighten_grid(grid, amount):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            val = min(255, grid[x][y] + amount)
            grid[x][y] = val

def create_surface_from_grid(grid):
    surf = pygame.Surface((WIDTH, HEIGHT))
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            shade = grid[x][y]
            col = (shade, shade, shade)
            rect = pygame.Rect(x*PIXEL_SIZE, y*PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
            pygame.draw.rect(surf, col, rect)
    return surf

def apply_random_color_to_grid(grid):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            hue = random.randint(0, 360)
            c = hsv_color(hue, 100, grid[x][y] * 100 // 255)
            grid[x][y] = c

def flood_fill(grid, start_x, start_y, old_color, new_color):
    if start_x < 0 or start_x >= len(grid) or start_y < 0 or start_y >= len(grid[0]):
        return
    if grid[start_x][start_y] != old_color:
        return
    grid[start_x][start_y] = new_color
    flood_fill(grid, start_x + 1, start_y, old_color, new_color)
    flood_fill(grid, start_x - 1, start_y, old_color, new_color)
    flood_fill(grid, start_x, start_y + 1, old_color, new_color)
    flood_fill(grid, start_x, start_y - 1, old_color, new_color)

def random_pixel_mutation(grid, steps):
    for _ in range(steps):
        x = random.randint(0, len(grid) - 1)
        y = random.randint(0, len(grid[0]) - 1)
        val = random.randint(80, 180)
        grid[x][y] = val

def oscillate_color(color_grid, amplitude, speed, frame):
    for x in range(len(color_grid)):
        for y in range(len(color_grid[0])):
            c = color_grid[x][y]
            if c:
                h, s, v, a = c.hsva
                nv = max(0, min(100, int(v + amplitude * math.sin(speed * frame + x + y))))
                color_grid[x][y].hsva = (h, s, nv, a)


def ripple_effect(grid, center_x, center_y, radius, intensity):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            dx = x - center_x
            dy = y - center_y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < radius:
                effect = int((radius - dist) / radius * intensity)
                grid[x][y] = min(255, max(0, grid[x][y] + effect))

def sinusoidal_modulation(grid, frame, frequency, amplitude):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            val = grid[x][y]
            mod = amplitude * math.sin(frequency * (x + y) + frame)
            new_val = min(255, max(0, int(val + mod)))
            grid[x][y] = new_val

def combine_grids(grid1, grid2, alpha):
    combined = []
    for x in range(len(grid1)):
        col = []
        for y in range(len(grid1[0])):
            val1 = grid1[x][y]
            val2 = grid2[x][y]
            merged = int(val1 * (1-alpha) + val2 * alpha)
            col.append(merged)
        combined.append(col)
    return combined

def random_shapes(surface, count, max_size):
    for _ in range(count):
        shape_type = random.choice(['circle', 'rect'])
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, max_size)
        color = (random.randint(40, 255), random.randint(40, 255), random.randint(40, 255))
        if shape_type == 'circle':
            pygame.draw.circle(surface, color, (x,y), size)
        else:
            rect = pygame.Rect(x, y, size, size)
            pygame.draw.rect(surface, color, rect)

def blur_grid(grid, kernel_size):
    from copy import deepcopy
    new_grid = deepcopy(grid)
    k = kernel_size // 2
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            vals = []
            for nx in range(max(0, x - k), min(len(grid), x + k + 1)):
                for ny in range(max(0, y - k), min(len(grid[0]), y + k + 1)):
                    vals.append(grid[nx][ny])
            new_grid[x][y] = sum(vals)//len(vals)
    return new_grid

def draw_gradient(surface, left_color, right_color):
    for x in range(WIDTH):
        inter = x / WIDTH
        r = int(left_color[0] * (1 - inter) + right_color[0] * inter)
        g = int(left_color[1] * (1 - inter) + right_color[1] * inter)
        b = int(left_color[2] * (1 - inter) + right_color[2] * inter)
        pygame.draw.line(surface, (r, g, b), (x, 0), (x, HEIGHT))

def flood_fill_limited(grid, x, y, old_val, new_val, limit):
    if limit <= 0:
        return 0
    if x < 0 or y < 0 or x >= len(grid) or y >= len(grid[0]):
        return 0
    if grid[x][y] != old_val:
        return 0
    grid[x][y] = new_val
    count = 1
    count += flood_fill_limited(grid, x + 1, y, old_val, new_val, limit - 1)
    count += flood_fill_limited(grid, x - 1, y, old_val, new_val, limit - 1)
    count += flood_fill_limited(grid, x, y + 1, old_val, new_val, limit - 1)
    count += flood_fill_limited(grid, x, y - 1, old_val, new_val, limit - 1)
    return count

def paint_random_lines(surface, line_count):
    for _ in range(line_count):
        start_pos = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
        end_pos = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        width = random.randint(1, 7)
        pygame.draw.line(surface, color, start_pos, end_pos, width)

def shift_grid_left(grid):
    for x in range(len(grid) - 1):
        for y in range(len(grid[0])):
            grid[x][y] = grid[x + 1][y]
    for y in range(len(grid[0])):
        grid[-1][y] = random.randint(80, 180)

def trigger_glitch(grid, intensity):
    for _ in range(intensity):
        x = random.randint(0, len(grid) - 1)
        y = random.randint(0, len(grid[0]) - 1)
        grid[x][y] = random.randint(0, 255)

def create_noise_circle(grid, center_x, center_y, radius, val):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if dist < radius:
                grid[x][y] = val

def oscillate_hue(grid, speed, frame):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            c = grid[x][y]
            if c:
                h, s, v, a = c.hsva
                new_h = int((h + speed * frame) % 360)
                grid[x][y].hsva = (new_h, s, v, a)

def multiply_grids(grid1, grid2):
    new_grid = []
    for x in range(len(grid1)):
        col = []
        for y in range(len(grid1[0])):
            val = min(grid1[x][y] * grid2[x][y] // 255, 255)
            col.append(val)
        new_grid.append(col)
    return new_grid

def generate_sine_grid(width, height, freq_x, freq_y):
    grid = []
    for x in range(width):
        col = []
        for y in range(height):
            val = int((math.sin(freq_x * x) + math.cos(freq_y * y)) * 127 + 128)
            col.append(val)
        grid.append(col)
    return grid

def horizontal_wave(grid, amplitude, speed, frame):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            val = grid[x][y]
            wave = amplitude * math.sin(2 * math.pi * (y / len(grid[0])) + speed * frame)
            new_val = max(0, min(255, int(val + wave)))
            grid[x][y] = new_val

def vertical_wave(grid, amplitude, speed, frame):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            val = grid[x][y]
            wave = amplitude * math.cos(2 * math.pi * (x / len(grid)) + speed * frame)
            new_val = max(0, min(255, int(val + wave)))
            grid[x][y] = new_val

def shift_grid_up(grid):
    for y in range(len(grid[0]) - 1):
        for x in range(len(grid)):
            grid[x][y] = grid[x][y + 1]
    for x in range(len(grid)):
        grid[x][-1] = random.randint(80, 180)

def binary_threshold(grid, threshold):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            grid[x][y] = 255 if grid[x][y] > threshold else 0

def generate_checkerboard(width, height, block_size):
    grid = []
    for x in range(width):
        col = []
        for y in range(height):
            val = 255 if ((x // block_size) + (y // block_size)) % 2 == 0 else 0
            col.append(val)
        grid.append(col)
    return grid

def repaint_grid(grid, val):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            grid[x][y] = val

def add_noise(grid, amount):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            val = grid[x][y] + random.randint(-amount, amount)
            grid[x][y] = max(0, min(255, val))

def draw_mosaic(surface, grid):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            val = grid[x][y]
            hue = val * 360 // 255
            color = hsv_color(hue, 100, val * 100 // 255)
            rect = pygame.Rect(x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
            pygame.draw.rect(surface, color, rect)

def apply_checkerboard_color_overlay(grid, threshold):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if ((x + y) % 2 == 0) and grid[x][y] > threshold:
                grid[x][y] = 255 - grid[x][y]

def jitter_grid(grid, max_jitter):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            grid[x][y] = max(0, min(255, grid[x][y] + random.randint(-max_jitter, max_jitter)))

def pixelate_surface(surface, pixel_size):
    arr = pygame.surfarray.array3d(surface)
    w, h = arr.shape[0], arr.shape[1]
    for x in range(0, w, pixel_size):
        for y in range(0, h, pixel_size):
            block = arr[x:x+pixel_size, y:y+pixel_size]
            avg_color = block.mean(axis=(0,1)).astype(int)
            arr[x:x+pixel_size, y:y+pixel_size] = avg_color
    return pygame.surfarray.make_surface(arr)

def generate_gradient_circle_grid(width, height):
    grid = []
    cx, cy = width // 2, height // 2
    max_dist = math.sqrt(cx**2 + cy**2)
    for x in range(width):
        col = []
        for y in range(height):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            val = int(255 * (1 - dist / max_dist))
            col.append(val)
        grid.append(col)
    return grid

def apply_random_sparkle(grid, count):
    for _ in range(count):
        x = random.randint(0, len(grid) - 1)
        y = random.randint(0, len(grid[0]) - 1)
        grid[x][y] = 255

def flip_grid_horizontal(grid):
    for x in range(len(grid) // 2):
        for y in range(len(grid[0])):
            grid[x][y], grid[-x-1][y] = grid[-x-1][y], grid[x][y]

def flip_grid_vertical(grid):
    for x in range(len(grid)):
        for y in range(len(grid[0]) // 2):
            grid[x][y], grid[x][-y-1] = grid[x][-y-1], grid[x][y]

def cellular_automata(grid, iterations):
    for _ in range(iterations):
        new_grid = [[0]*len(grid[0]) for _ in range(len(grid))]
        for x in range(len(grid)):
            for y in range(len(grid[0])):
                neighbors = 0
                for nx in range(max(0, x-1), min(len(grid), x+2)):
                    for ny in range(max(0, y-1), min(len(grid[0]), y+2)):
                        if nx == x and ny == y:
                            continue
                        if grid[nx][ny] > 128:
                            neighbors += 1
                if grid[x][y] > 128:
                    new_grid[x][y] = 255 if neighbors in [2, 3] else 0
                else:
                    new_grid[x][y] = 255 if neighbors == 3 else 0
        grid[:] = new_grid

def shift_grid_right(grid):
    for x in range(len(grid)-1, 0, -1):
        for y in range(len(grid[0])):
            grid[x][y] = grid[x-1][y]
    for y in range(len(grid[0])):
        grid[0][y] = random.randint(80, 180)

def draw_noise_circles(surface, grid, max_radius):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            val = grid[x][y]
            radius = int(val * max_radius / 255)
            color = hsv_color(val * 360 // 255, 100, val * 100 // 255)
            pos = (x * PIXEL_SIZE + PIXEL_SIZE // 2, y * PIXEL_SIZE + PIXEL_SIZE // 2)
            if radius > 0:
                pygame.draw.circle(surface, color, pos, radius)

def generate_radial_gradient(width, height):
    grid = []
    cx, cy = width // 2, height // 2
    for x in range(width):
        col = []
        for y in range(height):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            val = min(255, int(255 - dist * 255 / (math.sqrt(cx**2 + cy**2))))
            col.append(val)
        grid.append(col)
    return grid

def horizontal_bars_pattern(width, height, bar_height):
    grid = []
    for x in range(width):
        col = []
        for y in range(height):
            col.append(255 if (y // bar_height) % 2 == 0 else 100)
        grid.append(col)
    return grid

def vertical_bars_pattern(width, height, bar_width):
    grid = []
    for x in range(width):
        col = []
        for y in range(height):
            col.append(255 if (x // bar_width) % 2 == 0 else 100)
        grid.append(col)
    return grid

def add_noise_layer(grid, intensity):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            val = grid[x][y] + random.randint(-intensity, intensity)
            grid[x][y] = max(0, min(255, val))

def rotate_grid(grid):
    rotated = []
    for y in range(len(grid[0])):
        row = []
        for x in reversed(range(len(grid))):
            row.append(grid[x][y])
        rotated.append(row)
    return rotated

def mirror_grid(grid):
    mirrored = []
    for x in range(len(grid)):
        row = grid[x] + list(reversed(grid[x]))
        mirrored.append(row)
    return mirrored

def draw_checkerboard(surface, block_size):
    for x in range(0, WIDTH, block_size):
        for y in range(0, HEIGHT, block_size):
            color_val = 220 if ((x // block_size) + (y // block_size)) % 2 == 0 else 90
            color = (color_val, color_val, color_val)
            rect = pygame.Rect(x, y, block_size, block_size)
            pygame.draw.rect(surface, color, rect)

def draw_diagonal_lines(surface, spacing, color, thickness):
    for i in range(0, WIDTH + HEIGHT, spacing):
        start_pos = (max(0, i - HEIGHT), min(i, HEIGHT))
        end_pos = (min(i, WIDTH), max(0, i - WIDTH))
        pygame.draw.line(surface, color, start_pos, end_pos, thickness)

def random_pixels(surface, count):
    for _ in range(count):
        x = random.randint(0, WIDTH-1)
        y = random.randint(0, HEIGHT-1)
        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        surface.set_at((x, y), color)

def steady_flicker(surface, color, speed):
    current_alpha = surface.get_alpha() or 255
    new_alpha = max(0, min(255, int(current_alpha + speed)))
    surface.set_alpha(new_alpha)
    surface.fill(color)

def cycle_colors(color_list, index):
    return color_list[index % len(color_list)]

from perlin_noise import PerlinNoise

def generate_perlin_noise(width, height, scale=10, octaves=4):
    noise = PerlinNoise(octaves=octaves)
    noise_grid = []
    for x in range(width):
        col = []
        for y in range(height):
            val = noise([x / scale, y / scale])
            # val is in range [-1, 1], convert to [0, 255]
            gray = int((val + 1) / 2 * 255)
            col.append(gray)
        noise_grid.append(col)
    return noise_grid


def apply_wave_distortion(grid, amplitude, frequency, frame):
    distorted = []
    for x in range(len(grid)):
        col = []
        for y in range(len(grid[0])):
            offset = int(amplitude * math.sin(2 * math.pi * y * frequency + frame))
            src_x = (x + offset) % len(grid)
            col.append(grid[src_x][y])
        distorted.append(col)
    return distorted

def render_text(surface, text, pos, font_size, color):
    font = pygame.font.SysFont("Arial", font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_colored_grid(surface, grid):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            c = grid[x][y]
            if isinstance(c, pygame.Color):
                rect = pygame.Rect(x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
                pygame.draw.rect(surface, c, rect)
            else:
                shade = c if isinstance(c, int) else 0
                col = (shade, shade, shade)
                rect = pygame.Rect(x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
                pygame.draw.rect(surface, col, rect)

def clamped_add(val, add_val):
    return max(0, min(255, val + add_val))

def invert_surface(surface):
    arr = pygame.surfarray.array3d(surface)
    arr = 255 - arr
    return pygame.surfarray.make_surface(arr)

def noise_to_brightness_map(grid):
    brightness_map = []
    for x in range(len(grid)):
        col = []
        for y in range(len(grid[0])):
            val = grid[x][y]
            brightness = int(val * 255 // max(1, max(grid[x])))
            col.append(brightness)
        brightness_map.append(col)
    return brightness_map

def contrast_adjust(grid, factor):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            val = grid[x][y]
            val = ((val - 128) * factor) + 128
            grid[x][y] = max(0, min(255, int(val)))

# Main loop with added variants and techniques

frames = 0
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Modulate noise with sinusoidal effect
    sinusoidal_modulation(noise_grid, frames * 0.05, 0.1, 15)

    # Randomly add sparkles
    if frames % 20 == 0:
        apply_random_sparkle(noise_grid, 50)

    # Add ripple at center
    ripple_effect(noise_grid, GRID_WIDTH // 2, GRID_HEIGHT // 2, 10, 20)

    # Blur the noise grid for smoothing
    noise_grid = blur_grid(noise_grid, 3)

    # Overlay checkerboard for pattern effect
    checker = generate_checkerboard(GRID_WIDTH, GRID_HEIGHT, 5)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if checker[x][y] == 255 and noise_grid[x][y] < 150:
                noise_grid[x][y] = 150

    apply_color_layer(noise_grid)

    shift_hue(colored_grid, 1)

    screen.fill((0, 0, 0))
    draw_grid(screen, colored_grid)

    # Random shapes overlay
    if frames % 60 == 0:
        random_shapes(screen, 5, 40)

    # Paint random lines
    if frames % 100 == 0:
        paint_random_lines(screen, 10)

    pygame.display.flip()
    clock.tick(30)
    frames += 1
