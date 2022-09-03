import re
import numpy as np  # 导入必要的库函数
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import requests
import json
from pyecharts.charts import Map, Geo
from PIL import Image

from nonebot import on_command, on_regex
from nonebot.typing import T_State
from nonebot.adapters import Event, Bot
from nonebot.adapters.cqhttp import Message
from src.libraries.image import *
from src.libraries.COVID_draw import generate
# query_internal = on_command('瓜瓜 国内疫情')
# @query_internal.handle()
# async def _(bot: Bot, event: Event, state: T_State):
#     url1 = "https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5"
#     resp=requests.get(url1)
#     listData=[]
#     listData=resp.json()
#     # listData1=json.loads(listData['data']) #把'data'转换成字典类型方便分析
#     print(listData.data.chinaTotal)

query_by_name = on_regex(r"^疫情动态 .+$")


@query_by_name.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "疫情动态 (.+)"
    res = re.match(regex, str(event.get_message())).groups()
    img, success = await generate(res[0])
    if success == 0:
        await query_by_name.finish(Message([
            {
                "type": "image",
                "data": {
                    "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
                }
            }
        ]))
    elif success == 233:
        await query_by_name.finish(Message([
            {
                "type": "text",
                "data": {
                    "text": "暂未查询到该地区信息！"
                }
            }
        ]))
    else:
        await query_by_name.finish(Message([
            {
                "type": "text",
                "data": {
                    "text": "发生未知错误，请联系Bot管理员！"
                }
            }
        ]))

