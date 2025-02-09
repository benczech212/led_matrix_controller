# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_is31fl3741
from colour import Color
from adafruit_is31fl3741.adafruit_rgbmatrixqt import Adafruit_RGBMatrixQT


# i2c = board.I2C()  # uses board.SCL and board.SDA
# # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
# is31 = adafruit_is31fl3741.IS31FL3741(i2c)

# is31.set_led_scaling(0xFF)  # turn on LEDs all the way
# is31.global_current = 0xFF  # set current to max
# is31.enable = True  # enable!

# # light up every LED, one at a time


def color_to_color32(color):
    return (int(color.red * 255) << 16) | (int(color.green * 255) << 8) | int(color.blue * 255)



class IS31Driver:
    def __init__(self,brightness=0.5):
        while True:
            try:
                self.i2c = board.I2C()  # uses board.SCL and board.SDA
                # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
                self.is31 = Adafruit_RGBMatrixQT(self.i2c, allocate=adafruit_is31fl3741.PREFER_BUFFER)
                break
            except Exception as e:
                print(f"Failed to initialize RGB matrix: {e}. Retrying...")
        
        
    
        
        # get pixel count
        self.height = self.is31.height
        self.width = self.is31.width
        self.grid_size = (self.width, self.height)
        self.pixel_count = self.height * self.width
        self.pixels = [[[Color("black")] for _ in range(self.width)] for _ in range(self.height)]
        self.push_colors()
        self.is31.show()
        

        # set brightness
        self.set_brightness(brightness)
        self.is31.enable = True

    def set_brightness(self,brightness):
        self.brightness = brightness
        self.brightness_int = int(brightness * 255)
        self.is31.set_led_scaling(self.brightness_int)
        self.is31.global_current = self.brightness_int
    
    def add_color_at_xy(self, x, y, value):
        self.pixels[y][x].append(value)

    def blend_colors(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x] == []:
                    self.pixels[y][x] = [Color("black")]
                else:
                    self.pixels[y][x] = [blend_list_of_colors_using_hsl_avg(self.pixels[y][x])]
    def fade_all_pixels(self, fade_amount):
        for y in range(self.height):
            for x in range(self.width):
                self.pixels[y][x].append(Color("black"))

    def push_colors(self):
        for y in range(self.height):
            for x in range(self.width):
                self.is31.pixel(x, y, color_to_color32(self.pixels[y][x][0]))
def blend_list_of_colors_using_hsl_avg(colors):
    if len(colors) == 0:
        return Color("black")
    elif len(colors) == 1:
        return colors[0]
    else:
        h, s, l = zip(*[(c.hue, c.saturation, c.luminance) for c in colors])
        h_avg = sum(h) / len(h)
        s_avg = sum(s) / len(s)
        l_avg = sum(l) / len(l)
        return Color(hsl=(h_avg, s_avg, l_avg))



driver = IS31Driver()

tick_count = 0

while True:
    driver.add_color_at_xy(tick_count // 8 , 0, Color("red"))
    driver.add_color_at_xy(tick_count // 7, 0, Color("green"))
    driver.add_color_at_xy(2, 0, Color("blue"))
    driver.blend_colors()
    driver.push_colors()
    driver.is31.show()
    tick_count += 1
    # for y in range(9):
    #     for x in range(13):
    #         driver.is31.pixel(x, y, 0x010101)
    #         driver.is31.show()
    #         time.sleep(0.01)