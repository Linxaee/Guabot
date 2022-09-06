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
        subCity['dangerousAreas'] = item['dangerousAreas']
        province['subCity'].append(subCity)
    city_data.append(province)
