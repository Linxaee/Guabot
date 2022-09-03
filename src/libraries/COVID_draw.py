from asyncio.windows_events import NULL
from email.mime import base, image
from email.policy import default
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np  # 导入必要的库函数
import pandas as pd
import re
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from pyecharts.charts import Map, Geo
from src.libraries.COVID_data import cityList, city_data
from src.libraries.image import resizePic, circle_corner


class DrawPicByCityName(object):
    def __init__(self, cityList: cityList, city_name: str):
        self.subCity = cityList.by_subCity_name(city_name)
        # 记得改
        self.pic_dir = 'src/static/COVID/'
        self.stand_font = 'src/static/adobe_simhei.otf'
        self.img = NULL
        self.draw()

    def draw(self):
        subCity = self.subCity
        base = Image.new('RGB', (820, 360), (255, 255, 255))
        baseDraw = ImageDraw.Draw(base)

        # 绘制title
        lungPng = Image.open(self.pic_dir+'lung.png')
        base.paste(lungPng, (20, 20), lungPng)
        font = ImageFont.truetype('simhei', 30, encoding='UTF-8')
        titleText = subCity.get('city_name')+'疫情动态'
        timeText = '新增数据统计周期为昨日 '+subCity.get('updateTime')+' 0-24时'
        baseDraw.text((80, 27), titleText, 'black', font)
        font = ImageFont.truetype('simhei', 18, encoding='UTF-8')
        baseDraw.text((420, 35), timeText, (145, 149, 163), font)
        # 绘制数据和小标题
        colum_margin = [100, 320, 620, 100, 360, 620]
        row_margin = [100, 220]
        data_list = [{
            "subTitle": '新增本土',
            "data": subCity.get("nativeRelative"),
            "color": (255, 106, 151)
        }, {
            "subTitle": '新增本土无症状',
            "data": subCity.get("asymptomaticLocalRelative"),
            "color": (232, 109, 72)
        }, {
            "subTitle": '现有确诊',
            "data": subCity.get("curConfirm"),
            "color": (255, 106, 151)
        }, {
            "subTitle": '累计确诊',
            "data": subCity.get("confirmed"),
            "color": (232, 49, 50)
        }, {
            "subTitle": '累计治愈',
            "data": subCity.get("cured"),
            "color": (16, 174, 181)
        }, {
            "subTitle": '累计死亡',
            "data": subCity.get("died"),
            "color": (0, 0, 0)
        }]

        for num in range(0, len(data_list)):
            data = data_list[num]

            title = data.get('subTitle')
            dataStr = data.get('data')
            font = ImageFont.truetype('simhei', 28, encoding='UTF-8')
            titleSize = font.getsize(title)[0]
            font = ImageFont.truetype('simhei', 40, encoding='UTF-8')
            dataSize = font.getsize(dataStr)[0]
            maxLen = titleSize if titleSize > dataSize else dataSize

            block = Image.new('RGB', (maxLen, 70), (255, 255, 255))
            blockDraw = ImageDraw.Draw(block)
            font = ImageFont.truetype('simhei', 28, encoding='UTF-8')
            blockDraw.text(((maxLen-titleSize)/2, 0), title, "black", font)
            font = ImageFont.truetype('simhei', 40, encoding='UTF-8')
            blockDraw.text(((maxLen-dataSize)/2, 35),
                           dataStr, data.get('color'), font)

            row = num // 3

            base.paste(block, (colum_margin[num], row_margin[row]))
        self.img = base

    def getDir(self):
        return self.img


class DrawPicByProName(object):
    def __init__(self, cityList: cityList, prov_name: str):
        self.city = cityList.by_prov_name(prov_name)
        # 记得改
        self.pic_dir = 'src/static/COVID/'
        self.stand_font = 'src/static/adobe_simhei.otf'
        self.img = NULL
        self.draw()

    def draw(self):
        city = self.city
        base = Image.new('RGB', (820, 360), (255, 255, 255))
        baseDraw = ImageDraw.Draw(base)

        # 绘制title
        lungPng = Image.open(self.pic_dir+'lung.png')
        base.paste(lungPng, (20, 20), lungPng)
        font = ImageFont.truetype('simhei', 30, encoding='UTF-8')
        titleText = city.get('prov_name')+'疫情动态'
        timeText = '新增数据统计周期为昨日 '+city.get('relativeTime')+' 0-24时'
        baseDraw.text((80, 27), titleText, 'black', font)
        font = ImageFont.truetype('simhei', 18, encoding='UTF-8')
        baseDraw.text((420, 35), timeText, (145, 149, 163), font)
        # 绘制数据和小标题
        colum_margin = [80, 240, 480, 640, 80, 290, 480, 640]
        row_margin = [100, 220]
        data_list = [{
            "subTitle": '新增本土',
            "data": city.get("nativeRelative"),
            "color": (255, 106, 151)
        }, {
            "subTitle": '新增本土无症状',
            "data": city.get("asymptomaticLocalRelative"),
            "color": (232, 109, 72)
        }, {
            "subTitle": '新增境外',
            "data": str(int(city.get('confirmedRelative'))-int(city.get("nativeRelative"))),
            "color": (232, 109, 72)
        }, {
            "subTitle": '新增确诊',
            "data": city.get("confirmedRelative"),
            "color": (255, 106, 151)
        }, {
            "subTitle": '现有确诊',
            "data": city.get("curConfirm"),
            "color": (255, 106, 151)
        }, {
            "subTitle": '累计确诊',
            "data": city.get("confirmed"),
            "color": (232, 49, 50)
        }, {
            "subTitle": '累计治愈',
            "data": city.get("cured"),
            "color": (16, 174, 181)
        }, {
            "subTitle": '累计死亡',
            "data": city.get("died"),
            "color": (0, 0, 0)
        }]

        for num in range(0, len(data_list)):
            data = data_list[num]

            title = data.get('subTitle')
            dataStr = data.get('data')
            font = ImageFont.truetype('simhei', 28, encoding='UTF-8')
            titleSize = font.getsize(title)[0]
            font = ImageFont.truetype('simhei', 40, encoding='UTF-8')
            dataSize = font.getsize(dataStr)[0]
            maxLen = titleSize if titleSize > dataSize else dataSize

            block = Image.new('RGB', (maxLen, 70), (255, 255, 255))
            blockDraw = ImageDraw.Draw(block)
            font = ImageFont.truetype('simhei', 28, encoding='UTF-8')
            blockDraw.text(((maxLen-titleSize)/2, 0), title, "black", font)
            font = ImageFont.truetype('simhei', 40, encoding='UTF-8')
            blockDraw.text(((maxLen-dataSize)/2, 35),
                           dataStr, data.get('color'), font)

            row = num // 4

            base.paste(block, (colum_margin[num], row_margin[row]))
        self.img = base

    def getDir(self):
        return self.img


async def generate(name: str):
    judgeRes = city_data.judge(name)
    if judgeRes == 0:
        return NULL, 233
    switch = {
        '1': DrawPicByCityName,
        '2': DrawPicByProName,
    }
    pic = switch.get(str(judgeRes))(city_data, name).getDir()
    return pic, 0
