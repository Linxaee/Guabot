import random
import threading
from tkinter import Image
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Event, Bot
from src.libraries.image import image_to_base64
from src.libraries.tool import resizePic
from src.libraries.image import *

num_count = 0
di_flag = 1
max_time = 0
reset_flag = False
# run函数
def run():
    global max_time
    global num_count
    global di_flag
    global reset_flag
    if not reset_flag:
        max_time += 1
        # 60秒后停止定时器
        if max_time < 60:
            threading.Timer(1, run).start()
        else:
            num_count = 0
            di_flag = 1
            max_time = 0
    else:
        num_count = 0
        di_flag = 1
        max_time = 0
        reset_flag = False


send_dragon = on_command('瓜瓜 来点龙', aliases={'来点龙图', '/dragon', '随个龙'})


@send_dragon.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global num_count
    global di_flag
    global cancel_tim
    global max_time
    if num_count == 3:
        di_flag = 0
        if max_time == 0:
            run()
    flag = di_flag
    if flag == 1:
        now_count = num_count
        num_count = now_count + 1
        randomIndex = random.randint(0, 257)
        img = Image.open(
            f"src/static/dragon/{randomIndex}.png").convert('RGBA')
        if img.size[0]>500:
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
                    "text": f'你不许龙了,一分钟只许龙3次,等{60 - max_time}秒再龙,你先别急'
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
    global reset_flag
    if str(event.get_user_id()) in reset_white_list:
        img = Image.open(
            f"src/static/dragon/reset.png").convert('RGBA')
        img = resizePic(img, 0.5)
        reset_flag = True
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
    global num_count
    global di_flag
    global cancel_tim
    global max_time
    if num_count == 3:
        di_flag = 0
        if max_time == 0:
            run()
    flag = di_flag
    if flag == 1:
        now_count = num_count
        num_count = now_count + 1
        randomIndex = random.randint(0, 118)
        img = Image.open(
            f"src/static/fufu/{randomIndex}.png").convert('RGBA')
        print(img.size[0])
        if img.size[0]>400:
            img = resizePic(img, 0.4)
        await send_dragon.finish([{
            "type": "image",
            "data": {
                    "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            }
        }])
    else:
        img = Image.open(
            f"src/static/fufu/stop.png").convert('RGBA')
        img = resizePic(img, 0.5)
        await send_dragon.finish([{
            "type": "text",
            "data": {
                    "text": f'你不许fu了,一分钟只许fu3次,等{60 - max_time}秒再fu,你先别急'
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
    global reset_flag
    if str(event.get_user_id()) in reset_white_list:
        img = Image.open(
            f"src/static/fufu/reset.png").convert('RGBA')
        img = resizePic(img, 0.5)
        reset_flag = True
        await reset_dragon.finish([{
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