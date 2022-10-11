# Author: xyb, Diving_Fish
import asyncio
from email.mime import image
from importlib.metadata import version
import os
import math
import random
from typing import Optional, Dict, List

import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.libraries.maimaidx_music import get_cover_len4_id, total_list
from src.libraries.tool import computeRa


scoreRank = 'D C B BB BBB A AA AAA S S+ SS SS+ SSS SSS+'.split(' ')
combo = ' FC FC+ AP AP+'.split(' ')
diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')


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


class DrawBest(object):

    def __init__(self, sdBest: BestList, dxBest: BestList, userName: str, playerRating: int, musicRating: int):
        self.sdBest = sdBest
        self.dxBest = dxBest
        self.userName = self._stringQ2B(userName)
        self.playerRating = playerRating
        self.musicRating = musicRating
        self.rankRating = self.playerRating - self.musicRating
        self.pic_dir = 'src/static/mai/pic/'
        self.cover_dir = 'src/static/mai/cover/'
        self.img = Image.open(
            self.pic_dir + 'gua_bg2.jpeg').convert('RGBA').filter(ImageFilter.GaussianBlur(3))
        self.ROWS_IMG = [2]
        for i in range(6):
            # 第二个参数上下图片间隔
            self.ROWS_IMG.append(120 + 220 * i)
        self.COLOUMS_IMG = []
        for i in range(6):
            self.COLOUMS_IMG.append(20 + 155 * i)
        for i in range(4):
            self.COLOUMS_IMG.append(860 + 155 * i)
        self.draw()

    def _Q2B(self, uchar):
        """单个字符 全角转半角"""
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e:  # 转完之后不是半角字符返回原来的字符
            return uchar
        return chr(inside_code)

    def _stringQ2B(self, ustring):
        """把字符串全角转半角"""
        return "".join([self._Q2B(uchar) for uchar in ustring])

    def _getCharWidth(self, o) -> int:
        widths = [
            (126, 1), (159, 0), (687, 1), (710, 0), (711, 1), (727,
                                                               0), (733, 1), (879, 0), (1154, 1), (1161, 0),
            (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369,
                                                         1), (8426, 0), (9000, 1), (9002, 2), (11021, 1),
            (12350, 2), (12351, 1), (12438, 2), (12442,
                                                 0), (19893, 2), (19967, 1), (55203, 2), (63743, 1),
            (64106, 2), (65039, 1), (65059, 0), (65131,
                                                 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
            (120831, 1), (262141, 2), (1114109, 1),
        ]
        if o == 0xe or o == 0xf:
            return 0
        for num, wid in widths:
            if o <= num:
                return wid
        return 1

    def _columWidth(self, s: str):
        res = 0
        for ch in s:
            res += self._getCharWidth(ord(ch))
        return res

    def _changeColumnWidth(self, s: str, len: int) -> str:
        res = 0
        sList = []
        for ch in s:
            res += self._getCharWidth(ord(ch))
            if res <= len:
                sList.append(ch)
        return ''.join(sList)

    def _resizePic(self, img: Image.Image, time: float):
        return img.resize((int(img.size[0] * time), int(img.size[1] * time)))

    def _findRaPic(self) -> str:
        num = '10'
        if self.playerRating < 1000:
            num = '01'
        elif self.playerRating < 2000:
            num = '02'
        elif self.playerRating < 3000:
            num = '03'
        elif self.playerRating < 4000:
            num = '04'
        elif self.playerRating < 5000:
            num = '05'
        elif self.playerRating < 6000:
            num = '06'
        elif self.playerRating < 7000:
            num = '07'
        elif self.playerRating < 8000:
            num = '08'
        elif self.playerRating < 8500:
            num = '09'
        return f'UI_CMN_DXRating_S_{num}.png'

    def _drawRating(self, ratingBaseImg: Image.Image):
        COLOUMS_RATING = [86, 100, 115, 130, 145]
        theRa = self.playerRating
        i = 4
        while theRa:
            digit = theRa % 10
            theRa = theRa // 10
            digitImg = Image.open(
                self.pic_dir + f'UI_NUM_Drating_{digit}.png').convert('RGBA')
            digitImg = self._resizePic(digitImg, 0.6)
            ratingBaseImg.paste(
                digitImg, (COLOUMS_RATING[i] - 2, 9), mask=digitImg.split()[3])
            i = i - 1
        return ratingBaseImg

    # 绘制边框
    def _text_border(self, myDraw: any, x, y, font, border_color, fill_color, text):
        # thin border
        myDraw.text((x - 1, y), text, font=font, fill=border_color)
        myDraw.text((x + 1, y), text, font=font, fill=border_color)
        myDraw.text((x, y - 1), text, font=font, fill=border_color)
        myDraw.text((x, y + 1), text, font=font, fill=border_color)

        # thicker border
        myDraw.text((x - 1, y - 1), text, font=font, fill=border_color)
        myDraw.text((x + 1, y - 1), text, font=font, fill=border_color)
        myDraw.text((x - 1, y + 1), text, font=font, fill=border_color)
        myDraw.text((x + 1, y + 1), text, font=font, fill=border_color)

        # now draw the text over it
        myDraw.text((x, y), text, font=font, fill=fill_color)

    # 绘制圆角
    def _circle_corner(self, img, radii):
        # 画圆（用于分离4个角）
        circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形
        # 原图
        img = img.convert("RGBA")
        w, h = img.size
        # 画4个角（将整圆分离为4个部分）
        alpha = Image.new('L', img.size, 255)
        alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
        alpha.paste(circle.crop((radii, 0, radii * 2, radii)),
                    (w - radii, 0))  # 右上角
        alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)),
                    (w - radii, h - radii))  # 右下角
        alpha.paste(circle.crop((0, radii, radii, radii * 2)),
                    (0, h - radii))  # 左下角
        # alpha.show()
        img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见
        return img

    # 绘制推荐
    def _drawRecommend(self, img: Image.Image, sdBest: BestList, dxBest: BestList):
        itemW = 330
        itemH = 220
        rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
        diffPic = 'BSC ADV EXP MST MST_Re'.split(' ')
        titleFontName = 'src/static/adobe_simhei.otf'
        offsetH = [490, 730, 980]
        # 推荐列表
        sdList = []
        dxList = []
        ReList = []
        # 分别选出sd和dx中符合条件的乐谱
        for sdItem in sdBest:
            if (sdItem.achievement < 100.5 and 100.5-sdItem.achievement < 0.2) or (sdItem.achievement < 100 and 100-sdItem.achievement < 0.2):
                sdList.append(sdItem)
        for dxItem in dxBest:
            if (dxItem.achievement < 100.5 and 100.5-dxItem.achievement < 0.2) or (dxItem.achievement < 100 and 100-dxItem.achievement < 0.2):
                dxList.append(dxItem)
        if len(sdList) > 2 and len(dxList) > 1:
            count = 0
            while count < 2:
                randomNum = random.randint(0, len(sdList)-1)
                if sdList[randomNum] not in ReList:
                    ReList.append(sdList[randomNum])
                    count = count + 1
                    continue
            ReList.append(dxList[random.randint(0, len(dxList)-1)])
        else:
            ReList.extend(sdList)
            ReList.extend(dxList)
            ReList = ReList[0:3]
        if len(ReList) < 3:
            imgDraw = ImageDraw.Draw(self.img)
            tipFont = ImageFont.truetype(
                'src/static/mht.ttf', 34, encoding='utf-8')
            self._text_border(imgDraw, 1360, 1050,
                              tipFont, (237, 125, 49), (255, 255, 255), '仅显示最多三条与sss+\nsss相差0.2以内的铺面')
        for num in range(0, len(ReList)):

            chartInfo = ReList[num]
            # 绘制模糊背景
            pngPath = self.cover_dir + \
                f'{get_cover_len4_id(chartInfo.idNum)}.jpeg'
            if not os.path.exists(pngPath):
                pngPath = self.cover_dir + '0031.jpeg'
            baseImg = Image.open(pngPath).convert('RGB')
            baseImg = self._resizePic(baseImg, itemW / baseImg.size[0])
            baseImg = baseImg.crop(
                (0, (baseImg.size[1] - itemH) / 2, itemW, (baseImg.size[1] + itemH) / 2))
            baseImg = baseImg.filter(ImageFilter.GaussianBlur(3))
            baseImg = self._circle_corner(baseImg, 30)

            baseDraw = ImageDraw.Draw(baseImg)

            # 绘制难度和版本
            diffPng = Image.open(
                self.pic_dir + f'UI_PFC_MS_Info02_{diffPic[chartInfo.diff]}.png')
            diffPng = self._resizePic(diffPng, 1.3)
            baseImg.paste(diffPng, (5, 5), diffPng)
            if chartInfo.tp == 'DX':
                versionPng = Image.open(
                    self.pic_dir + 'UI_UPE_Infoicon_DeluxeMode.png')
            else:
                versionPng = Image.open(
                    self.pic_dir + 'UI_UPE_Infoicon_StandardMode.png')
            versionPng = self._resizePic(versionPng, 1)
            baseImg.paste(versionPng, (190, 5), versionPng)

            # 绘制title
            title = chartInfo.title
            if self._columWidth(title) > 15:
                title = self._changeColumnWidth(title, 14) + '...'
            titleFont = ImageFont.truetype(titleFontName, 22, encoding='utf-8')
            self._text_border(baseDraw, 25, 40,
                              titleFont, 'black', 'white', title)
            # 绘制定数
            titleFont = ImageFont.truetype(titleFontName, 22, encoding='utf-8')
            self._text_border(baseDraw, 205, 40,
                              titleFont, 'black', 'white', '定数:' + str(chartInfo.ds))

            # 绘制当前rank&achievement
            if (chartInfo.achievement < 100):
                offsetLeft = 20
            else:
                offsetLeft = 15
            font = ImageFont.truetype(
                'src/static/mht.ttf', 22, encoding='utf-8')

            self._text_border(baseDraw, 25, 75,
                              font, 'black', 'white', '当前')
            curRankPng = Image.open(
                self.pic_dir + f'UI_GAM_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
            curRankPng = self._resizePic(curRankPng, 0.8)
            baseImg.paste(curRankPng, (offsetLeft, 108), curRankPng)

            self._text_border(baseDraw, 245, 75,
                              font, 'black', 'white', '目标')
            nextRankPng = Image.open(
                self.pic_dir + f'UI_GAM_Rank_{rankPic[chartInfo.scoreId+1]}.png').convert('RGBA')
            nextRankPng = self._resizePic(nextRankPng, 0.8)
            baseImg.paste(nextRankPng, (235, 108), nextRankPng)

            # 绘制达成率
            achFont = ImageFont.truetype(
                'src/static/mht.ttf', 24, encoding='utf-8')
            curAchText = f'{"%.4f" % chartInfo.achievement}% '
            self._text_border(baseDraw, 5, 145,
                              achFont, 'black', 'white', curAchText)
            if chartInfo.achievement < 100.5 and chartInfo.achievement > 100:
                nextAchText = '100.5000%'
            else:
                nextAchText = '100.0000%'
            self._text_border(baseDraw, 205, 145,
                              achFont, 'black', 'white', nextAchText)

            # 绘制箭头和差值

            if chartInfo.achievement < 100.5 and chartInfo.achievement > 100:
                up = f'{"%.4f" % (100.5 - chartInfo.achievement)}% '
            else:
                up = f'{"%.4f" % (100 - chartInfo.achievement)}% '
            arrowFont = ImageFont.truetype(
                'src/static/mht.ttf', 30, encoding='utf-8')
            self._text_border(baseDraw, 143, 110,
                              arrowFont, 'black', 'white', '->')
            upFont = ImageFont.truetype(
                'src/static/mht.ttf', 24, encoding='utf-8')
            self._text_border(baseDraw, 100, 85,
                              upFont, 'black', 'white', '+'+up)

            # 绘制rating
            if chartInfo.achievement < 100.5 and chartInfo.achievement > 100:
                nextAch = 100.5
            else:
                nextAch = 100
            ratingFont = ImageFont.truetype(
                'src/static/mht.ttf', 24, encoding='utf-8')
            curRa = computeRa(chartInfo.ds, nextAch)
            ratingText = f'Rating: {chartInfo.ra} -> {curRa} +{curRa-chartInfo.ra}'
            self._text_border(baseDraw, 25, 180,
                              ratingFont, 'black', 'white', ratingText)

            img.paste(baseImg, (1350, offsetH[num]), baseImg)

    def _drawBestList(self, img: Image.Image, sdBest: BestList, dxBest: BestList):
        itemW = 150
        itemH = 208
        Color = [(69, 193, 36), (255, 186, 1), (255, 90, 102),
                 (134, 49, 200), (217, 197, 233)]
        rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
        comboPic = ' FC FCp AP APp'.split(' ')
        diffPic = 'BSC ADV EXP MST Re'.split(' ')
        imgDraw = ImageDraw.Draw(img)
        titleFontName = 'src/static/adobe_simhei.otf'
        for num in range(0, len(sdBest)):
            i = num // 5
            j = num % 5

            chartInfo = sdBest[num]

            # 打开单个背景图(根据diff难度选择背景)
            baseImg = Image.open(
                self.pic_dir+f'UI_MYDIY_MBase_{diffPic[chartInfo.diff]}.jpeg')
            # 等比缩小单个背景图
            originW = baseImg.size[0]
            baseImg = self._resizePic(baseImg, itemW / baseImg.size[0])
            baseDraw = ImageDraw.Draw(baseImg)

            # 绘制cover
            pngPath = self.cover_dir + \
                f'{get_cover_len4_id(chartInfo.idNum)}.jpeg'
            if not os.path.exists(pngPath):
                pngPath = self.cover_dir + '1000.jpeg'
            pngTemp = Image.open(pngPath).convert('RGB')
            # 等比缩放
            pngTemp = self._resizePic(
                pngTemp, (itemW / originW)*(287 / 396))
            baseImg.paste(pngTemp, (21, 16))

            # 绘制title
            font = ImageFont.truetype(titleFontName, 16, encoding='utf-8')
            title = chartInfo.title
            if self._columWidth(title) > 15:
                title = self._changeColumnWidth(title, 14) + '...'
            # 计算出要写入的文字占用的像素
            w = font.getsize(title)
            baseDraw.text(
                ((baseImg.size[0] - w[0])/2, 155), title, 'white', font)

            # 绘制等级标识
            lvFont = ImageFont.truetype(
                'src/static/mht.ttf', 10, encoding='utf-8')
            border_color = (237, 125, 49)
            fill_color = (255, 255, 255)
            self._text_border(baseDraw, 98, 135, lvFont,
                              border_color, fill_color, 'Lv')
            diffFont = ImageFont.truetype(
                'src/static/mht.ttf', 19, encoding='utf-8')
            self._text_border(baseDraw, 113, 126,
                              diffFont, border_color, fill_color, str(chartInfo.ds))

            # 绘制rank
            rankPng = Image.open(
                self.pic_dir + f'UI_GAM_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
            rankPng = self._resizePic(rankPng, 0.6)
            baseImg.paste(rankPng, (20, 97), rankPng)

            # 绘制fc&fdx
            if chartInfo.comboId:
                comboImg = Image.open(
                    self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png').convert('RGBA')
                comboImg = self._resizePic(comboImg, 0.6)
                baseImg.paste(comboImg, (103, 98), comboImg.split()[3])

            # 绘制达成率
            if chartInfo.diff == 2:
                offsetH = itemH-24
            else:
                offsetH = itemH-22
            # 计算出要写入的文字占用的像素
            achText = f'{"%.4f" % chartInfo.achievement}% -> {chartInfo.ra}'
            w, h = font.getsize(achText)
            achFont = ImageFont.truetype(
                'src/static/mht.ttf', 14, encoding='utf-8')
            self._text_border(baseDraw, (baseImg.size[0] - w)/2+5, offsetH,
                              achFont, border_color, fill_color, achText)

            # 绘制id
            # 计算出要写入的文字占用的像素
            w, h = font.getsize(chartInfo.idNum)
            idFont = ImageFont.truetype(titleFontName, 14, encoding='utf-8')
            self._text_border(baseDraw, itemW-w-35, 22,
                              idFont, 'black', 'white', 'id:'+chartInfo.idNum)

            img.paste(
                baseImg, (self.COLOUMS_IMG[j] + 4, self.ROWS_IMG[i + 1] + 4), baseImg)
        # for num in range(len(sdBest), sdBest.size):
        #     i = num // 5
        #     j = num % 5
        #     temp = Image.open(self.cover_dir + f'1000.png').convert('RGB')
        #     temp = self._resizePic(temp, itemW / temp.size[0])
        #     temp = temp.crop(
        #         (0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
        #     temp = temp.filter(ImageFilter.GaussianBlur(1))
        #     img.paste(
        #         temp, (self.COLOUMS_IMG[j] + 4, self.ROWS_IMG[i + 1] + 4))
        for num in range(0, len(dxBest)):
            i = num // 3
            j = num % 3

            chartInfo = dxBest[num]

            # 打开单个背景图(根据diff难度选择背景)
            baseImg = Image.open(
                self.pic_dir+f'UI_MYDIY_MBase_{diffPic[chartInfo.diff]}.jpeg')
            # 等比缩小单个背景图
            originW = baseImg.size[0]
            baseImg = self._resizePic(baseImg, itemW / baseImg.size[0])
            baseDraw = ImageDraw.Draw(baseImg)

            # 绘制cover
            pngPath = self.cover_dir + \
                f'{get_cover_len4_id(chartInfo.idNum)}.jpeg'
            if not os.path.exists(pngPath):
                pngPath = self.cover_dir + '1000.jpeg'
            pngTemp = Image.open(pngPath).convert('RGB')
            # 等比缩放
            pngTemp = self._resizePic(
                pngTemp, (itemW / originW)*(287 / 396))
            baseImg.paste(pngTemp, (21, 16))

            # 绘制title
            font = ImageFont.truetype(titleFontName, 16, encoding='utf-8')
            title = chartInfo.title
            if self._columWidth(title) > 15:
                title = self._changeColumnWidth(title, 14) + '...'
            # 计算出要写入的文字占用的像素
            w = font.getsize(title)
            baseDraw.text(
                ((baseImg.size[0] - w[0])/2, 155), title, 'white', font)

            # 绘制等级标识
            lvFont = ImageFont.truetype(
                'src/static/mht.ttf', 10, encoding='utf-8')
            border_color = (237, 125, 49)
            fill_color = (255, 255, 255)
            self._text_border(baseDraw, 98, 135, lvFont,
                              border_color, fill_color, 'Lv')
            diffFont = ImageFont.truetype(
                'src/static/mht.ttf', 19, encoding='utf-8')
            self._text_border(baseDraw, 113, 126,
                              diffFont, border_color, fill_color, str(chartInfo.ds))

            # 绘制rank
            rankPng = Image.open(
                self.pic_dir + f'UI_GAM_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
            rankPng = self._resizePic(rankPng, 0.6)
            baseImg.paste(rankPng, (20, 97), rankPng)

            # 绘制fc&fdx
            if chartInfo.comboId:
                comboImg = Image.open(
                    self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png').convert('RGBA')
                comboImg = self._resizePic(comboImg, 0.6)
                baseImg.paste(comboImg, (103, 98), comboImg.split()[3])

           # 绘制达成率
            if chartInfo.diff == 2:
                offsetH = itemH-24
            else:
                offsetH = itemH-22
            # 计算出要写入的文字占用的像素
            achText = f'{"%.4f" % chartInfo.achievement}% -> {chartInfo.ra}'
            w, h = font.getsize(achText)
            achFont = ImageFont.truetype(
                'src/static/mht.ttf', 14, encoding='utf-8')
            self._text_border(baseDraw, (baseImg.size[0] - w)/2+5, offsetH,
                              achFont, border_color, fill_color, achText)

            # 绘制id
            # 计算出要写入的文字占用的像素
            w, h = font.getsize(chartInfo.idNum)
            idFont = ImageFont.truetype(titleFontName, 14, encoding='utf-8')
            self._text_border(baseDraw, itemW-w-35, 20,
                              idFont, 'black', 'white', 'id:'+chartInfo.idNum)

            img.paste(
                baseImg, (self.COLOUMS_IMG[j + 6] + 4, self.ROWS_IMG[i + 1] + 4), baseImg)
        # for num in range(len(dxBest), dxBest.size):
        #     i = num // 3
        #     j = num % 3
        #     temp = Image.open(self.cover_dir + f'1000.png').convert('RGB')
        #     temp = self._resizePic(temp, itemW / temp.size[0])
        #     temp = temp.crop(
        #         (0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
        #     temp = temp.filter(ImageFilter.GaussianBlur(1))
        #     img.paste(
        #         temp, (self.COLOUMS_IMG[j + 6] + 4, self.ROWS_IMG[i + 1] + 4))

    def draw(self):
        guaLogo = Image.open(
            self.pic_dir + 'gua_logo.png').convert('RGBA')
        guaLogo = self._resizePic(guaLogo, 0.5)
        self.img.paste(guaLogo, (-25, -85), mask=guaLogo.split()[3])

        ratingBaseImg = Image.open(
            self.pic_dir + self._findRaPic()).convert('RGBA')
        ratingBaseImg = self._drawRating(ratingBaseImg)
        ratingBaseImg = self._resizePic(ratingBaseImg, 0.85)
        self.img.paste(ratingBaseImg, (220, 8), mask=ratingBaseImg.split()[3])

        namePlateImg = Image.open(
            self.pic_dir + 'UI_TST_PlateMask.png').convert('RGBA')
        namePlateImg = namePlateImg.resize((285, 40))
        namePlateDraw = ImageDraw.Draw(namePlateImg)
        font1 = ImageFont.truetype('src/static/msyh.ttc', 28, encoding='unic')
        namePlateDraw.text((12, 4), ' '.join(
            list(self.userName)), 'black', font1)
        nameDxImg = Image.open(
            self.pic_dir + 'UI_CMN_Name_DX.png').convert('RGBA')
        nameDxImg = self._resizePic(nameDxImg, 0.9)
        namePlateImg.paste(nameDxImg, (210, 4), mask=nameDxImg.split()[3])
        self.img.paste(namePlateImg, (220, 40), mask=namePlateImg.split()[3])

        shougouImg = Image.open(
            self.pic_dir + 'UI_CMN_Shougou_Rainbow.png').convert('RGBA')
        shougouDraw = ImageDraw.Draw(shougouImg)
        font2 = ImageFont.truetype(
            'src/static/adobe_simhei.otf', 12, encoding='utf-8')
        playCountInfo = f'底分: {self.musicRating} + 段位分: {self.rankRating}'
        shougouImgW, shougouImgH = shougouImg.size
        playCountInfoW, playCountInfoH = shougouDraw.textsize(
            playCountInfo, font2)
        textPos = ((shougouImgW - playCountInfoW -
                   font2.getoffset(playCountInfo)[0]) / 2, 5)
        shougouDraw.text((textPos[0] - 1, textPos[1]),
                         playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1]),
                         playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0], textPos[1] - 1),
                         playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0], textPos[1] + 1),
                         playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] - 1, textPos[1] - 1),
                         playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1] - 1),
                         playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] - 1, textPos[1] + 1),
                         playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1] + 1),
                         playCountInfo, 'black', font2)
        shougouDraw.text(textPos, playCountInfo, 'white', font2)
        shougouImg = self._resizePic(shougouImg, 1.05)
        self.img.paste(shougouImg, (220, 83), mask=shougouImg.split()[3])

        # 绘制b40
        self._drawBestList(self.img, self.sdBest, self.dxBest)
        # 绘制推荐
        self._drawRecommend(self.img, self.sdBest, self.dxBest)

        # 绘制瓜瓜催收
        imgDraw = ImageDraw.Draw(self.img)
        guaFont = ImageFont.truetype(
            'src/static/mht.ttf', 60, encoding='utf-8')
        self._text_border(imgDraw, 1400, 400,
                          guaFont, (237, 125, 49), (255, 255, 255), '瓜瓜催收')

        guaguacsPng = Image.open(
            self.pic_dir + 'guaguacs_logo.png').convert('RGBA')
        guaguacsPng = self._resizePic(guaguacsPng, 0.38)
        self.img.paste(guaguacsPng, (1300, 18), guaguacsPng)

        authorBoardImg = Image.open(
            self.pic_dir + 'UI_CMN_MiniDialog_01.png').convert('RGBA')
        authorBoardImg = self._resizePic(authorBoardImg, 0.35)
        authorBoardDraw = ImageDraw.Draw(authorBoardImg)
        authorBoardDraw.text(
            (13, 28), '   Credit to\n   XybBot & Diving-fish\n   Generated by Guabot', 'black', font2)
        self.img.paste(authorBoardImg, (1150, 19),
                       mask=authorBoardImg.split()[3])

        dxImg = Image.open(
            self.pic_dir + 'UI_RSL_MBase_Parts_01.png').convert('RGBA')
        self.img.paste(dxImg, (870, 70), mask=dxImg.split()[3])
        sdImg = Image.open(
            self.pic_dir + 'UI_RSL_MBase_Parts_02.png').convert('RGBA')
        self.img.paste(sdImg, (685, 70), mask=sdImg.split()[3])

        # self.img.show()

    def getDir(self):
        return self.img


async def generate(payload: Dict):
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403
        sd_best = BestList(25)
        dx_best = BestList(15)
        obj = await resp.json()
        dx: List[Dict] = obj["charts"]["dx"]
        sd: List[Dict] = obj["charts"]["sd"]
        for c in sd:
            sd_best.push(ChartInfo.from_json(c))
        for c in dx:
            dx_best.push(ChartInfo.from_json(c))
        pic = DrawBest(sd_best, dx_best, obj["nickname"], obj["rating"] +
                       obj["additional_rating"], obj["rating"]).getDir()
        return pic, 0
