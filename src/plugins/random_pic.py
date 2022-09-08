import random
import threading
from tkinter import Image
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Event, Bot
from src.libraries.image import image_to_base64
from src.libraries.tool import resizePic
from src.libraries.image import *

dragon_num_count = 0
dragon_di_flag = 1
dragon_max_time = 0
dragon_reset_flag = False
fufu_num_count = 0
fufu_di_flag = 1
fufu_max_time = 0
fufu_reset_flag = False
# run函数


def dragon_run():
    global dragon_max_time
    global dragon_num_count
    global dragon_di_flag
    global dragon_reset_flag
    if not dragon_reset_flag:
        dragon_max_time += 1
        # 60秒后停止定时器
        if dragon_max_time < 60:
            threading.Timer(1, dragon_run).start()
        else:
            dragon_num_count = 0
            dragon_di_flag = 1
            dragon_max_time = 0
    else:
        dragon_num_count = 0
        dragon_di_flag = 1
        dragon_max_time = 0
        dragon_reset_flag = False


def fufu_run():
    global fufu_max_time
    global fufu_num_count
    global fufu_di_flag
    global fufu_reset_flag
    if not fufu_reset_flag:
        fufu_max_time += 1
        # 60秒后停止定时器
        if fufu_max_time < 60:
            threading.Timer(1, fufu_run).start()
        else:
            fufu_num_count = 0
            fufu_di_flag = 1
            fufu_max_time = 0
    else:
        fufu_num_count = 0
        fufu_di_flag = 1
        fufu_max_time = 0
        fufu_reset_flag = False


send_dragon = on_command('瓜瓜 来点龙', aliases={'来点龙图', '/dragon', '随个龙'})


@send_dragon.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global dragon_num_count
    global dragon_di_flag
    global dragon_max_time
    flag = dragon_di_flag
    if flag == 1:
        now_count = dragon_num_count
        dragon_num_count = now_count + 1
        if dragon_num_count == 3:
            dragon_di_flag = 0
            if dragon_max_time == 0:
                dragon_run()
        randomIndex = random.randint(0, 257)
        img = Image.open(
            f"src/static/dragon/{randomIndex}.png").convert('RGBA')

        if img.size[0] > 500:
            img = resizePic(img, 0.5)
        await send_dragon.finish([{
            "type": "image",
            "data": {
                    "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            }
        }])
    else:
        img = Image.open(
            f"src/static/dragon/stop.png").convert('RGBA')
        await send_dragon.finish([{
            "type": "text",
            "data": {
                    "text": f'你不许龙了,一分钟只许龙3次,等{60 - dragon_max_time}秒再龙,你先别急'
            },
        }, {
            "type": "image",
            "data": {
                    "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            }
        }])
reset_white_list = ['702611663', '1017649288']
reset_dragon = on_command('重置龙')


@reset_dragon.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global dragon_reset_flag
    if str(event.get_user_id()) in reset_white_list:
        img = Image.open(
            f"src/static/dragon/reset.png").convert('RGBA')
        img = resizePic(img, 0.5)
        dragon_reset_flag = True
        await reset_dragon.finish([{
            "type": "text",
            "data": {
                "text": '已重置，你就龙吧，最后害的还是你自己'
            }
        }, {
            "type": "image",
            "data": {
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            }
        }])
    else:
        img = Image.open(
            f"src/static/dragon/nonono.png").convert('RGBA')
        img = resizePic(img, 0.5)
        await reset_dragon.finish([{
            "type": "text",
            "data": {
                "text": '不要'
            }
        }, {
            "type": "image",
            "data": {
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            }
        }])

send_fu = on_command('瓜瓜 来点fu', aliases={'来点fufu', '/fufu', '随个fu'})


@send_fu.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global fufu_num_count
    global fufu_di_flag
    global fufu_max_time
    flag = fufu_di_flag
    if flag == 1:
        now_count = fufu_num_count
        fufu_num_count = now_count + 1
        if fufu_num_count == 3:
            fufu_di_flag = 0
            if fufu_max_time == 0:
                fufu_run()
        randomIndex = random.randint(0, 118)
        img = Image.open(
            f"src/static/fufu/{randomIndex}.png").convert('RGBA')
        print(img.size[0])
        if img.size[0] > 400:
            img = resizePic(img, 0.4)
        await send_fu.finish([{
            "type": "image",
            "data": {
                    "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            }
        }])
    else:
        img = Image.open(
            f"src/static/fufu/stop.png").convert('RGBA')
        img = resizePic(img, 0.5)
        await send_fu.finish([{
            "type": "text",
            "data": {
                    "text": f'你不许fu了,一分钟只许fu3次,等{60 - fufu_max_time}秒再fu,你先别急'
            },
        }, {
            "type": "image",
            "data": {
                    "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            }
        }])
reset_white_list = ['702611663', '1017649288']
reset_fu = on_command('重置fu')


@reset_fu.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global fufu_reset_flag
    if str(event.get_user_id()) in reset_white_list:
        img = Image.open(
            f"src/static/fufu/reset.png").convert('RGBA')
        img = resizePic(img, 0.5)
        fufu_reset_flag = True
        await reset_fu.finish([{
            "type": "text",
            "data": {
                "text": 'fufu已重置'
            }
        }, {
            "type": "image",
            "data": {
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            }
        }])
    else:
        img = Image.open(
            f"src/static/fufu/nonono.png").convert('RGBA')
        img = resizePic(img, 0.5)
        await reset_fu.finish([{
            "type": "text",
            "data": {
                "text": '不要'
            }
        }, {
            "type": "image",
            "data": {
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            }
        }])
