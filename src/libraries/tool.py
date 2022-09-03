import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def hash(qq: int):
    days = int(time.strftime("%d", time.localtime(time.time()))) + 31 * int(
        time.strftime("%m", time.localtime(time.time()))) + 77
    return (days * qq) >> 8


def resizePic(img: Image.Image, time: float):
    return img.resize((int(img.size[0] * time), int(img.size[1] * time)))
