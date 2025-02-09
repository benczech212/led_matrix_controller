
import board
import time
from rainbowio import colorwheel
from adafruit_is31fl3741.adafruit_rgbmatrixqt import Adafruit_RGBMatrixQT
import adafruit_is31fl3741

def color32_to_rgb(color):
    return (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF

def rgb_to_color32(rgb):
    return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]

def lerp(a, b, t):
    return a + (b - a) * t
def lerp_color_rgb(a, b, t):
    return tuple(int(lerp(a[i], b[i], t)) for i in range(3))
def rgb_to_hsv(rgb):
    r, g, b = rgb
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin
    if cmax == r:
        h = 60 * (((g - b) / delta) % 6)
    elif cmax == g:
        h = 60 * (((b - r) / delta) + 2)
    else:
        h = 60 * (((r - g) / delta) + 4)
    if cmax == 0:
        s = 0
    else:
        s = delta / cmax
    v = cmax
    return (h, s, v)
def hsv_to_rgb(hsv):
    h, s, v = hsv
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        rgb = (c, x, 0)
    elif h < 120:
        rgb = (x, c, 0)
    elif h < 180:
        rgb = (0, c, x)
    elif h < 240:
        rgb = (0, x, c)
    elif h < 300:
        rgb = (x, 0, c)
    else:
        rgb = (c, 0, x)
    return tuple(int((c + m) * 255) for c in rgb)

def lerp_color_hsv(a, b, t):
    a_hsv = rgb_to_hsv(a)
    b_hsv = rgb_to_hsv(b)
    lerp_hsv = tuple(lerp(a_hsv[i], b_hsv[i], t) for i in range(3))
    return hsv_to_rgb(lerp_hsv)
def blend_list_of_rgb_colors(colors):
    if len(colors) == 0:
        return (0, 0, 0)
    elif len(colors) == 1:
        return colors[0]
    else:
        r = sum([color[0] for color in colors]) // len(colors)
        g = sum([color[1] for color in colors]) // len(colors)
        b = sum([color[2] for color in colors]) // len(colors)
        return (r, g, b)

def blend_list_of_hsv_colors(colors):
    if len(colors) == 0:
        return (0, 0, 0)
    elif len(colors) == 1:
        return colors[0]
    else:
        h, s, v = zip(*colors)
        h_avg = sum(h) / len(h)
        s_avg = sum(s) / len(s)
        v_avg = sum(v) / len(v)
        return (h_avg, s_avg, v_avg)


class IS31Driver:
    def __init__(self,brightness=0.5,orientation=0):
        self.i2c = board.I2C()
        self.is31 = Adafruit_RGBMatrixQT(self.i2c, allocate=adafruit_is31fl3741.PREFER_BUFFER)
        
        # get pixel count
        self.height = self.is31.height
        self.width = self.is31.width
        self.grid_size = (self.width, self.height)
        self.pixel_count = self.height * self.width
        self.pixels = [[[] for _ in range(self.width)] for _ in range(self.height)]
        self.clear_pixel_buffer()

        # set brightness
        self.set_brightness(brightness)
        self.is31.enable = True  # enable!
        # set orientation
        self.orientation = orientation
        

    def set_brightness(self,brightness):
        self.brightness = brightness
        self.brightness_int = int(brightness * 255)
        self.is31.set_led_scaling(self.brightness_int)
        self.is31.global_current = self.brightness_int

    def add_color_at_xy(self, x, y, value):
        self.pixels[y][x].append(value)
        

    def get_pixel(self, x, y):
        return self.pixels[y][x]

    def clear_pixel_buffer(self):
        self.pixels_buffer = [[0 for _ in range(self.width)] for _ in range(self.height)]
        

    def show(self):
        # blend all colors at each pixel position
        self.clear_pixel_buffer()
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x] == []:
                    self.pixels_buffer[y][x] = 0
                else:
                    new_color = blend_list_of_rgb_colors(self.pixels[y][x])
                    self.pixels_buffer[y][x] = rgb_to_color32(new_color)
                    self.pixels[y][x] = [new_color]
        # show pixels
        for y in range(self.height):
            for x in range(self.width):
                self.is31.pixel(x, y, self.pixels_buffer[y][x])
        self.is31.show()


                    



# driver = IS31Driver()
i2c = board.I2C()
is31 = Adafruit_RGBMatrixQT(i2c, allocate=adafruit_is31fl3741.PREFER_BUFFER)
tick_count = 0
while True:
    # driver.add_color_at_xy(0,0,(255,0,0))
    is31.pixel(4, 4, colorwheel(tick_count % 256))
    is31.show()
    tick_count += 1