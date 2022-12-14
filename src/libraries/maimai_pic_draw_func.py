from asyncio.windows_events import NULL
import os
import math
import random
from typing import Optional, Dict, List

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
                temp = random.choice(sssp_list)
                if temp not in sssp_temp:
                    sssp_temp.append(temp)
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

# ???????????????score??????


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
# ???????????????????????????


def draw_temp_pic():

    # ??????sd??????
    itemW = 310
    itemH = 180

    pic_dir = 'src/static/dragon/'
    cover_dir = 'src/static/mai/cover/'

    # ??????????????????
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
    # ??????????????????????????????????????????
    Text = '????????????'
    w, h = font.getsize(Text)
    text_border(tempDraw, (tempImg.size[0]-w)/2, (tempImg.size[1]-h)/2,
                font, 'black', 'white', '????????????')
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


# ??????????????????
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
        # ?????????????????????
        # ??????????????????????????????????????????
        # ????????????ra??????????????????????????????>??????
        # ????????????????????????b40??????????????????/?????????????????????????????????
        # ????????????ra?????????????????????????????????????????????????????????????????????
        # ?????????????????????b40???????????????ra??????????????????????????????>????????????????????????????????????
        for music in total_list:
            if music.is_new:
                for ds in music.ds:
                    achievement = 0
                    music_ra = computeRa(ds, 100)
                    # ???????????????????????????????????????
                    if music_ra > dx_floor and music_ra < dx_floor+12:
                        ds_index = music.ds.index(ds)
                        # ?????????????????????best???
                        if dx_best.find_by_id(int(music.id), ds_index) != -1:
                            # ??????????????????????????????????????????
                            if dx_best.is_n(int(music.id)):
                                # ??????????????????
                                if dx_best.is_np(int(music.id)):
                                    continue
                                else:
                                    # ??????????????????????????????????????????
                                    music_ra = computeRa(ds, 100.5)
                                    if music_ra > dx_floor and music_ra < dx_floor + 10:
                                        ds_index = music.ds.index(ds)
                                        # ?????????????????????best???
                                        if dx_best.find_by_id(int(music.id), ds_index) != -1:
                                            # ????????????????????????????????????
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
                        # ??????????????????????????????????????????
                        music_ra = computeRa(ds, 100.5)
                        if music_ra > dx_floor and music_ra < dx_floor+12:
                            ds_index = music.ds.index(ds)
                            # ?????????????????????best???
                            if dx_best.find_by_id(int(music.id), ds_index) != -1:
                                # ????????????????????????????????????
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
                    # ???????????????????????????????????????
                    if music_ra > sd_floor and music_ra < sd_floor+12:
                        ds_index = music.ds.index(ds)
                        # ?????????????????????best???
                        if sd_best.find_by_id(int(music.id), ds_index) != -1:
                            # ??????????????????????????????????????????
                            if sd_best.is_n(int(music.id)):
                                # ??????????????????
                                if sd_best.is_np(int(music.id)):
                                    continue
                                else:
                                    # ??????????????????????????????????????????
                                    music_ra = computeRa(ds, 100.5)
                                    if music_ra > sd_floor and music_ra < sd_floor + 10:

                                        ds_index = music.ds.index(ds)
                                        # ?????????????????????best???
                                        if sd_best.find_by_id(int(music.id), ds_index) != -1:
                                            # ????????????????????????????????????
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
                        # ??????????????????????????????????????????
                        music_ra = computeRa(ds, 100.5)
                        if music_ra > sd_floor and music_ra < sd_floor+12:
                            ds_index = music.ds.index(ds)
                            # ?????????????????????best???
                            if sd_best.find_by_id(int(music.id), ds_index) != -1:
                                # ????????????????????????????????????
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
        # ????????????
        pic_dir = 'src/static/mai/pic/'
        cover_dir = 'src/static/mai/cover/'
        fontName = 'src/static/mht.ttf'
        adobe = 'src/static/adobe_simhei.otf'
        baseImg = Image.open(
            pic_dir + 'gua_bg2.jpeg').convert('RGBA').filter(ImageFilter.GaussianBlur(3))
        # w1280 h914
        baseImg = baseImg.resize((1280, 914), Image.ANTIALIAS)
        baseDraw = ImageDraw.Draw(baseImg)
        # ??????title
        # ??????????????????
        # ??????sd??????
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
            # ??????????????????
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

            # ?????????????????????
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

            # ??????title
            title = chartInfo.title
            if columWidth(title) > 15:
                title = changeColumnWidth(title, 14) + '...'
            titleFont = ImageFont.truetype(adobe, 22, encoding='utf-8')
            detailFont = ImageFont.truetype(fontName, 22, encoding='utf-8')
            text_border(baseDraw, 10, 40,
                        titleFont, 'black', 'white', title)
            # ????????????
            text_border(baseDraw, 215, 40,
                        detailFont, 'black', 'white', '??????:' + str(chartInfo.ds))
            # ????????????
            genre = chartInfo.genre
            if 'Project' in genre:
                genre = '??????Project'
            if 'CHUNI' in genre:
                genre = 'CHUNITHM'
            if columWidth(genre) > 14:
                genre = changeColumnWidth(genre, 13) + '...'

            text_border(baseDraw, 10, 75,
                        detailFont, 'black', 'white', '??????:' + str(genre))
            # ????????????
            text_border(baseDraw, 215, 75,
                        detailFont, 'black', 'white', 'id:' + str(chartInfo.id))

            # ??????rank
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

           # ??????rating??????
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
                        raFont, border_color, fill_color, f'+{difference}??????')
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

            # ??????????????????
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

            # ?????????????????????
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

            # ??????title
            title = chartInfo.title
            if columWidth(title) > 15:
                title = changeColumnWidth(title, 14) + '...'
            titleFont = ImageFont.truetype(adobe, 22, encoding='utf-8')
            detailFont = ImageFont.truetype(fontName, 22, encoding='utf-8')
            text_border(baseDraw, 10, 40,
                        titleFont, 'black', 'white', title)
            # ????????????
            text_border(baseDraw, 215, 40,
                        detailFont, 'black', 'white', '??????:' + str(chartInfo.ds))
            # ????????????
            genre = chartInfo.genre
            if 'Project' in genre:
                genre = '??????Project'
            if 'CHUNI' in genre:
                genre = 'CHUNITHM'
            if columWidth(genre) > 14:
                genre = changeColumnWidth(genre, 13) + '...'

            text_border(baseDraw, 10, 75,
                        detailFont, 'black', 'white', '??????:' + str(genre))
            # ????????????
            text_border(baseDraw, 215, 75,
                        detailFont, 'black', 'white', 'id:' + str(chartInfo.id))

            # ??????rank
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

            # ??????rating??????
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
                        raFont, border_color, fill_color, f'+{difference}??????')
            baseImg.paste(
                chartImg, position_dx[num], chartImg)

        #   DX??????
        dxImg = Image.open(pic_dir+'UI_CMN_Name_DX.png').convert('RGBA')
        guaLogo = Image.open(pic_dir+'gua_logo.png').convert('RGBA')
        guaLogo = resizePic(guaLogo, 0.3)

        # ??????????????? sd
        b25Img = 'B25_board.png'
        b15Img = 'B15_board.png'
        b25_board_img = Image.open(
            pic_dir+b25Img).convert('RGBA')
        b25_board_img = b25_board_img.resize((530, 296))
        boardDraw = ImageDraw.Draw(b25_board_img)
        board_offsetX = baseImg.size[0]-30-b25_board_img.size[0]

        #  ????????????
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

        # rating???
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
        # ??????logo
        sdImg = Image.open(pic_dir+'UI_RSL_MBase_Parts_02.png').convert('RGBA')
        baseImg.paste(
            sdImg, (baseImg.size[0]-20-b25_board_img.size[0], 115), sdImg)
        # ?????????
        raImg = Image.open(
            pic_dir+'UI_CMN_Shougou_Rainbow.png').convert('RGBA')
        raImg = raImg.resize((220, 35), Image.ANTIALIAS)
        raDraw = ImageDraw.Draw(raImg)
        raFont = ImageFont.truetype(adobe, 20, encoding='utf-8')
        text_border(raDraw, 20, 5,
                    raFont, 'black', 'white', 'SD rating??? '+str(sd_ra))
        baseImg.paste(
            raImg, (baseImg.size[0]+85-b25_board_img.size[0], 130), raImg)
        # id??????
        userImg = Image.open(pic_dir+'UI_TST_PlateMask.png').convert('RGBA')
        userImg = userImg.resize((408, 70), Image.ANTIALIAS)
        userDraw = ImageDraw.Draw(userImg)
        idFont = ImageFont.truetype(adobe, 28, encoding='utf-8')
        userDraw.text((20, 20), userId, 'black', idFont)
        userImg.paste(dxImg, (340, 16), dxImg)
        baseImg.paste(
            userImg, (baseImg.size[0]+85-b25_board_img.size[0], 50), userImg)
        baseImg.paste(b25_board_img, (board_offsetX, 160), b25_board_img)

        # ??????????????? dx
        b15Img = 'B15_board.png'
        b15_board_img = Image.open(
            pic_dir+b15Img).convert('RGBA')
        b15_board_img = b15_board_img.resize((530, 296))
        boardDraw = ImageDraw.Draw(b15_board_img)
        board_offsetX = 30

        # ??????logo
        dxImg = Image.open(pic_dir+'UI_RSL_MBase_Parts_01.png').convert('RGBA')
        baseImg.paste(dxImg, (50, 535), dxImg)
        # ?????????
        raImg = Image.open(
            pic_dir+'UI_CMN_Shougou_Rainbow.png').convert('RGBA')
        raImg = raImg.resize((220, 35), Image.ANTIALIAS)
        raDraw = ImageDraw.Draw(raImg)
        raFont = ImageFont.truetype(adobe, 20, encoding='utf-8')
        text_border(raDraw, 20, 5,
                    raFont, 'black', 'white', 'DX rating??? '+str(dx_ra))
        baseImg.paste(raImg, (140, 550), raImg)

        #  ???????????? dx
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

        # ????????????
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

# ???????????????


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


async def draw_com_list(ds: str, qq: str):

    def contact_img(src_img, len):
        pic_dir = 'src/static/mai/pic/'
        bg_img = Image.open(
            pic_dir + 'UI_UNL_BG.png').convert('RGBA')
        src_w, src_h = src_img.size
        bg_w, bg_h = bg_img.size
        # ??????????????????
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
    if success == 400:
        return None, 400
    if success == 403:
        return None, 403
    # records????????????
    for music in records:
        song = total_list.by_id(str(music['id']))
        music['ds'] = song['ds'][music['level_index']]

    ds_range = ds_dict[ds]
    com_list = []
    for item in records:
        if item['ds'] >= ds_range[0] and item['ds'] <= ds_range[1]:
            com_list.append(item)

    ds_range = ds_dict[ds]
    # ????????????????????????
    music_list = inner_level_q(ds_range[0], ds_range[1])
    # ???????????????
    music_list = sorted(music_list, key=lambda i: i['ds'], reverse=True)
    for music in music_list:
        for com_music in com_list:
            if int(music['id']) == com_music['id'] and music['diff_index'] == com_music['level_index']:
                music['achievement'] = com_music['achievements']
    # ????????????????????????????????????
    ds_num_list = []
    count = 0
    cur_ds = ds_range[1]
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
    # ????????????
    block_margin = 30
    # ????????????
    item_margin = 15
    # ????????????
    row_num = 10
    # ??????????????????
    item_len = 75

    title_font = ImageFont.truetype(adobe, 70, encoding='utf-8')
    bg_draw.text((470, 80), f'{ds}?????????', 'black', title_font)
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
    cur_ds = ds_range[1]
    # ??????????????????
    cur_bg_h = 200
    for ds_num in ds_num_list:
        cur_row_h = int(math.ceil(ds_num/10)*80+item_margin*(ds_num/10))
        cur_bg_h = cur_bg_h+cur_row_h+block_margin
        if cur_bg_h > bg_h:
            # ????????????
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
            # ??????
            item = Image.open(
                cover_dir + f'{get_cover_len4_id(id)}.jpeg').convert('RGBA')

            diff = music['diff_label']
            if diff != 'Mst':
                # ??????????????????
                item = image_border(item, 'a', 40, color_dict[diff])
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
        # ???????????????
        margin_top = margin_top+cur_row_h+block_margin
        cur_ds = cur_ds - 0.1
    return bg_img, 1

diff_dict = ["Bas",
             "Adv",
             "Exp",
             "Mst",
             "ReM"]


async def draw_score_list(ds: str, qq: str, cur_page: int):
    ds_dict_score = {
        "15": [15.0, 15.0],
        "14+": [14.7, 14.9],
        "14": [14.0, 14.6],
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

    records, success = await get_user_data(qq)
    if success == 400:
        return None, 400
    if success == 403:
        return None, 403
    # records????????????
    for music in records:
        song = total_list.by_id(str(music['id']))
        music['ds'] = song['ds'][music['level_index']]

    ds_range = ds_dict_score[ds]
    score_list = []
    for item in records:
        if item['ds'] >= ds_range[0] and item['ds'] <= ds_range[1]:
            score_list.append(item)

    if len(score_list) == 0:
        return None, -1
    # ???????????????
    score_list = sorted(
        score_list, key=lambda i: i['achievements'], reverse=True)

    total_num = len(score_list)
    page_num = 25
    total_page = math.ceil(total_num / page_num)
    total_page = total_page if total_page > 0 else 1
    # ??????????????????
    flag = 0
    if cur_page > total_page:
        cur_page = 1
        # 233????????????
        flag = 233
    score_list = score_list[(cur_page-1)*page_num:cur_page*page_num]

    adobe = 'src/static/adobe_simhei.otf'
    font = ImageFont.truetype(adobe, 20, encoding='UTF-8')
    max_w = 0
    # ????????????????????????
    for i in range(0, len(score_list)):
        record = score_list[i]
        title = record['title']
        level_index = record["level_index"]
        achievements = record["achievements"]
        type = record["type"]
        if record['fc'] != '':
            if record['fc'] == 'app':
                fc = 'ap+'
            elif record['fc'] == 'fcp':
                fc = 'fc+'
            else:
                fc = record['fc']
            record['title'] = record['title']+f'({fc})'
        if record['fs'] != '':
            if record['fs'] == 'fsp':
                fs = 'fs+'
            else:
                fs = record['fs']
            record['title'] = record['title']+f'({fs})'
        text = f'{achievements:.4f}% ({type}) ({diff_dict[level_index]}){title}'
        size = font.getsize(text)
        if size[0] > max_w:
            max_w = size[0]
    # ????????????
    imgH = 850
    imgW = max(max_w+20, 530)
    baseImg = Image.new('RGB', (imgW, imgH), (255, 255, 255))
    baseDraw = ImageDraw.Draw(baseImg)

    # ??????title
    title = f'??????{ds}??????????????????:'
    baseDraw.text((10, 10), title, 'black', font)

    # ????????????
    for i in range(0, len(score_list)):
        record = score_list[i]
        title = record['title']
        level_index = record["level_index"]
        achievements = record["achievements"]
        type = record["type"]
        text = f'{achievements:.4f}% ({type}) ({diff_dict[level_index]}){title}'
        baseDraw.text((10, i*30+40), text, 'black', font)

    # ??????footer
    font = ImageFont.truetype('simhei', 22, encoding='UTF-8')
    footer = f'{cur_page}/{total_page}??? {page_num}????????? generated by Guabot & Linxae\n'
    baseDraw.text((10, imgH-60), footer, 'black', font)
    font = ImageFont.truetype('simhei', 16, encoding='UTF-8')
    baseDraw.text((10, imgH-35), 'xx???????????? ?????? ????????????', 'black', font)
    if flag == 233:
        return baseImg, 233
    else:
        return baseImg, 1


# ??????????????????

plate_version = {
    '???': ['maimai', 'maimai PLUS'],
    '???': ['maimai GreeN'],
    '???': ['maimai GreeN PLUS'],
    '???': ['maimai ORANGE'],
    '???': ['maimai ORANGE PLUS'],
    '???': ['maimai ORANGE PLUS'],
    '???': ['maimai PiNK'],
    '???': ['maimai PiNK PLUS'],
    '???': ['maimai PiNK PLUS'],
    '???': ['maimai MURASAKi'],
    '???': ['maimai MURASAKi PLUS'],
    '???': ['maimai MURASAKi PLUS'],
    '???': ['maimai MiLK'],
    '???': ['MiLK PLUS'],
    '???': ['maimai FiNALE'],
    '???': ['maimai FiNALE'],
    '???': ['maimai', 'maimai PLUS', 'maimai GreeN', 'maimai GreeN PLUS',
          'maimai ORANGE', 'maimai ORANGE PLUS', 'maimai PiNK', 'maimai PiNK PLUS',
          'maimai MURASAKi', 'maimai MURASAKi PLUS', 'maimai MiLK', 'MiLK PLUS', 'maimai FiNALE'],
    '???': ['maimai ???????????????'],
    '???': ['maimai ???????????????'],
    '???': ['maimai ???????????????'],
    # '???': 'maimai ??????????????? PLUS',
    # '???': 'maimai ??????????????? PLUS',
    '???': ['maimai ??????????????? Splash'],
    '???': ['maimai ??????????????? Splash'],
    # '???': 'maimai ??????????????? Splash PLUS',
}

plate_pic_index = {
    '???': ['006101', '006102', '006103'],
    '???': ['006104', '006105', '006106', '006107'],
    '???': ['006108', '006109', '006110', '006111'],
    '???': ['006112', '006113', '006114', '006115'],
    '???': ['006116', '006117', '006118', '006119'],
    '???': ['006116', '006117', '006118', '006119'],
    '???': ['006120', '006121', '006122', '006123'],
    '???': ['006124', '006125', '006126', '006127'],
    '???': ['006124', '006125', '006126', '006127'],
    '???': ['006128', '006129', '006130', '006131'],
    '???': ['006132', '006133', '006134', '006135'],
    '???': ['006132', '006133', '006134', '006135'],
    '???': ['006136', '006137', '006138', '006139'],
    '???': ['006140', '006141', '006142', '006143'],
    '???': ['006144', '006145', '006146', '006147'],
    '???': ['006144', '006145', '006146', '006147'],
    '???': ['006149', '006150', '006151', '006152', '006148'],
    '???': ['055101', '055102', '055103', '055104'],
    '???': ['109101', '109102', '109103', '109104'],
    '???': ['109101', '109102', '109103', '109104'],
    # '???': 'maimai ??????????????? PLUS',
    # '???': 'maimai ??????????????? PLUS',
    '???': ['159101', '159102', '159103', '159104'],
    '???': ['209101', '209102', '209103', '209104'],
    # '???': 'maimai ??????????????? Splash PLUS',
}

plate_index = {
    '???': 4,
    '???': 0,
    '???': 1,
    '???': 2,
    '??????': 3
}


# ?????????????????????
def handel_finish_img(img):
    pic_dir = 'src/static/mai/pic/'
    # gou
    gou_img = Image.open(pic_dir+'??????2.jpeg')
    img_w, img_h = img.size
    gou_img = gou_img.resize((img_w+35, img_h+35))
    mask = Image.new('RGBA', (img_w, img_h), 'black')
    label = Image.blend(img, mask, 0.3)
    label.paste(gou_img, (-17, -17), gou_img)
    return label

# ????????????????????????????????????


async def get_plate_ach(match, plate: str, qq: str):

    def convert_rate(achievements):
        if achievements >= 100.5:
            return 'sssp'
        elif achievements >= 100:
            return 'sss'

    with open('src/static/mai/plate/plate_dict.json', 'r') as f:
        plate_dict = json.load(f)
        f.close()
    records, success = await get_user_plate_records(qq, plate_version[plate])
    if success == 0:
        return None, 0
    music_list = []
    plate = '???' if match[0] == '???' else plate
    # ????????????????????????????????????
    for music in plate_dict[plate]['music_list']:
        # print(music)
        flag = False
        # ??????????????????
        for item in records:
            # print(item)
            if str(item['id']) == str(music['song_id']) and item['level_index'] == music['level_index']:
                # print_to_json(item)
                music_list.append(
                    {"id": item['id'], "title": music['title'], "ds": music['ds'], "level_index": item['level_index'], "level": item['level'],
                     "achievements": item['achievements'], "fc": item['fc'], "fs": item['fs'], 'rate': convert_rate(item['achievements'])})
                flag = True
        if not flag:
            music_list.append(
                {"id": int(music['song_id']), "title": music['title'], "ds": music['ds'], "level_index": music['level_index'], "level": music['level'],
                 "achievements": 0, "fc": '', "fs": '', 'rate': ''})
            flag = False
    return music_list, 1


async def draw_plate_img(match, music_list):
    def contact_img(src_img, len):
        pic_dir = 'src/static/mai/pic/'
        bg_img = Image.open(
            pic_dir + 'UI_UNL_BG.png').convert('RGBA')
        src_w, src_h = src_img.size
        bg_w, bg_h = bg_img.size
        # ??????????????????
        temp_img = Image.new('RGB', (src_w, src_h+len), (255, 255, 255))
        box = (0, 0, bg_w, len)
        bg_img = bg_img.crop(box)
        temp_img.paste(src_img, (0, 0))
        temp_img.paste(bg_img, (0, src_h))
        if len > bg_h:
            diff = len-bg_h
            temp_img.paste(bg_img, (0, src_h+diff))
        return temp_img

    temp_list = []
    for item in music_list:
        if item['level_index'] in [3, 4]:
            temp_list.append(item)
    # ??????????????????????????????????????????????????????
    full_name = f'{match[0]}{match[1]}'
    prefix = match[0]
    prefix = '???' if match[0] == '???' else prefix
    suffix = match[1]
    index = plate_index[suffix]
    index_list = plate_pic_index[prefix]
    if prefix == '???':
        if suffix == '???':
            index = 1
        elif suffix == '??????':
            index = 2

    # ??????????????????
    plate_dir = 'src/static/mai/plate/img/'
    plate_img = Image.open(plate_dir+f'UI_Plate_{index_list[index]}.png')
    plate_img_w, plate_img_h = plate_img.size
    # ???????????????????????????
    box = (420, 10, plate_img_w-20, plate_img_h-10)
    plate_img = plate_img.crop(box)
    resizePic(plate_img, 0.6)

    # ????????????
    pic_dir = 'src/static/mai/pic/'
    cover_dir = 'src/static/mai/cover/'
    bg_img = Image.open(
        pic_dir + 'UI_UNL_BG.png').convert('RGBA')
    bg_draw = ImageDraw.Draw(bg_img)

    # ??????
    adobe = 'src/static/adobe_simhei.otf'
    mft = 'src/static/msyh.ttc'

    # sss
    sss_img = resizePic(Image.open(pic_dir+'UI_GAM_Rank_SSS.png'), 0.8)
    sssp_img = resizePic(Image.open(pic_dir+'UI_GAM_Rank_SSSp.png'), 0.8)
    # fc
    fc_img = resizePic(Image.open(pic_dir+'UI_MSS_MBase_Icon_FC.png'), 1.2)
    fcp_img = resizePic(Image.open(pic_dir+'UI_MSS_MBase_Icon_FCp.png'), 1.2)
    # ap
    ap_img = resizePic(Image.open(pic_dir+'UI_MSS_MBase_Icon_AP.png'), 1.2)
    app_img = resizePic(Image.open(pic_dir+'UI_MSS_MBase_Icon_APp.png'), 1.2)
    # fsp
    fs_img = resizePic(Image.open(pic_dir+'UI_MSS_MBase_Icon_fs.png'), 1.2)
    fsp_img = resizePic(Image.open(
        pic_dir+'UI_MSS_MBase_Icon_fsp.png'), 1.2)

    bg_w, bg_h = bg_img.size
    # print(bg_h)
    # ????????????
    block_margin = 30
    # ????????????
    item_margin = 15
    # ????????????
    row_num = 10
    # ??????????????????
    item_len = 75

    title_font = ImageFont.truetype(adobe, 70, encoding='utf-8')
    bg_draw.text((650, 100), '?????????', 'black', title_font)
    bg_img.paste(plate_img, (350, 90), plate_img)

    auth_font = ImageFont.truetype(adobe, 22, encoding='utf-8')
    auth = 'Generated by Guabot\nGuagua & Linxae'
    bg_draw.text((20, 20),
                 f'{auth}', 'black', auth_font)

    index = 0
    margin_top = 250
    margin_left = 150
    ds_font = ImageFont.truetype(adobe, 48, encoding='utf-8')

    temp_list = sorted(temp_list, key=lambda x: x['level'], reverse=True)
    # ????????????????????????????????????
    if prefix == '???':
        temp_list = sorted(temp_list, key=lambda x: x['ds'], reverse=True)
        save_list = []
        for item in temp_list:
            if item['ds'] >= 14:
                save_list.append(item)
        temp_list = save_list
        ds_num_list = []
        ds_list = []
        count = 0
        cur_ds = temp_list[0]['ds']
        for i in range(len(temp_list)):
            ds = temp_list[i]['ds']
            if cur_ds == ds:
                count = count + 1
            else:
                ds_num_list.append(count)
                ds_list.append(cur_ds)
                count = 1
                cur_ds = ds
            if i == len(temp_list)-1:
                ds_num_list.append(count)
                ds_list.append(cur_ds)
                count = 1
        ds_index = 0
        cur_ds = ds_list[ds_index]
    else:
        ds_num_list = []
        ds_list = []
        count = 0
        cur_ds = temp_list[0]['level']
        for i in range(len(temp_list)):
            ds = temp_list[i]['level']
            if cur_ds == ds:
                count = count + 1
            else:
                ds_num_list.append(count)
                ds_list.append(cur_ds)
                count = 1
                cur_ds = ds
            if i == len(temp_list)-1:
                ds_num_list.append(count)
                ds_list.append(cur_ds)
                count = 1
        ds_index = 0
        cur_ds = ds_list[ds_index]
    # ??????????????????
    cur_bg_h = 250
    for ds_num in ds_num_list:
        cur_row_h = int(math.ceil(ds_num/10)*80+item_margin*(ds_num/10))
        cur_bg_h = cur_bg_h+cur_row_h+block_margin
        if cur_bg_h > bg_h:
            # ????????????
            bg_img = contact_img(bg_img, cur_bg_h-bg_h)
            bg_draw = ImageDraw.Draw(bg_img)
            bg_w, bg_h = bg_img.size
        bg_draw.text((margin_left-120, margin_top+15),
                     f'{cur_ds}', 'black', ds_font)
        for num in range(ds_num):
            music = temp_list[index]
            i = num % row_num
            j = num // row_num
            id = music['id']
            # ??????
            item = Image.open(
                cover_dir + f'{get_cover_len4_id(id)}.jpeg').convert('RGBA')
            item = item.resize((item_len, item_len))
            # score
            if suffix in ['???', '???']:
                if music['fc'] != '':
                    if music['fc'] == 'fc':
                        w, h = fc_img.size
                        item.paste(fc_img, (int((item_len-w)/2),
                                            int((item_len-h)/2)), fc_img)
                        item = handel_finish_img(item)
                    elif music['fc'] == 'fcp':
                        w, h = fcp_img.size
                        item.paste(fcp_img, (int((item_len-w)/2),
                                             int((item_len-h)/2)), fcp_img)
                        item = handel_finish_img(item)

            if suffix in ['???']:
                if music['rate'] != '':
                    if music['rate'] == 'sss':
                        w, h = sss_img.size
                        item.paste(sss_img, (int((item_len-w)/2),
                                             int((item_len-h)/2)), sss_img)
                        item = handel_finish_img(item)
                    elif music['rate'] == 'sssp':
                        w, h = sssp_img.size
                        item.paste(sssp_img, (int((item_len-w)/2),
                                              int((item_len-h)/2)), sssp_img)
                        item = handel_finish_img(item)

            if suffix in ['???']:
                if music['fc'] != '':
                    if music['fc'] == 'ap':
                        w, h = ap_img.size
                        item.paste(ap_img, (int((item_len-w)/2),
                                            int((item_len-h)/2)), ap_img)
                        item = handel_finish_img(item)
                    elif music['fc'] == 'app':
                        w, h = app_img.size
                        item.paste(app_img, (int((item_len-w)/2),
                                             int((item_len-h)/2)), app_img)
                        item = handel_finish_img(item)

            if suffix in ['??????']:
                if music['fs'] != '':
                    if music['fs'] == 'fs':
                        w, h = fs_img.size
                        item.paste(fs_img, (int((item_len-w)/2),
                                            int((item_len-h)/2)), fs_img)
                        item = handel_finish_img(item)
                    elif music['fs'] == 'fsp':
                        w, h = fsp_img.size
                        item.paste(fsp_img, (int((item_len-w)/2),
                                             int((item_len-h)/2)), fsp_img)
                        item = handel_finish_img(item)

            if suffix in ['???']:
                if music['achievements'] >= 80:
                    item = handel_finish_img(item)
            if music['level_index'] == 4:
                # ??????????????????
                item = image_border(item, 'a', 5, (226, 209, 240))
                item = item.resize((item_len, item_len))

            bg_img.paste(item, (margin_left+i*(item_margin+item_len),
                                margin_top+j*(item_margin+item_len)))
            index = index+1
        # ???????????????
        margin_top = margin_top+cur_row_h+block_margin
        ds_index = ds_index + 1 if ds_index < len(ds_list)-1 else ds_index
        cur_ds = ds_list[ds_index]
    return bg_img


# ??????????????????
def filter_data(match, music_list):
    music_played = []
    music_remain_basic = []
    music_remain_advanced = []
    music_remain_expert = []
    music_remain_master = []
    music_remain_re_master = []
    music_remain_difficult = []
    if match[1] in ['???', '???']:
        for music in music_list:
            if music['level_index'] == 0 and music['achievements'] < (100.0 if match[1] == '???' else 80.0):
                music_remain_basic.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if music['level_index'] == 1 and music['achievements'] < (100.0 if match[1] == '???' else 80.0):
                music_remain_advanced.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if music['level_index'] == 2 and music['achievements'] < (100.0 if match[1] == '???' else 80.0):
                music_remain_expert.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if music['level_index'] == 3 and music['achievements'] < (100.0 if match[1] == '???' else 80.0):

                music_remain_master.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if match[0] in ['???', '???'] and music['level_index'] == 4 and music['achievements'] < (100.0 if match[1] == '???' else 80.0):
                music_remain_re_master.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            music_played.append(
                {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                 "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
    elif match[1] in ['???', '???']:
        for music in music_list:
            if music['level_index'] == 0 and not music['fc']:
                music_remain_basic.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if music['level_index'] == 1 and not music['fc']:
                music_remain_advanced.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if music['level_index'] == 2 and not music['fc']:
                music_remain_expert.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if music['level_index'] == 3 and not music['fc']:
                music_remain_master.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if match[0] == '???' and music['level_index'] == 4 and not music['fc']:
                music_remain_re_master.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            music_played.append(
                {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                 "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
    elif match[1] == '??????':
        for music in music_list:
            if music['level_index'] == 0 and music['fs'] not in ['fs', 'fsp']:
                music_remain_basic.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if music['level_index'] == 1 and music['fs'] not in ['fs', 'fsp']:
                music_remain_advanced.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if music['level_index'] == 2 and music['fs'] not in ['fs', 'fsp']:
                music_remain_expert.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if music['level_index'] == 3 and music['fs'] not in ['fs', 'fsp']:
                music_remain_master.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if match[0] == '???' and music['level_index'] == 4 and music['fs'] not in ['fs', 'fsp']:
                music_remain_re_master.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            music_played.append(
                {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                 "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
    elif match[1] == '???':
        for music in music_list:
            if music['level_index'] == 0 and music['fc'] not in ['ap', 'app']:
                music_remain_basic.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if music['level_index'] == 1 and music['fc'] not in ['ap', 'app']:
                music_remain_advanced.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if music['level_index'] == 2 and music['fc'] not in ['ap', 'app']:
                music_remain_expert.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if music['level_index'] == 3 and music['fc'] not in ['ap', 'app']:
                music_remain_master.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            if match[0] == '???' and music['level_index'] == 4 and music['fc'] not in ['ap', 'app']:
                music_remain_re_master.append(
                    {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                     "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
            music_played.append(
                {"id": music['id'], "level_index": music['level_index'], "ds": music['ds'],
                 "level": music['level'], "achievements": music['achievements'], "fc": music['fc'], "fs": music['fs']})
    total_remain = music_remain_basic+music_remain_advanced+music_remain_expert + \
        music_remain_master+music_remain_re_master
    for music in total_remain:
        song = total_list.by_id(str(music['id']))
        # ????????????13.6???????????????
        if music['ds'] > 13.6:
            music_remain_difficult.append(
                {"id": song.id, "title": song.title, "ds": music['ds'], "level_index": music['level_index'], "level": song.level[music['level_index']], "achievements": music['achievements']})
    return total_remain, music_played, music_remain_basic, music_remain_advanced, music_remain_expert, music_remain_master, music_remain_re_master, music_remain_difficult

# xx??????


async def create_plate_text(match, music_list):
    total_remain, music_played, music_remain_basic, music_remain_advanced, music_remain_expert, music_remain_master, music_remain_re_master, music_remain_difficult = filter_data(
        match, music_list)
    message = f'''?????? {match[0]}{match[1]} ??????????????????
Basic??????{len(music_remain_basic)}???
Advanced??????{len(music_remain_advanced)}???
Expert??????{len(music_remain_expert)}???
Master??????{len(music_remain_master)}???
'''

    pc = math.ceil(len(total_remain)/3)
    if pc == 0:
        message += f'?????????????????????{match[0]}{match[1]}?????????'
        return message
    music_remain_difficult = sorted(
        music_remain_difficult, key=lambda i: i['ds'], reverse=True)
    if match[0] in ['???', '???']:
        message += f'Re:Master??????{len(music_remain_re_master)}???\n'
    message += f'''????????????{len(total_remain)}???\n'''
    if len(music_remain_master) == 0:
        message += f'???????????????{match[0]}{match[1]}???????????????\n'
    total_remain = total_remain + music_remain_basic + music_remain_advanced
    # ???????????????10??????10?????????
    if len(music_remain_difficult) == 0:
        message += f'??????????????????????????????????????????!\n'
    elif len(music_remain_difficult) <= 10:
        message += '????????????????????????????????????:\n'
        for music in music_remain_difficult:
            message += f'''[{music['level']}] {music['title']} {str(music['achievements'])+'%' if music['achievements']!=0 else '?????????'}\n'''
    else:
        message += f'???????????????????????????????????????{len(music_remain_difficult)}???\n'
    message += f'??????????????????????????????{pc}???\n??????{int((pc*12)/60)}??????{(pc*12)%60}??????,?????????'
    return message


# ??????
LINE_CHAR_COUNT = 12*2  # ??????????????????12???????????????
TABLE_WIDTH = 4


def line_break(line):
    ret = ''
    width = 0
    for c in line:
        if len(c.encode('utf8')) == 3:  # ??????
            if LINE_CHAR_COUNT == width + 1:  # ??????????????????????????????
                width = 2
                ret += '\n' + c
            else:  # ???????????????2?????????????????????
                width += 2
                ret += c
        else:
            if c == '\t':
                space_c = TABLE_WIDTH - width % TABLE_WIDTH  # ???????????????TABLE_WIDTH??????
                ret += ' ' * space_c
                width += space_c
            elif c == '\n':
                width = 0
                ret += c
            else:
                width += 1
                ret += c
        if width >= LINE_CHAR_COUNT:
            ret += '\n'
            width = 0
    if ret.endswith('\n'):
        return ret
    return ret + '\n'

# ????????????


async def draw_single_record(id, single_records):
    music = total_list.by_id(id)
    # ????????????
    pic_dir = 'src/static/mai/pic/'
    cover_dir = 'src/static/mai/cover/'
    adobe = 'src/static/adobe_simhei.otf'

    # ???????????????
    if len(single_records) == 5:
        margin_top = [[230, 225, 610, 800], [
            380, 375], [540, 530], [690, 680], [840, 840]]
        bg_img = Image.open(
            pic_dir + 'UI_Single_Base_Re.png').convert('RGBA')
    else:
        margin_top = [[250, 245, 610, 800], [430, 425], [615, 605], [800, 790]]
        bg_img = Image.open(
            pic_dir + 'UI_Single_Base_Mas.png').convert('RGBA')
    bg_draw = ImageDraw.Draw(bg_img)

    # type????????????
    if single_records[0]['type'] == 'DX':
        type_img = Image.open(
            pic_dir + 'UI_UPE_Infoicon_DeluxeMode.png').convert('RGBA')
    else:
        type_img = Image.open(
            pic_dir + 'UI_UPE_Infoicon_StandardMode.png').convert('RGBA')
    bg_img.paste(type_img, (240, 340), type_img)

    # ????????????
    music_cover = resizePic(Image.open(
        cover_dir + f'{get_cover_len4_id(id)}.jpeg'), 0.8).convert('RGBA')
    bg_img.paste(music_cover, (40, 380))

    # ????????????
    # ??????
    title = music.title
    if columWidth(title) > 41:
        title = changeColumnWidth(title, 40) + '...'
    title = line_break(title)
    title_font = ImageFont.truetype(adobe, 40, encoding='utf-8')
    bg_draw.text((380, 380), title, font=title_font, fill='black')

    # ??????
    artist = music.artist
    if columWidth(artist) > 25:
        artist = changeColumnWidth(artist, 24) + '...'
    artist_font = ImageFont.truetype(adobe, 30, encoding='utf-8')
    bg_draw.text((380, 480), artist, font=artist_font, fill='black')

    # ID
    music_id = 'ID:'+music.id
    id_font = ImageFont.truetype(adobe, 34, encoding='utf-8')
    bg_draw.text((380, 530), music_id, font=id_font, fill=(91, 98, 124))

    # ??????
    genre = '??????:'+music.genre
    genre_font = ImageFont.truetype(adobe, 34, encoding='utf-8')
    bg_draw.text((380, 590), genre, font=genre_font, fill='black')

    # ??????
    version = '??????:'+music.version
    version = line_break(version)
    version_font = ImageFont.truetype(adobe, 34, encoding='utf-8')
    bg_draw.text((380, 660), version, font=version_font, fill='black')

    for i in range(len(single_records)):
        song = single_records[i]
        # ??????
        ds = song['ds']
        ds_font = ImageFont.truetype(adobe, 34, encoding='utf-8')
        if len(str(ds)) == 4:
            margin_left = 900
        else:
            margin_left = 910
        bg_draw.text((margin_left, margin_top[i][0]), str(ds),
                     font=ds_font, fill='black')

        # fc&ap
        fc_img = None
        if song['fc'] == 'fc':
            fc_img = resizePic(Image.open(
                pic_dir+'UI_MSS_MBase_Icon_FC.png'), 1.8)
            bg_img.paste(fc_img, (1010, margin_top[i][1]-25), fc_img)
        elif song['fc'] == 'fcp':
            fc_img = resizePic(Image.open(
                pic_dir+'UI_MSS_MBase_Icon_FCp.png'), 1.8)
            bg_img.paste(fc_img, (1010, margin_top[i][1]-25), fc_img)
        elif song['fc'] == 'ap':
            fc_img = resizePic(Image.open(
                pic_dir+'UI_MSS_MBase_Icon_AP.png'), 1.8)
            bg_img.paste(fc_img, (1010, margin_top[i][1]-25), fc_img)
        elif song['fc'] == 'app':
            fc_img = resizePic(Image.open(
                pic_dir+'UI_MSS_MBase_Icon_APp.png'), 1.8)
            bg_img.paste(fc_img, (1010, margin_top[i][1]-25), fc_img)

        # fc&ap
        fs_img = None
        if song['fs'] == 'fs':
            fs_img = resizePic(Image.open(
                pic_dir+'UI_MSS_MBase_Icon_fs.png'), 1.8)
            bg_img.paste(fs_img, (1100, margin_top[i][1]-25), fs_img)
        elif song['fs'] == 'fsp':
            fs_img = resizePic(Image.open(
                pic_dir+'UI_MSS_MBase_Icon_fsp.png'), 1.8)
            bg_img.paste(fs_img, (1100, margin_top[i][1]-25), fs_img)

        # achievements
        achievements = song['achievements']
        achievements = '' if achievements == 0 else f'{"%.4f" % achievements} %'
        achievements_font = ImageFont.truetype(adobe, 42, encoding='utf-8')
        bg_draw.text((1210, margin_top[i][1]-10), str(achievements),
                     font=achievements_font, fill='black')

        # rank
        # rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
        achievements = song['achievements']
        rank = computeRank(achievements)
        if achievements != 0:
            rank_img = resizePic(Image.open(
                pic_dir+f'UI_GAM_Rank_{rank}.png'), 1.4)
            bg_img.paste(rank_img, (1460, margin_top[i][1]-20), rank_img)

    return bg_img, 1
