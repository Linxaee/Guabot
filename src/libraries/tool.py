import math
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def hash(qq: int):
    days = int(time.strftime("%d", time.localtime(time.time()))) + 31 * int(
        time.strftime("%m", time.localtime(time.time()))) + 77
    return (days * qq) >> 8


def resizePic(img: Image.Image, time: float):
    return img.resize((int(img.size[0] * time), int(img.size[1] * time)))


def computeRa(ds: float, achievement: float, spp: bool = False) -> int:
    baseRa = 22.4 if spp else 14.0
    if achievement < 50:
        baseRa = 7.0 if spp else 0.0
    elif achievement < 60:
        baseRa = 8.0 if spp else 5.0
    elif achievement < 70:
        baseRa = 9.6 if spp else 6.0
    elif achievement < 75:
        baseRa = 11.2 if spp else 7.0
    elif achievement < 80:
        baseRa = 12.0 if spp else 7.5
    elif achievement < 90:
        baseRa = 13.6 if spp else 8.5
    elif achievement < 94:
        baseRa = 15.2 if spp else 9.5
    elif achievement < 97:
        baseRa = 16.8 if spp else 10.5
    elif achievement < 98:
        baseRa = 20.0 if spp else 12.5
    elif achievement < 99:
        baseRa = 20.3 if spp else 12.7
    elif achievement < 99.5:
        baseRa = 20.8 if spp else 13.0
    elif achievement < 100:
        baseRa = 21.1 if spp else 13.2
    elif achievement < 100.5:
        baseRa = 21.6 if spp else 13.5

    return math.floor(ds * (min(100.5, achievement) / 100) * baseRa)
