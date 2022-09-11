import json
import time
import requests
from nonebot import on_command, require, get_driver, get_bots
from nonebot.adapters.cqhttp import MessageSegment
import asyncio
import os
from random import randint

from src.libraries.COVID_data import get_level_data
from .config import Config

__plugin_name__ = 'timing'
__plugin_usage__ = '用法：在规定时间触发发送的信息。'


# 发送图片时用到的函数, 返回发送图片所用的编码字符串
# def send_img(img_name):
#     global img_path
#     return MessageSegment.image(img_path + img_name)


# 设置一个定时器
timing = require("nonebot_plugin_apscheduler").scheduler

# 12点更新日更数据


def write_today_events():
    url = 'http://v.juhe.cn/todayOnhistory/queryEvent.php'
    key = '488593dc256349e8f06f5d3d13614a6a'
    date = time.strftime('%#m/%d', time.localtime())
    data_list = requests.get(url+f'?key={key}&date={date}')
    data_list = json.loads(data_list.text)
    if data_list['reason'] == 'success':
        with open('src/static/public/today_events.log', 'w', encoding='utf-8') as f:
            f.write(str(data_list))
            f.close()


@timing.scheduled_job('cron', hour=0, minute=0, id='update_daily_data')
async def update_daily_data():
    # 历史上的今天
    write_today_events()


@timing.scheduled_job('cron', hour=12, minute=0, id='update_daily_data')
async def update_COVID_data():
    # 风险区数据
    get_level_data()
# @timing.scheduled_job("cron", hour=22, minute=55, id="drink_tea")
# async def drink_tea():
#     write_today_events()
#     bot, = get_bots().values()
#     group_id = 781295772
#     await bot.send_group_msg(group_id=group_id, message="定时器测试消息")
    # # 发送一条群聊信息
    # await bot.send_msg(
    #     message_type="group",
    #     # 群号
    #     group_id=12345678,
    #     message='这是一条群聊信息' + send_img('三点饮茶.gif')
    # )
