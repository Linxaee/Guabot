from asyncio.windows_events import NULL
from importlib.metadata import version
import os
import math
import random
from typing import Optional, Dict, List

import requests
from urllib import request
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.libraries.maimaidx_music import *
from src.libraries.tool import *
from src.libraries.image import *

scoreRank = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
combo = ' FC FC+ AP AP+'.split(' ')
diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')


def mix_list(sssp_list, sss_list, floor):
    res_list = []
    sssp_temp = []
    sss_temp = []
    sssp_res = []
    sss_res = []
    # print(sssp_list)
    if len(sssp_list) > 2:
        for item in sssp_list:
            target_ra = computeRa(item.ds, 100.5)
            if item.achievement != 0:
                music_ra = computeRa(item.ds, item.achievement)
                if target_ra - music_ra <= 8 and target_ra - music_ra >= 3:
                    sssp_temp.append(item)
            else:
                if target_ra - floor <= 8 and target_ra - floor >= 3:
                    sssp_temp.append(item)
        if len(sssp_temp) >= 2:
            sssp_res = random.sample(sssp_temp, 2)
        else:
            while len(sssp_temp) < 2:
                sssp_temp.append(random.choice(sssp_list))
            for item in sssp_temp:
                sssp_res.append(item)
    else:
        sssp_res = sssp_list
    if len(sss_list) > 2:
        for item in sss_list:
            target_ra = computeRa(item.ds, 100)
            if item.achievement != 0:
                music_ra = computeRa(item.ds, item.achievement)
                if target_ra - music_ra <= 8 and target_ra - music_ra >= 3:
                    sss_temp.append(item)
            else:
                if target_ra - floor <= 8 and target_ra - floor >= 3:

                    sss_temp.append(item)
        if len(sss_temp) >= 2:
            sss_res = random.sample(sss_temp, 2)
        else:
            while len(sss_temp) < 2:
                sss_temp.append(random.choice(sss_list))
            for item in sss_temp:
                sss_res.append(item)
    else:
        sss_res = sss_list
    for item in sssp_res:
        res_list.append(item)
    for item in sss_res:
        res_list.append(item)
    return res_list

# 达成率转化score序号


def trans_score_id(achievement):
    if achievement >= 100.5:
        return 13
    elif achievement >= 100:
        return 12
    elif achievement >= 99.5:
        return 11
    elif achievement >= 99:
        return 10
    elif achievement >= 98:
        return 9
    elif achievement >= 97:
        return 8
    elif achievement >= 94:
        return 7
    elif achievement >= 90:
        return 6
    elif achievement >= 80:
        return 5
    elif achievement >= 75:
        return 4
    elif achievement >= 70:
        return 3
    elif achievement >= 60:
        return 2
    elif achievement >= 50:
        return 1
    else:
        return 0
# 绘制无推荐时替代图


def draw_temp_pic():

    # 绘制sd区域
    itemW = 310
    itemH = 180

    pic_dir = 'src/static/dragon/'
    cover_dir = 'src/static/mai/cover/'

    # 绘制模糊背景
    pngPath = pic_dir + '0.png'
    tempImg = Image.open(pngPath).convert('RGB')
    tempImg = resizePic(tempImg, itemW / tempImg.size[0])
    tempImg = tempImg.crop(
        (0, (tempImg.size[1] - itemH) / 2, itemW, (tempImg.size[1] + itemH) / 2))
    tempImg = tempImg.filter(ImageFilter.GaussianBlur(5))
    tempImg = circle_corner(tempImg, 30)

    tempDraw = ImageDraw.Draw(tempImg)
    fontName = 'src/static/mht.ttf'
    font = ImageFont.truetype(fontName, 58, encoding='utf-8')
    # 计算出要写入的文字占用的像素
    Text = '暂无推荐'
    w, h = font.getsize(Text)
    text_border(tempDraw, (tempImg.size[0]-w)/2, (tempImg.size[1]-h)/2,
                font, 'black', 'white', '暂无推荐')
    # tempImg.show()
    return tempImg


class ChartInfo(object):
    def __init__(self, idNum: str, diff: int, tp: str, achievement: float, ra: int, comboId: int, scoreId: int,
                 title: str, ds: float, lv: str):
        self.idNum = idNum
        self.diff = diff
        self.tp = tp
        self.achievement = achievement
        self.ra = ra
        self.comboId = comboId
        self.scoreId = scoreId
        self.title = title
        self.ds = ds
        self.lv = lv

    def __str__(self):
        return '%-50s' % f'{self.title} [{self.tp}]' + f'{self.ds}\t{diffs[self.diff]}\t{self.ra}'

    def __eq__(self, other):
        return self.ra == other.ra

    def __lt__(self, other):
        return self.ra < other.ra

    @classmethod
    def from_json(cls, data):
        rate = ['d', 'c', 'b', 'bb', 'bbb', 'a', 'aa',
                'aaa', 's', 'sp', 'ss', 'ssp', 'sss', 'sssp']
        ri = rate.index(data["rate"])
        fc = ['', 'fc', 'fcp', 'ap', 'app']
        fi = fc.index(data["fc"])
        return cls(
            idNum=total_list.by_title(data["title"]).id,
            title=data["title"],
            diff=data["level_index"],
            ra=data["ra"],
            ds=data["ds"],
            comboId=fi,
            scoreId=ri,
            lv=data["level"],
            achievement=data["achievements"],
            tp=data["type"]
        )


class BestList(object):
    def __init__(self, size: int):
        self.data = []
        self.size = size

    def push(self, elem: ChartInfo):
        if len(self.data) >= self.size and elem < self.data[-1]:
            return
        self.data.append(elem)
        self.data.sort()
        self.data.reverse()
        while (len(self.data) > self.size):
            del self.data[-1]

    def pop(self):
        del self.data[-1]

    def __str__(self):
        return '[\n\t' + ', \n\t'.join([str(ci) for ci in self.data]) + '\n]'

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def find_by_id(self, id, diff):
        for item in self.data:
            if int(item.idNum) == id and diff == item.diff:
                return item.idNum
        return -1

    def get_by_id(self, id):
        for item in self.data:
            if int(item.idNum) == id:
                return item
        return NULL

    def is_np(self, id):
        music = self.get_by_id(id)
        if music.achievement >= 100.5000:
            return True
        else:
            return False

    def is_n(self, id):
        music = self.get_by_id(id)
        if music.achievement >= 100.0000:
            return True
        else:
            return False


# 绘制底分分析

async def draw_recommend_pic(payload: Dict):
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403
        sd_best = BestList(25)
        dx_best = BestList(15)
        obj = await resp.json()
        userId = obj['nickname']
        dx: List[Dict] = obj["charts"]["dx"]
        sd: List[Dict] = obj["charts"]["sd"]
        curRating = obj["rating"]
        additional_rating = obj["additional_rating"]
        dx_ra = sd_ra = 0
        dx_top = dx[0]['ra']
        dx_floor = dx[0]['ra']
        sd_top = sd[0]['ra']
        sd_floor = sd[0]['ra']
        for c in sd:
            sd_floor = c['ra']if c['ra'] < sd_floor else sd_floor
            sd_top = c['ra']if c['ra'] > sd_top else sd_top
            sd_ra += c['ra']
            sd_best.push(ChartInfo.from_json(c))
        for c in dx:
            dx_floor = c['ra']if c['ra'] < dx_floor else dx_floor
            dx_top = c['ra']if c['ra'] > dx_top else dx_top
            dx_ra += c['ra']
            dx_best.push(ChartInfo.from_json(c))
        sd_recommend_list_sssp = []
        sd_recommend_list_sss = []
        dx_recommend_list_sssp = []
        dx_recommend_list_sss = []
        # 筛选推荐列表表
        # 先筛选出所有符合条件的乐曲：
        # 一、乐曲ra（鸟和鸟加分别判断）>地板
        # 二、若乐曲存在于b40中判断是否鸟/鸟加，未鸟则加入鸟推荐
        # 三、若鸟ra满足且已鸟则判断是否鸟加，未鸟加则加入鸟加推荐
        # 四、若不存在于b40中则且乐曲ra（鸟和鸟加分别判断）>地板，则直接加入对应推荐
        for music in total_list:
            if music.is_new:
                for ds in music.ds:
                    achievement = 0
                    music_ra = computeRa(ds, 100)
                    # 判断定数是否在鸟推荐范围内
                    if music_ra > dx_floor:
                        ds_index = music.ds.index(ds)
                        # 判断是否已经再best中
                        if dx_best.find_by_id(int(music.id), ds_index) != -1:
                            # 判断是否鸟，鸟则交给鸟加处理
                            if dx_best.is_n(int(music.id)):
                                # 判断是否鸟加
                                if dx_best.is_np(int(music.id)):
                                    continue
                                else:
                                    # 判断定数是否在鸟加推荐范围内
                                    music_ra = computeRa(ds, 100.5)
                                    if music_ra > dx_floor:
                                        ds_index = music.ds.index(ds)
                                        # 判断是否已经再best中
                                        if dx_best.find_by_id(int(music.id), ds_index) != -1:
                                            # 判断是否鸟加，鸟加则跳过
                                            if dx_best.is_np(int(music.id)):
                                                continue
                                            else:
                                                achievement = dx_best.get_by_id(
                                                    int(music.id)).achievement
                                                cur_music = rc_music(
                                                    {'id': music.id, 'title': music.title, 'ds': ds, 'level': music.level[ds_index],  'genre': music.genre, 'type': music.type, 'achievement': achievement, 'is_new': music.is_new, 'artist': music.artist, 'target': 'sssp', 'diff': ds_index, 'diffs_label': diffs[ds_index]})
                                                dx_recommend_list_sssp.append(
                                                    cur_music)
                                                continue
                                        cur_music = rc_music(
                                            {'id': music.id, 'title': music.title, 'ds': ds, 'level': music.level[ds_index],  'genre': music.genre, 'type': music.type, 'achievement': achievement, 'is_new': music.is_new, 'artist': music.artist, 'target': 'sssp', 'diff': ds_index, 'diffs_label': diffs[ds_index]})
                                        dx_recommend_list_sssp.append(
                                            cur_music)
                                        continue
                            else:
                                achievement = dx_best.get_by_id(
                                    int(music.id)).achievement
                                cur_music = rc_music(
                                    {'id': music.id, 'title': music.title, 'ds': ds, 'level': music.level[ds_index],  'genre': music.genre, 'type': music.type, 'achievement': achievement, 'is_new': music.is_new, 'artist': music.artist, 'target': 'sss', 'diff': ds_index, 'diffs_label': diffs[ds_index]})
                                dx_recommend_list_sss.append(cur_music)
                                continue
                        else:
                            cur_music = rc_music(
                                {'id': music.id, 'title': music.title, 'ds': ds, 'level': music.level[ds_index],  'genre': music.genre, 'type': music.type, 'achievement': achievement, 'is_new': music.is_new, 'artist': music.artist, 'target': 'sss', 'diff': ds_index, 'diffs_label': diffs[ds_index]})
                            dx_recommend_list_sss.append(cur_music)
                            continue
                    else:
                        # 判断定数是否在鸟加推荐范围内
                        music_ra = computeRa(ds, 100.5)
                        if music_ra > dx_floor:
                            ds_index = music.ds.index(ds)
                            # 判断是否已经再best中
                            if dx_best.find_by_id(int(music.id), ds_index) != -1:
                                # 判断是否鸟加，鸟加则跳过
                                if dx_best.is_np(int(music.id)):
                                    continue
                                else:
                                    achievement = dx_best.get_by_id(
                                        int(music.id)).achievement
                                    cur_music = rc_music(
                                        {'id': music.id, 'title': music.title, 'ds': ds, 'level': music.level[ds_index],  'genre': music.genre, 'type': music.type, 'achievement': achievement, 'is_new': music.is_new, 'artist': music.artist, 'target': 'sssp', 'diff': ds_index, 'diffs_label': diffs[ds_index]})
                                    dx_recommend_list_sssp.append(
                                        cur_music)
                                    continue
                            cur_music = rc_music(
                                {'id': music.id, 'title': music.title, 'ds': ds, 'level': music.level[ds_index],  'genre': music.genre, 'type': music.type, 'achievement': achievement, 'is_new': music.is_new, 'artist': music.artist, 'target': 'sssp', 'diff': ds_index, 'diffs_label': diffs[ds_index]})
                            dx_recommend_list_sssp.append(cur_music)
                            continue

            else:
                for ds in music.ds:
                    achievement = 0
                    music_ra = computeRa(ds, 100)
                    # 判断定数是否在鸟推荐范围内
                    if music_ra > sd_floor:
                        ds_index = music.ds.index(ds)
                        # 判断是否已经再best中
                        if sd_best.find_by_id(int(music.id), ds_index) != -1:
                            # 判断是否鸟，鸟则交给鸟加处理
                            if sd_best.is_n(int(music.id)):
                                # 判断是否鸟加
                                if sd_best.is_np(int(music.id)):
                                    continue
                                else:
                                    # 判断定数是否在鸟加推荐范围内
                                    music_ra = computeRa(ds, 100.5)
                                    if music_ra > sd_floor:

                                        ds_index = music.ds.index(ds)
                                        # 判断是否已经再best中
                                        if sd_best.find_by_id(int(music.id), ds_index) != -1:
                                            # 判断是否鸟加，鸟加则跳过
                                            if sd_best.is_np(int(music.id)):
                                                continue
                                            else:
                                                achievement = sd_best.get_by_id(
                                                    int(music.id)).achievement
                                                cur_music = rc_music(
                                                    {'id': music.id, 'title': music.title, 'ds': ds, 'level': music.level[ds_index],  'genre': music.genre, 'type': music.type, 'achievement': achievement, 'is_new': music.is_new, 'artist': music.artist, 'target': 'sssp', 'diff': ds_index, 'diffs_label': diffs[ds_index]})
                                                sd_recommend_list_sssp.append(
                                                    cur_music)
                                                continue
                                        cur_music = rc_music(
                                            {'id': music.id, 'title': music.title, 'ds': ds, 'level': music.level[ds_index],  'genre': music.genre, 'type': music.type, 'achievement': achievement, 'is_new': music.is_new, 'artist': music.artist, 'target': 'sssp',  'diff': ds_index, 'diffs_label': diffs[ds_index]})
                                        sd_recommend_list_sssp.append(
                                            cur_music)
                                        continue
                            else:
                                achievement = sd_best.get_by_id(
                                    int(music.id)).achievement
                                cur_music = rc_music(
                                    {'id': music.id, 'title': music.title, 'ds': ds, 'level': music.level[ds_index],  'genre': music.genre, 'type': music.type, 'achievement': achievement, 'is_new': music.is_new, 'artist': music.artist, 'target': 'sss', 'diff': ds_index, 'diffs_label': diffs[ds_index]})
                                sd_recommend_list_sss.append(cur_music)
                                continue
                        else:
                            cur_music = rc_music(
                                {'id': music.id, 'title': music.title, 'ds': ds, 'level': music.level[ds_index],  'genre': music.genre, 'type': music.type, 'achievement': achievement, 'target': 'sss', 'is_new': music.is_new, 'artist': music.artist, 'diff': ds_index, 'diffs_label': diffs[ds_index]})
                            sd_recommend_list_sss.append(cur_music)
                            continue
                    else:
                        # 判断定数是否在鸟加推荐范围内
                        music_ra = computeRa(ds, 100.5)
                        if music_ra > sd_floor:
                            ds_index = music.ds.index(ds)
                            # 判断是否已经再best中
                            if sd_best.find_by_id(int(music.id), ds_index) != -1:
                                # 判断是否鸟加，鸟加则跳过
                                if sd_best.is_np(int(music.id)):
                                    continue
                                else:
                                    achievement = sd_best.get_by_id(
                                        int(music.id)).achievement
                                    cur_music = rc_music(
                                        {'id': music.id, 'title': music.title, 'ds': ds, 'level': music.level[ds_index],  'genre': music.genre, 'type': music.type, 'achievement': achievement, 'is_new': music.is_new, 'artist': music.artist, 'target': 'sssp', 'diff': ds_index, 'diffs_label': diffs[ds_index]})
                                    sd_recommend_list_sssp.append(
                                        cur_music)
                                    continue
                            cur_music = rc_music(
                                {'id': music.id, 'title': music.title, 'ds': ds, 'level': music.level[ds_index],  'genre': music.genre, 'type': music.type, 'achievement': achievement, 'is_new': music.is_new, 'artist': music.artist, 'target': 'sssp',  'diff': ds_index, 'diffs_label': diffs[ds_index]})
                            sd_recommend_list_sssp.append(cur_music)
                            continue

        sd_list = mix_list(sd_recommend_list_sssp,
                           sd_recommend_list_sss, sd_floor)
        dx_list = mix_list(dx_recommend_list_sssp,
                           dx_recommend_list_sss, dx_floor)

        # 绘制背景
        pic_dir = 'src/static/mai/pic/'
        cover_dir = 'src/static/mai/cover/'
        fontName = 'src/static/mht.ttf'
        adobe = 'src/static/adobe_simhei.otf'
        baseImg = Image.open(
            pic_dir + 'gua_bg2.jpeg').convert('RGBA').filter(ImageFilter.GaussianBlur(3))
        # w1280 h914
        baseImg = baseImg.resize((1280, 914), Image.ANTIALIAS)
        baseDraw = ImageDraw.Draw(baseImg)
        # 绘制title
        # 绘制推荐主体
        # 绘制sd区域
        itemW = 310
        itemH = 180
        rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
        diffPic = 'BSC ADV EXP MST MST_Re'.split(' ')

        position_sd = [(50, 50), (385, 50), (50, 255), (385, 255)]
        if len(sd_list) != 4:
            for i in range(len(dx_list), 4):
                tempImg = draw_temp_pic()
                baseImg.paste(
                    tempImg, position_sd[i], tempImg)

        for num in range(0, len(sd_list)):
            chartInfo = sd_list[num]
            # print(chartInfo)
            id = chartInfo['id']
            # 绘制模糊背景
            pngPath = cover_dir + \
                f'{get_cover_len4_id(id)}.jpeg'
            if not os.path.exists(pngPath):
                pngPath = cover_dir + '0031.jpeg'
            chartImg = Image.open(pngPath).convert('RGB')
            chartImg = resizePic(chartImg, itemW / chartImg.size[0])
            chartImg = chartImg.crop(
                (0, (chartImg.size[1] - itemH) / 2, itemW, (chartImg.size[1] + itemH) / 2))
            chartImg = chartImg.filter(ImageFilter.GaussianBlur(3))
            chartImg = circle_corner(chartImg, 30)
            baseDraw = ImageDraw.Draw(chartImg)

            # 绘制难度和版本
            diff = chartInfo.diff
            if diff == 4:
                offsetX = 3
            else:
                offsetX = -6
            diffPng = Image.open(
                pic_dir + f'UI_PFC_MS_Info02_{diffPic[diff]}.png')
            diffPng = resizePic(diffPng, 1.3)
            chartImg.paste(diffPng, (offsetX, 5), diffPng)
            if chartInfo['type'] == 'DX':
                versionPng = Image.open(
                    pic_dir + 'UI_UPE_Infoicon_DeluxeMode.png')
            else:
                versionPng = Image.open(
                    pic_dir + 'UI_UPE_Infoicon_StandardMode.png')
            versionPng = resizePic(versionPng, 1)
            chartImg.paste(versionPng, (185, 5), versionPng)

            # 绘制title
            title = chartInfo.title
            if columWidth(title) > 15:
                title = changeColumnWidth(title, 14) + '...'
            titleFont = ImageFont.truetype(adobe, 22, encoding='utf-8')
            detailFont = ImageFont.truetype(fontName, 22, encoding='utf-8')
            text_border(baseDraw, 10, 40,
                        titleFont, 'black', 'white', title)
            # 绘制定数
            text_border(baseDraw, 215, 40,
                        detailFont, 'black', 'white', '定数:' + str(chartInfo.ds))
            # 绘制曲包
            genre = chartInfo.genre
            if 'Project' in genre:
                genre = '东方Project'
            if 'CHUNI' in genre:
                genre = 'CHUNITHM'
            if columWidth(genre) > 14:
                genre = changeColumnWidth(genre, 13) + '...'

            text_border(baseDraw, 10, 75,
                        detailFont, 'black', 'white', '分类:' + str(genre))
            # 绘制等级
            text_border(baseDraw, 215, 75,
                        detailFont, 'black', 'white', 'id:' + str(chartInfo.id))

            # 绘制rank
            achievement = 0
            if chartInfo.target == 'sss':
                rankPng = Image.open(
                    pic_dir + f'UI_GAM_Rank_SSS.png').convert('RGBA')
                achievement = 100
            else:
                rankPng = Image.open(
                    pic_dir + f'UI_GAM_Rank_SSSp.png').convert('RGBA')
                achievement = 100.5
            rankPng = resizePic(rankPng, 1.2)
            chartImg.paste(rankPng, (10, 110), rankPng)

           # 绘制rating差值
            music_target = computeRa(chartInfo.ds, achievement)
            difference = 0
            if chartInfo.achievement != 0:
                music_ra = computeRa(chartInfo.ds, chartInfo.achievement)
                difference = music_target - music_ra
            else:
                difference = music_target - sd_floor
            raFont = ImageFont.truetype(fontName, 23, encoding='utf-8')
            textRa = f'ra:{music_target}'
            textTotal = f'total:{curRating}->{curRating+difference}'
            text_border(baseDraw, 110, 140,
                        raFont, 'black', 'white', textTotal)

            border_color = (237, 125, 49)
            fill_color = (255, 255, 255)
            text_border(baseDraw, 125, 110,
                        raFont, border_color, fill_color, textRa)
            text_border(baseDraw, 215, 110,
                        raFont, border_color, fill_color, f'+{difference}分！')
            baseImg.paste(
                chartImg, position_sd[num], chartImg)

        position_dx = [(580, 479), (920, 479), (580, 684), (920, 684)]
        if len(dx_list) != 4:
            for i in range(len(dx_list), 4):
                tempImg = draw_temp_pic()
                baseImg.paste(
                    tempImg, position_dx[i], tempImg)
        for num in range(0, len(dx_list)):
            chartInfo = dx_list[num]
            id = chartInfo['id']

            # 绘制模糊背景
            pngPath = cover_dir + \
                f'{get_cover_len4_id(id)}.jpeg'
            if not os.path.exists(pngPath):
                pngPath = cover_dir + '0031.jpeg'
            chartImg = Image.open(pngPath).convert('RGB')
            chartImg = resizePic(chartImg, itemW / chartImg.size[0])
            chartImg = chartImg.crop(
                (0, (chartImg.size[1] - itemH) / 2, itemW, (chartImg.size[1] + itemH) / 2))
            chartImg = chartImg.filter(ImageFilter.GaussianBlur(3))
            chartImg = circle_corner(chartImg, 20)
            baseDraw = ImageDraw.Draw(chartImg)

            # 绘制难度和版本
            diff = chartInfo.diff
            if diff == 4:
                offsetX = 3
            else:
                offsetX = -6
            diffPng = Image.open(
                pic_dir + f'UI_PFC_MS_Info02_{diffPic[diff]}.png')
            diffPng = resizePic(diffPng, 1.3)
            chartImg.paste(diffPng, (offsetX, 5), diffPng)
            if chartInfo['type'] == 'DX':
                versionPng = Image.open(
                    pic_dir + 'UI_UPE_Infoicon_DeluxeMode.png')
            else:
                versionPng = Image.open(
                    pic_dir + 'UI_UPE_Infoicon_StandardMode.png')
            versionPng = resizePic(versionPng, 1)
            chartImg.paste(versionPng, (185, 5), versionPng)

            # 绘制title
            title = chartInfo.title
            if columWidth(title) > 15:
                title = changeColumnWidth(title, 14) + '...'
            titleFont = ImageFont.truetype(adobe, 22, encoding='utf-8')
            detailFont = ImageFont.truetype(fontName, 22, encoding='utf-8')
            text_border(baseDraw, 10, 40,
                        titleFont, 'black', 'white', title)
            # 绘制定数
            text_border(baseDraw, 215, 40,
                        detailFont, 'black', 'white', '定数:' + str(chartInfo.ds))
            # 绘制曲包
            genre = chartInfo.genre
            if 'Project' in genre:
                genre = '东方Project'
            if 'CHUNI' in genre:
                genre = 'CHUNITHM'
            if columWidth(genre) > 14:
                genre = changeColumnWidth(genre, 13) + '...'

            text_border(baseDraw, 10, 75,
                        detailFont, 'black', 'white', '分类:' + str(genre))
            # 绘制等级
            text_border(baseDraw, 215, 75,
                        detailFont, 'black', 'white', 'id:' + str(chartInfo.id))

            # 绘制rank
            achievement = 0
            if chartInfo.target == 'sss':
                rankPng = Image.open(
                    pic_dir + f'UI_GAM_Rank_SSS.png').convert('RGBA')
                achievement = 100
            else:
                rankPng = Image.open(
                    pic_dir + f'UI_GAM_Rank_SSSp.png').convert('RGBA')
                achievement = 100.5
            rankPng = resizePic(rankPng, 1.2)
            chartImg.paste(rankPng, (10, 110), rankPng)

            # 绘制rating差值
            music_target = computeRa(chartInfo.ds, achievement)
            difference = 0
            if chartInfo.achievement != 0:
                music_ra = computeRa(chartInfo.ds, chartInfo.achievement)
                difference = music_target - music_ra
            else:
                difference = music_target - dx_floor
            raFont = ImageFont.truetype(fontName, 23, encoding='utf-8')
            textRa = f'ra:{music_target}'
            textTotal = f'total:{curRating}->{curRating+difference}'
            text_border(baseDraw, 110, 140,
                        raFont, 'black', 'white', textTotal)

            border_color = (237, 125, 49)
            fill_color = (255, 255, 255)
            text_border(baseDraw, 125, 110,
                        raFont, border_color, fill_color, textRa)
            text_border(baseDraw, 215, 110,
                        raFont, border_color, fill_color, f'+{difference}分！')
            baseImg.paste(
                chartImg, position_dx[num], chartImg)

        #   DX图标
        dxImg = Image.open(pic_dir+'UI_CMN_Name_DX.png').convert('RGBA')
        guaLogo = Image.open(pic_dir+'gua_logo.png').convert('RGBA')
        guaLogo = resizePic(guaLogo, 0.3)

        # 绘制分析板 sd
        b25Img = 'B25_board.png'
        b15Img = 'B15_board.png'
        b25_board_img = Image.open(
            pic_dir+b25Img).convert('RGBA')
        b25_board_img = b25_board_img.resize((530, 296))
        boardDraw = ImageDraw.Draw(b25_board_img)
        board_offsetX = baseImg.size[0]-30-b25_board_img.size[0]

        #  绘制推荐
        raFont = ImageFont.truetype(adobe, 22, encoding='utf-8')
        achievement_list = [100.5, 100, 99.5, 99]
        margin_top_list = [83, 131, 181]
        margin_left_list = [205, 283, 363, 443]
        table_first_list = [sd_top, sd_floor, sd_floor+3]
        for i in range(0, len(table_first_list)):
            boardDraw.text((125, margin_top_list[i]), str(
                table_first_list[i]), (68, 114, 196), raFont)
        # for i in range(0, 4):

        for i in range(0, len(achievement_list)):
            achievement = achievement_list[i]
            offsetX = margin_left_list[i]
            ra = get_ds_by_ra_ach(sd_top, achievement)
            if ra == -1:
                ra = '/'
                offsetX = margin_left_list[i]+15
            boardDraw.text((offsetX, margin_top_list[0]), str(
                ra), (68, 114, 196), raFont)

            offsetX = margin_left_list[i]
            ra = get_ds_by_ra_ach(sd_floor, achievement)
            if ra == -1:
                ra = '/'
                offsetX = margin_left_list[i]+15
            boardDraw.text((offsetX, margin_top_list[1]), str(
                ra), (68, 114, 196), raFont)
            offsetX = margin_left_list[i]
            ra = get_ds_by_ra_ach(sd_floor+3, achievement)
            if ra == -1:
                ra = '/'
                offsetX = margin_left_list[i]+15
            boardDraw.text((offsetX, margin_top_list[2]), str(
                ra), (68, 114, 196), raFont)

        # rating框
        raFont = ImageFont.truetype(adobe, 16, encoding='utf-8')
        totalRaImg = Image.open(
            pic_dir+'UI_CMN_DXRating_S_10.png').convert('RGBA')
        trImgDraw = ImageDraw.Draw(totalRaImg)
        totalRa = str(curRating + additional_rating)
        raColor = (248, 212, 97)
        raBorder = 'black'
        for i in range(0, len(totalRa)):
            offsetX = 88 + 15*(5-len(totalRa)+i)
            char = totalRa[i]
            text_border(trImgDraw, offsetX, 10,
                        raFont, raBorder, raColor, char)
        baseImg.paste(
            totalRaImg, (baseImg.size[0]+85-b25_board_img.size[0], 10), totalRaImg)
        # guaLogo
        baseImg.paste(
            guaLogo, (baseImg.size[0]-60-b25_board_img.size[0], -8), guaLogo)
        # 类型logo
        sdImg = Image.open(pic_dir+'UI_RSL_MBase_Parts_02.png').convert('RGBA')
        baseImg.paste(
            sdImg, (baseImg.size[0]-20-b25_board_img.size[0], 115), sdImg)
        # 分数框
        raImg = Image.open(
            pic_dir+'UI_CMN_Shougou_Rainbow.png').convert('RGBA')
        raImg = raImg.resize((220, 35), Image.ANTIALIAS)
        raDraw = ImageDraw.Draw(raImg)
        raFont = ImageFont.truetype(adobe, 20, encoding='utf-8')
        text_border(raDraw, 20, 5,
                    raFont, 'black', 'white', 'SD rating： '+str(sd_ra))
        baseImg.paste(
            raImg, (baseImg.size[0]+85-b25_board_img.size[0], 130), raImg)
        # id框子
        userImg = Image.open(pic_dir+'UI_TST_PlateMask.png').convert('RGBA')
        userImg = userImg.resize((408, 70), Image.ANTIALIAS)
        userDraw = ImageDraw.Draw(userImg)
        idFont = ImageFont.truetype(adobe, 28, encoding='utf-8')
        userDraw.text((20, 20), userId, 'black', idFont)
        userImg.paste(dxImg, (340, 16), dxImg)
        baseImg.paste(
            userImg, (baseImg.size[0]+85-b25_board_img.size[0], 50), userImg)
        baseImg.paste(b25_board_img, (board_offsetX, 160), b25_board_img)

        # 绘制分析板 dx
        b15Img = 'B15_board.png'
        b15_board_img = Image.open(
            pic_dir+b15Img).convert('RGBA')
        b15_board_img = b15_board_img.resize((530, 296))
        boardDraw = ImageDraw.Draw(b15_board_img)
        board_offsetX = 30

        # 类型logo
        dxImg = Image.open(pic_dir+'UI_RSL_MBase_Parts_01.png').convert('RGBA')
        baseImg.paste(dxImg, (50, 535), dxImg)
        # 分数框
        raImg = Image.open(
            pic_dir+'UI_CMN_Shougou_Rainbow.png').convert('RGBA')
        raImg = raImg.resize((220, 35), Image.ANTIALIAS)
        raDraw = ImageDraw.Draw(raImg)
        raFont = ImageFont.truetype(adobe, 20, encoding='utf-8')
        text_border(raDraw, 20, 5,
                    raFont, 'black', 'white', 'DX rating： '+str(dx_ra))
        baseImg.paste(raImg, (140, 550), raImg)

        #  绘制推荐 dx
        raFont = ImageFont.truetype(adobe, 22, encoding='utf-8')
        achievement_list = [100.5, 100, 99.5, 99]
        margin_top_list = [83, 131, 181]
        margin_left_list = [205, 283, 363, 443]
        table_first_list = [dx_top, dx_floor, dx_floor+3]
        for i in range(0, len(table_first_list)):
            boardDraw.text((125, margin_top_list[i]), str(
                table_first_list[i]), (68, 114, 196), raFont)
        for i in range(0, len(achievement_list)):
            achievement = achievement_list[i]
            offsetX = margin_left_list[i]
            ra = get_ds_by_ra_ach(dx_top, achievement)
            if ra == -1:
                ra = '/'
                offsetX = margin_left_list[i]+15
            boardDraw.text((offsetX, margin_top_list[0]), str(
                ra), (68, 114, 196), raFont)

            offsetX = margin_left_list[i]
            ra = get_ds_by_ra_ach(dx_floor, achievement)
            if ra == -1:
                ra = '/'
                offsetX = margin_left_list[i]+15
            boardDraw.text((offsetX, margin_top_list[1]), str(
                ra), (68, 114, 196), raFont)
            offsetX = margin_left_list[i]
            ra = get_ds_by_ra_ach(dx_floor+3, achievement)
            if ra == -1:
                ra = '/'
                offsetX = margin_left_list[i]+15
            boardDraw.text((offsetX, margin_top_list[2]), str(
                ra), (68, 114, 196), raFont)
        baseImg.paste(b15_board_img, (board_offsetX,
                                      baseImg.size[1]-b15_board_img.size[1]-30), b15_board_img)

        # 绘制作者
        # board
        authBoardImg = Image.open(pic_dir+'UI_TST_PlateMask.png')
        authBoardImg = authBoardImg.resize((310, 80))
        authDraw = ImageDraw.Draw(authBoardImg)
        authFont = ImageFont.truetype(fontName, 16, encoding='utf-8')
        authText = '''
        Credit to 
        XybBot & Diving-fish
        Generated By Linxae & guagua
        '''
        # w, h = authFont.getsize(authText)
        authDraw.text(
            (-10, -12), authText, 'black', authFont)
        guaguaImg = Image.open(pic_dir+'guaguacs_logo.png')
        guaguaImg = resizePic(guaguaImg, 0.15)
        baseImg.paste(authBoardImg, (50,
                      baseImg.size[1]-b15_board_img.size[1]-165), authBoardImg)
        baseImg.paste(guaguaImg, (380,
                      baseImg.size[1]-b15_board_img.size[1]-175), guaguaImg)
    return baseImg, 0


ds_dict = {
    "15": [14.0, 15.0],
    "14+": [14.0, 15.0],
    "14": [14.0, 15.0],
    "13+": [13.7, 13.9],
    "13": [13.0, 13.6],
    "12+": [12.7, 12.9],
    "12": [12.0, 12.6],
    "11+": [11.7, 11.9],
    "11": [11.0, 11.6],
    "10+": [10.7, 10.9],
    "10": [10.0, 10.6],
    "9+": [9.7, 9.9],
    "9": [9.0, 9.6],
    "8+": [8.7, 8.9],
    "8": [8.0, 8.6],
}
color_dict = {
    "Bas": (69, 193, 36),
    "Adv": (248, 176, 8),
    "Exp": (255, 90, 102),
    "Mst": (159, 81, 220),
    "ReM": (226, 209, 240),
}

# 绘制定数表


async def draw_com_list(ds: str, qq: str):

    def inner_level_q(ds1, ds2=None):
        result_set = []
        diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'ReM']
        if ds2 is not None:
            music_data = total_list.filter(ds=(ds1, ds2))
        else:
            music_data = total_list.filter(ds=ds1)
        for music in sorted(music_data, key=lambda i: int(i['id'])):
            for i in music.diff:
                result_set.append(
                    {"id": music['id'], "title": music['title'], "ds": music['ds'][i], "diff_label": diff_label[i], "diff_index": i, "level": music['level'][i], "type": music['type'], "achievement": 0})
        return result_set

    def contact_img(src_img, len):
        pic_dir = 'src/static/mai/pic/'
        bg_img = Image.open(
            pic_dir + 'UI_UNL_BG.png').convert('RGBA')
        src_w, src_h = src_img.size
        bg_w, bg_h = bg_img.size
        # 生成等长白布
        temp_img = Image.new('RGB', (src_w, src_h+len), (255, 255, 255))
        box = (0, 0, bg_w, len)
        bg_img = bg_img.crop(box)
        temp_img.paste(src_img, (0, 0))
        temp_img.paste(bg_img, (0, src_h))
        if len > bg_h:
            diff = len-bg_h
            temp_img.paste(bg_img, (0, src_h+diff))
        # src_img.paste(bg_img, (0, src_h), bg_img)
        # src_img.show()
        return temp_img

    records, success = await get_user_data(qq)
    if success == 0:
        return None, 0
    ds_range = ds_dict[ds]
    com_list = []
    for item in records:
        if item['ds'] >= ds_range[0] and item['ds'] <= ds_range[1]:
            com_list.append(item)

    ds_range = ds_dict[ds]
    # 筛出范围内的乐曲
    music_list = inner_level_q(ds_range[0], ds_range[1])
    # 按定数排序
    music_list = sorted(music_list, key=lambda i: i['ds'])
    for music in music_list:
        for com_music in com_list:
            if int(music['id']) == com_music['song_id'] and music['diff_index'] == com_music['level_index']:
                music['achievement'] = com_music['achievements']
    # 计算出每种定数各有多少个
    ds_num_list = []
    count = 0
    cur_ds = ds_range[0]
    for i in range(len(music_list)):
        music = music_list[i]
        if cur_ds == music['ds']:
            count = count + 1
        else:
            ds_num_list.append(count)
            count = 1
            cur_ds = music['ds']
        if i == len(music_list)-1:
            ds_num_list.append(count)
            count = 1
    if ds == '15' or ds == '14' or ds == '14+':
        ds = '14-15'
    pic_dir = 'src/static/mai/pic/'
    cover_dir = 'src/static/mai/cover/'
    bg_img = Image.open(
        pic_dir + 'UI_UNL_BG.png').convert('RGBA')
    gua_logo = resizePic(Image.open(
        pic_dir + 'gua_logo.png').convert('RGBA'), 0.4)
    bg_draw = ImageDraw.Draw(bg_img)
    adobe = 'src/static/adobe_simhei.otf'
    mft = 'src/static/msyh.ttc'

    bg_w, bg_h = bg_img.size
    # 板块间隔
    block_margin = 30
    # 单体间隔
    item_margin = 15
    # 每行个数
    row_num = 10
    # 单个封面大小
    item_len = 75

    title_font = ImageFont.truetype(adobe, 70, encoding='utf-8')
    bg_draw.text((470, 80), f'{ds}完成表', 'black', title_font)
    bg_img.paste(gua_logo, (270, -10), gua_logo)

    auth_font = ImageFont.truetype(adobe, 22, encoding='utf-8')
    auth = 'Generated by Guabot\nGuagua & Linxae'
    bg_draw.text((20, 20),
                 f'{auth}', 'black', auth_font)

    dx_img = Image.open(
        pic_dir + 'UI_UPE_Infoicon_DeluxeMode.png').convert('RGBA')
    dx_img = dx_img.resize((40, 11))

    index = 0
    margin_top = 200
    margin_left = 150
    ds_font = ImageFont.truetype(adobe, 48, encoding='utf-8')
    cur_ds = ds_range[0]
    # 已绘制总高度
    cur_bg_h = 200
    for ds_num in ds_num_list:
        cur_row_h = int(math.ceil(ds_num/10)*80+item_margin*(ds_num/10))
        cur_bg_h = cur_bg_h+cur_row_h+block_margin
        if cur_bg_h > bg_h:
            # 拼接背景
            bg_img = contact_img(bg_img, cur_bg_h-bg_h)
            bg_draw = ImageDraw.Draw(bg_img)
            bg_w, bg_h = bg_img.size
        bg_draw.text((margin_left-120, margin_top+15),
                     f'{"%.1f" % cur_ds}', 'black', ds_font)
        for num in range(ds_num):
            music = music_list[index]
            i = num % row_num
            j = num // row_num
            id = music.get('id')
            # 封面
            item = Image.open(
                cover_dir + f'{get_cover_len4_id(id)}.jpeg').convert('RGBA')

            diff = music['diff_label']
            if diff != 'Mst':
                # 图片添加边框
                item = image_border(item, 'a', 20, color_dict[diff])
            item = item.resize((item_len, item_len))
            if music['type'] == 'DX':
                item.paste(dx_img, (35, 0), dx_img)

            # score
            if music['achievement'] != 0:
                score_id = trans_score_id(music['achievement'])
                score_img = Image.open(
                    pic_dir + f'UI_GAM_Rank_{scoreRank[score_id]}.png').convert('RGBA')
                score_img = resizePic(score_img, 0.8)
                w, h = score_img.size
                item.paste(score_img, (int((item_len-w)/2),
                           int((item_len-h)/2)), score_img)

            bg_img.paste(item, (margin_left+i*(item_margin+item_len),
                                margin_top+j*(item_margin+item_len)))
            index = index+1
        # 当前块行高
        margin_top = margin_top+cur_row_h+block_margin
        cur_ds = cur_ds + 0.1
    return bg_img, 1
