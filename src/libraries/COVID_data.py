from asyncio.windows_events import NULL
import time
from typing import Dict, List, Optional, Union, Tuple, Any
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np  # 导入必要的库函数
import pandas as pd
import re
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import requests
import json
from pyecharts.charts import Map, Geo
import hashlib
from typing import Optional
import requests


class cityList(List):
    def by_prov_name(self, name):
        for city in self:
            if city['prov_name'] == name:
                return city
        return NULL

    def by_subCity_name(self, name):
        for city in self:
            for subCity in city['subCity']:
                if subCity['city_name'] == name:
                    return subCity
        return NULL

    def judge(self, name):
        target = 0
        if name in ['国内', '全国', '中国']:
            target = 3
            return target
        for city in self:
            for subCity in city['subCity']:
                if subCity['city_name'] == name:
                    target = 1
                    return target
        for city in self:
            if city['prov_name'] == name:
                target = 2
                return target
        return target

# 获取新增


def get_data():

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
    }
    # 请求地址
    url = 'https://voice.baidu.com/act/newpneumonia/newpneumonia/?from=osari_aladin_banner'
    urlTX = 'https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=diseaseh5Shelf'
    # 发送请求
    response = requests.get(url=url, headers=headers)
    responseTX = requests.get(url=urlTX, headers=headers)
    # 数据解析
    data_html = response.text
    json_str = re.findall('"component":\[(.*)\],', data_html)[0]
    # 转换字典
    json_dict = json.loads(json_str)
    caseList = json_dict['caseList']
    city_data: cityList = cityList([])

    internal_data_temp = json.loads(responseTX.text)['data']
    internal_data_temp = internal_data_temp['diseaseh5Shelf']
    internal_data = {}
    internal_data['lastUpdateTime'] = internal_data_temp['lastUpdateTime']
    internal_data['chinaTotal'] = internal_data_temp['chinaTotal']

    # 循环获取各个地区的数据
    for item in caseList:
        province = {}
        province['prov_name'] = item['area']
        # 累计确诊
        province['confirmed'] = item['confirmed']
        # 现有确诊
        province['curConfirm'] = item['curConfirm']
        # 新增确诊
        province['confirmedRelative'] = item['confirmedRelative']
        # 新增本土确诊
        province['nativeRelative'] = item['nativeRelative']
        # 新增本土无症状
        province['asymptomaticLocalRelative'] = item['asymptomaticLocalRelative']
        # 累计死亡
        province['died'] = item['died']
        # 累计治愈
        province['cured'] = item['crued']
        # 更新时间
        province['relativeTime'] = time.strftime(
            "%Y-%m-%d", time.localtime(int(item['relativeTime'])))
        province['subCity'] = []
        for item in item['subList']:
            subCity = {}
            subCity['city_name'] = item['city']
            # 现有确诊
            subCity['curConfirm'] = item['curConfirm']
            # 新增本土确诊
            subCity['nativeRelative'] = item['nativeRelative']
            # 新增本土无症状
            subCity['asymptomaticLocalRelative'] = item['asymptomaticLocalRelative']
            # 累计确诊
            subCity['confirmed'] = item['confirmed']
            # 累计死亡
            subCity['died'] = item['died']
            # 累计治愈
            subCity['cured'] = item['crued']
            # 更新时间
            # subCity['updateTime'] = time.strftime(
            #     "%Y-%m-%d", time.localtime(int(item['updateTime'])))
            subCity['relativeTime'] = province['relativeTime']
            # 风险区
            province['subCity'].append(subCity)
        city_data.append(province)
    return city_data, internal_data


# 获取风险区

timestamp = str(int((time.time())))
token = '23y0ufFl5YxIyGrI8hWRUZmKkvtSjLQA'
nonce = '123456789abcdefg'
passid = 'zdww'
key = "3C502C97ABDA40D0A60FBEE50FAAD1DA"


def get_signature():
    zdwwsign = timestamp + 'fTN2pfuisxTavbTuYVSsNJHetwq5bJvC' + \
        'QkjjtiLM2dCratiA' + timestamp
    hsobj = hashlib.sha256()
    hsobj.update(zdwwsign.encode('utf-8'))
    signature = hsobj.hexdigest().upper()
    # print(zdwwsignature)
    return signature


def get_signature_header():
    has256 = hashlib.sha256()
    sign_header = timestamp + token + nonce + timestamp
    has256.update(sign_header.encode('utf-8'))
    signatureHeader = has256.hexdigest().upper()
    # print(signatureHeader)
    return signatureHeader


def get_level_data():
    url = 'https://bmfw.www.gov.cn/bjww/interface/interfaceJson'

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        # "Content-Length": "235",
        "Content-Type": "application/json; charset=UTF-8",
        "Host": "bmfw.www.gov.cn",
        "Origin": "http://bmfw.www.gov.cn",
        "Referer": "http://bmfw.www.gov.cn/yqfxdjcx/risk.html",
        # "Sec-Fetch-Dest": "empty",
        # "Sec-Fetch-Mode": "cors",
        # "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 SE 2.X MetaSr 1.0",
        "x-wif-nonce": "QkjjtiLM2dCratiA",
        "x-wif-paasid": "smt-application",
        "x-wif-signature": get_signature(),
        "x-wif-timestamp": timestamp
    }

    params = {
        'appId': "NcApplication",
        'paasHeader': "zdww",
        'timestampHeader': timestamp,
        'nonceHeader': "123456789abcdefg",
        'signatureHeader': get_signature_header(),
        'key': "3C502C97ABDA40D0A60FBEE50FAAD1DA"
    }

    resp = requests.post(url, headers=headers, json=params)
    data = resp.text

    # 在线获取后，保存到本地，再进行本地整理操作，减少在线访问，以免被封IP
    with open('src/static/COVID/risk_data.log', 'w', encoding='utf-8') as f:
        f.write(data)


def get_high_list(data, name):
    high_list = []
    data = data['highlist']
    for item in data:
        # print()
        if name in item['city']:
            for address in item['communitys']:
                high_item = {}
                county = item['county']
                high_item['area'] = f'{county}{address}'
                high_item['level'] = '高风险'
                high_list.append(high_item)
    return high_list


def get_mid_list(data, name):
    mid_list = []
    data = data['middlelist']
    for item in data:
        # print()
        if name in item['city']:
            for address in item['communitys']:
                mid_item = {}
                county = item['county']
                mid_item['area'] = f'{county}{address}'
                mid_item['level'] = '中风险'
                mid_list.append(mid_item)
    return mid_list


def get_level_list(name: str):
    get_level_data()
    with open('src/static/COVID/risk_data.log', 'r', encoding='utf-8') as f:
        data_dic = json.loads(f.read())['data']
        # 获取高风险区
        sub_list = []
        high_list = get_high_list(data_dic, name)
        mid_list = get_mid_list(data_dic, name)
        sub_list.extend(high_list)
        sub_list.extend(mid_list)
        return sub_list
