from asyncio.windows_events import NULL
from email.mime import base, image
from email.policy import default
import math
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np  # 导入必要的库函数
import pandas as pd
import re
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from pyecharts.charts import Map, Geo
from src.libraries.COVID_data import cityList, get_data, get_level_list
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
        # 圆角
        base = circle_corner(base, 20)
        baseDraw = ImageDraw.Draw(base)

        # 绘制title
        lungPng = Image.open(self.pic_dir+'lung.png')
        base.paste(lungPng, (20, 20), lungPng)
        font = ImageFont.truetype('simhei', 30, encoding='UTF-8')
        titleText = subCity.get('city_name')+'疫情动态'
        timeText = '新增数据统计周期为昨日 '+subCity.get('relativeTime')+' 0-24时'
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
        # 圆角
        base = circle_corner(base, 20)
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


class DrawPicInternal(object):
    def __init__(self, cityList: cityList, prov_name: str):
        self.city = get_data()[1]
        # 记得改
        self.pic_dir = 'src/static/COVID/'
        self.stand_font = 'static/adobe_simhei.otf'
        self.img = NULL
        self.draw()

    def draw(self):
        city = self.city['chinaTotal']
        base = Image.new('RGB', (820, 480), (255, 255, 255))
        # 圆角
        base = circle_corner(base, 20)
        baseDraw = ImageDraw.Draw(base)

        # 绘制title
        lungPng = Image.open(self.pic_dir+'lung.png')
        base.paste(lungPng, (20, 20), lungPng)
        font = ImageFont.truetype('simhei', 30, encoding='UTF-8')
        titleText = '全国疫情动态'
        timeText = '数据更新时间 ' + str(city.get('mtime'))
        baseDraw.text((80, 27), titleText, 'black', font)
        font = ImageFont.truetype('simhei', 18, encoding='UTF-8')
        baseDraw.text((420, 35), timeText, (145, 149, 163), font)
        # 绘制数据和小标题
        colum_margin = [110, 300, 570, 110, 300, 570, ]
        row_margin = [100, 220]
        data_list = [{
            "subTitle": '新增本土',
            "data": city.get("localConfirmAdd"),
            "color": (255, 106, 151)
        }, {
            "subTitle": '新增本土无症状',
            "data": city.get("localWzzAdd"),
            "color": (232, 109, 72)
        }, {
            "subTitle": '港澳台新增',
            "data": str(city.get('confirmAdd')-city.get('localConfirmAdd')),
            "color": (232, 109, 72)
        }, {
            "subTitle": '现有本土',
            "data": city.get("localConfirm"),
            "color": (255, 106, 151)
        }, {
            "subTitle": '现有本土无症状',
            "data": city.get("noInfectH5"),
            "color": (255, 106, 151)
        }, {
            "subTitle": '现有确诊',
            "data": city.get("nowConfirm"),
            "color": (232, 49, 50)
        },  {
            "subTitle": '累计确诊',
            "data": city.get("confirm"),
            "color": (232, 49, 50),
        }, {
            "subTitle": '累计境外',
            "data": city.get("importedCase"),
            "color": (71, 109, 160),
        }, {
            "subTitle": '累计治愈',
            "data": city.get("heal"),
            "color": (16, 174, 181),
        }, {
            "subTitle": '累计死亡',
            "data": city.get("dead"),
            "color": (77, 80, 84),
        }, ]

        for num in range(0, len(data_list)-4):
            data = data_list[num]

            title = str(data.get('subTitle'))
            dataStr = str(data.get('data'))
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

        # 绘制下半部分
        baseDraw.line([(20, 330), (800, 330)], (145, 149, 163), width=0)
        colum_margin = [90, 280, 450, 620]
        row_margin = 360

        for num in range(0, 4):
            data = data_list[num+6]

            title = str(data.get('subTitle'))
            dataStr = str(data.get('data'))
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

            base.paste(block, (colum_margin[num], row_margin))
        self.img = base

    def getDir(self):
        return self.img


def DrawPicByQueryCity(city, subName: Optional[str], curPage: Optional[int] = 1):
    subList = get_level_list(city['city_name'])
    totalPage = 1
    pageNum = 40
    totalNum = highLevelNum = midLevelNum = 0
    resList = []
    # flag判断返回类型
    flag = 0
    for item in subList:

        if subName != '':
            if subName in item['area']:
                totalNum += 1
                highLevelNum = highLevelNum + \
                    1 if item['level'] == '高风险' else highLevelNum
                midLevelNum = midLevelNum + \
                    1 if item['level'] == '中风险' else midLevelNum
                area = {}
                area['address'] = item['area']
                area['level'] = item['level']
                resList.append(area)
        else:
            totalNum += 1
            highLevelNum = highLevelNum + \
                1 if item['level'] == '高风险' else highLevelNum
            midLevelNum = midLevelNum + \
                1 if item['level'] == '中风险' else midLevelNum
            area = {}
            area['address'] = item['area']
            area['level'] = item['level']
            resList.append(area)
    # print(len(resList))
    if len(resList) == 0:
        return NULL, 666
    totalPage = math.ceil(totalNum / pageNum)
    totalPage = totalPage if totalPage > 0 else 1
    if curPage > totalPage:
        curPage = 1
        # 233为页越界
        flag = 233
    resList = resList[(curPage-1)*pageNum:curPage*pageNum]
    # 空白背景
    imgH = 880
    imgW = 650
    base = Image.new('RGB', (imgW, imgH), (255, 255, 255))
    baseDraw = ImageDraw.Draw(base)

    # 绘制title
    font = ImageFont.truetype('simhei', 22, encoding='UTF-8')
    areaName = subName if subName != ''else city['city_name']
    title = f'{areaName}共有风险区: {totalNum} 个,其中高风险 {highLevelNum} 个,中风险 {midLevelNum} 个'
    baseDraw.text((10, 20), title, 'black', font)
    # 绘制主体
    font = ImageFont.truetype('simhei', 14, encoding='UTF-8')
    for i in range(0, len(resList)):
        area = resList[i]
        if area["level"] == '高风险':
            level = area["level"]
            address = area["address"]
            baseDraw.text((12, i*20+55), level, 'red', font)
            baseDraw.text((60, i*20+55), address, 'black', font)
        else:
            area = resList[i]
            level = area["level"]
            address = area["address"]
            baseDraw.text((12, i*20+55), level, (212, 161, 58), font)
            baseDraw.text((60, i*20+55), address, 'black', font)
    # 绘制页数结尾
    font = ImageFont.truetype('simhei', 18, encoding='UTF-8')
    footer = f'{curPage}/{totalPage}页 {pageNum}项每页 generated by Guabot & Linxae'
    baseDraw.text((12, imgH-20), footer, 'black', font)

    if flag == 0:
        return base, 0
    elif flag == 233:
        return base, 233
    else:
        return NULL, 404


async def generate(name: str):
    city_data, internal_data = get_data()
    judgeRes = city_data.judge(name)
    if judgeRes == 0:
        return NULL, 233
    switch = {
        '1': DrawPicByCityName,
        '2': DrawPicByProName,
        '3': DrawPicInternal,
    }
    pic = switch.get(str(judgeRes))(city_data, name).getDir()
    return pic, 0
