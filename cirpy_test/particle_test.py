# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import random
import math
from rainbowio import colorwheel

from adafruit_is31fl3741.adafruit_rgbmatrixqt import Adafruit_RGBMatrixQT
import adafruit_is31fl3741

while True:
    try:
        i2c = board.I2C()  # uses board.SCL and board.SDA
        # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        is31 = Adafruit_RGBMatrixQT(i2c, allocate=adafruit_is31fl3741.PREFER_BUFFER)
        break
    except Exception as e:
        print(f"Failed to initialize RGB matrix: {e}. Retrying...")

brightness = 0.1
brightess_int = int(brightness * 255)

is31.set_led_scaling(brightess_int)
is31.global_current = brightess_int
is31.enable = True

x_count = 13
y_count = 9
grid_size = (x_count, y_count)

class PixelBuffer:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.pixels = [[0 for _ in range(grid_size[0])] for _ in range(grid_size[1])]

    def set_pixel(self, x, y, value):
        self.pixels[y][x] = value
        is31.pixel(x, y, value)

    def get_pixel(self, x, y):
        return self.pixels[y][x]

class Grid:
    def __init__(self, grid_size, particles=[]):
        self.grid_size = grid_size
        self.grid = [[None for _ in range(grid_size[0])] for _ in range(grid_size[1])]
        self.particles = particles

    def clear_grid(self):
        self.grid = [[None for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

    def add_particle(self, particle):
        if len(self.particles) < 5:  # Restrict to 5 particles
            self.particles.append(particle)

    def update(self):
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)

    def fade_pixels(self):
        for y in range(self.grid_size[1]):
            for x in range(self.grid_size[0]):
                current_color = px_buf.get_pixel(x, y)  # Get current pixel color
                r = (current_color >> 16) & 0xFF
                g = (current_color >> 8) & 0xFF
                b = current_color & 0xFF
                current_rgb = (r, g, b)
                if current_rgb != (0, 0, 0):  # Only fade if pixel is not black
                    faded_rgb = tuple(int(c * 0.9) for c in current_rgb)  # Apply fading
                    faded_color = (faded_rgb[0] << 16) | (faded_rgb[1] << 8) | faded_rgb[2]
                    px_buf.set_pixel(x, y, faded_color)

    def draw(self):
        self.clear_grid()
        for particle in self.particles:
            x, y = particle.position_int
            if 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]:
                if self.grid[y][x] is None:  # Only place particle if grid cell is empty
                    self.grid[y][x] = particle
                    faded_hue = int(particle.hue * ((particle.lifetime - particle.age) / particle.lifetime))
                    color = colorwheel(faded_hue)
                    px_buf.set_pixel(x, y, color)
        self.fade_pixels()  # Apply fading to the entire grid
        is31.show()

class Particle:
    def __init__(self, position, hue, velocity=(0.5, random.uniform(0.05, 0.2)), gravity=(0, 0), friction=(0, 0), grid_size=grid_size, size=1, lifetime=120, hue_offset = random.randint(0, 12)):
        self.position_float = position
        self.hue = hue
        self.hue_offset = hue_offset
        self.velocity = velocity
        self.gravity = gravity
        self.friction = friction
        self.grid_size = grid_size
        self.size = 1  # Force particles to be 1 pixel in size
        self.age = 0
        self.lifetime = lifetime
        self.wall_collisions = False

    def update(self):
        center_x, center_y = self.grid_size[0] // 2, self.grid_size[1] // 2
        dx = center_x - self.position_float[0]
        dy = center_y - self.position_float[1]
        self.hue = tick_count + self.hue_offset
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            gravitational_force = 0.02  # Increased force for stronger attraction
            self.velocity = (self.velocity[0] + gravitational_force * dx / distance, self.velocity[1] + gravitational_force * dy / distance)

        # Apply velocity to update position
        self.position_float = (self.position_float[0] + self.velocity[0], self.position_float[1] + self.velocity[1])
        self.position_int = (int(self.position_float[0]), int(self.position_float[1]))
        self.age += 1

        if self.age > self.lifetime:
            return False  # Particle should be removed

        # Handle wall collisions
        if self.wall_collisions:
            if self.position_int[0] < 0 or self.position_int[0] >= self.grid_size[0]:
                self.velocity = (-self.velocity[0], self.velocity[1])
            if self.position_int[1] < 0 or self.position_int[1] >= self.grid_size[1]:
                self.velocity = (self.velocity[0], -self.velocity[1])

        return True  # Particle is still active

class ParticleSpawner:
    def __init__(self):
        self.spawned_particles = 0

    def spawn_particle(self, position=(0, 0)):
        # if self.spawned_particles < 1024:
        self.spawned_particles += 1
        hue = tick_count // 64 + random.randint(0, 12)
        return Particle(position, hue=hue, velocity=(0, random.uniform(0.05, 0.2)), lifetime=random.randint(150, 2000))
        # return None

px_buf = PixelBuffer(grid_size)
grid = Grid(grid_size)
spawner = ParticleSpawner()
tick_count = 0
# Main loop
while True:
    grid.clear_grid()
    new_particle = spawner.spawn_particle()
    if new_particle:
        grid.add_particle(new_particle)  # Only add if particle count < 5
    grid.update()
    grid.draw()
    # for partice in grid.particles:
    #     partice.velocity = (partice.velocity[0] * 1.01, partice.velocity[1] * 1.01)
    #     partice.gravity = (partice.gravity[0] * 1.1, partice.gravity[1] * 1.1)
    # is31.fill(0)
    tick_count += 1