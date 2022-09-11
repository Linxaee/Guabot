import ast
import threading
from asyncio.windows_events import NULL
import csv
from multiprocessing import current_process
import os
import random
import re
import imghdr
from typing import Optional
import urllib.request
from PIL import Image
from nonebot import on_command, on_message, on_notice, require, get_driver, on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Message, Event, Bot, MessageSegment
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.matcher import Matcher
from src.libraries.image import *
from src.libraries.tool import *
from random import randint


def record_txt(dict, flag, img=NULL):
    # 0发文字 1发gif,2发png
    if flag == 0:
        return Message([
            {
                "type": "text",
                "data": {
                    "text": f"由用户:{dict['adder']} 添加于:{dict['time']}\n"
                }
            },
            {
                "type": "text",
                "data": {
                    "text": f"{dict['context']}"
                }
            }

        ])
    elif flag == 1:
        print(img)
        return Message([
            {
                "type": "text",
                "data": {
                    "text": f"由用户:{dict['adder']} 添加于:{dict['time']}\n"
                }
            },
            {
                "type": "image",
                "data": {
                    "file":  f"file:///{img}"
                }
            },

        ])
    else:
        return Message([
            {
                "type": "text",
                "data": {
                    "text": f"由用户:{dict['adder']} 添加于:{dict['time']}\n"
                }
            },
            {
                "type": "image",
                "data": {
                    "file":  f"base64://{str(image_to_base64(img), encoding='utf-8')}"
                }
            },

        ])


@event_preprocessor
async def preprocessor(bot, event, state):
    if hasattr(event, 'message_type') and event.message_type == "private" and event.sub_type != "friend":
        raise IgnoredException("not reply group temp message")


help = on_command('瓜瓜 help', aliases={'help'})


@help.handle()
async def _(bot: Bot, event: Event, state: T_State):
    help_str = '''可用命令如下：
今日舞萌 查看今天的舞萌运势
XXXmaimaiXXX什么 随机一首歌
随个[dx/标准][绿黄红紫白]<难度> 随机一首指定条件的乐曲
查歌<乐曲标题的一部分> 查询符合条件的乐曲
[绿黄红紫白]id<歌曲编号> 查询乐曲信息或谱面信息
<歌曲别名>是什么歌 查询乐曲别名对应的乐曲
定数查歌 <定数>  查询定数对应的乐曲
定数查歌 <定数下限> <定数上限>
分数线 <难度+歌曲id> <分数线> 详情请输入“分数线 帮助”查看'''
    await help.send(Message([{
        "type": "image",
        "data": {
            "file": f"base64://{str(image_to_base64(text_to_image(help_str)), encoding='utf-8')}"
        }
    }]))


async def _group_poke(bot: Bot, event: Event, state: dict) -> bool:
    value = (event.notice_type == "notify" and event.sub_type ==
             "poke" and event.target_id == int(bot.self_id))
    return value


poke = on_notice(rule=_group_poke, priority=10, block=True)


@poke.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if event.__getattribute__('group_id') is None:
        event.__delattr__('group_id')
    await poke.send(Message([{
        "type": "poke",
        "data": {
            "qq": f"{event.sender_id}"
        }
    }]))

sb_records = on_command('群友圣经', aliases={'来点圣经'})


@sb_records.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # group_id = event.get_session_id().split('_')[1]
    f = open('src/static/friends_sb_records.csv', 'r', encoding='utf-8')
    temp = f.readlines()
    f.close()
    res_list = []
    # 读取全部文件存入字典列表
    for line in temp:
        arr = line.strip().split(' ')
        for i in range(len(arr)):
            if len(arr) == 4:
                item = {}
                item['group_id'] = arr[0]
                item['time'] = arr[1]
                item['adder'] = arr[2]
                item['context'] = arr[3]
            else:
                print('长度不对啊这')
        res_list.append(item)
    # 随机选择一条
    # for res in res_list:
    #     if res['group_id'] != group_id:
    #         res_list.remove(res)
    if len(res_list) == 0:
        await sb_records.finish(
            '''
本群还没有圣经，可以通过如下指令添加:
瓜瓜 添加圣经 <文字/图片>
或者
瓜瓜 添加圣经
在bot回复后发送<文字/图片>
''')
    choice = random.choice(res_list)
    img_path = 'S:\\CodeField\\Guabot\\src\\static\\friends\\'
    if 'file-img' not in choice['context']:
        await sb_records.finish(record_txt(choice, 0))
    else:
        if 'gif' in choice['context']:
            file_name = choice['context']
            gif_path = f'{img_path}{file_name}'
            await sb_records.finish(record_txt(choice, 1, gif_path))
        else:
            file_name = choice['context']
            img = Image.open(
                f"src/static/friends/{file_name}").convert('RGBA')
            await sb_records.finish(record_txt(choice, 2, img))

# 图片添加文件夹


def add_to_folder(url):
    file_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())

    def createFile(path: str, fpath):
        urllib.request.urlretrieve(path, fpath)
    filepath = 'src/static/friends/'
    # 创建临时图片
    createFile(url, f'{filepath}temp.jpg')
    # 判断图片类型
    img_type = imghdr.what(f'{filepath}temp.jpg')
    # 删除临时图片
    os.remove(os.path.join(f'{filepath}temp.jpg'))
    # 创建原文件
    createFile(url, f'{filepath}file-img-{file_time}.{img_type}')


# 添加到csv


def add_to_csv(group_id, time, adder, context):
    file = open('src/static/friends_sb_records.csv',
                'a', encoding='utf-8', newline='')
    wf = csv.writer(file, delimiter=' ')
    wf.writerow([group_id, time, adder, context])


add_record = on_command('瓜瓜 添加圣经')


@add_record.handle()
async def _(bot: Bot, event: Event, state: T_State):
    raw_args = str(event.get_message()).strip()
    if event.message_type == "private":
        await add_record.finish("只允许群聊添加哦")
    else:
        if raw_args:
            # 将参数存入state以阻止后续再向用户询问参数
            state["context"] = raw_args  # 如果用户发送了参数则直接赋值


@add_record.got("context", prompt="请发送要添加的文本或图片")
async def arg_handle(bot: Bot, event: Event, state: T_State):
    # group_id = event.get_session_id().split('_')[1]
    group_id = 702611663
    current_time = get_current_time()
    if 'CQ:image' in state["context"]:
        pattern = re.compile(r'http.+')
        res = f'{state["context"]}'
        # 图片请求ur
        url = pattern.search(res).group()[:-1]
        # 将参数存入state以阻止后续再向用户询问参数
        state["context"] = url  # 如果用户发送了参数则直接赋值
        img_type, file_time = add_to_folder(state["context"])
        add_to_csv(group_id, current_time,
                   event.get_user_id(), f'file-img-{file_time}.{img_type}')
        await add_record.finish("圣经已添加")
    else:
        context = state["context"]
        context = f'"{context}"'
        add_to_csv(group_id, current_time,
                   event.get_user_id(), context)
        await add_record.finish("圣经已添加")
