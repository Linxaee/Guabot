from asyncio.windows_events import NULL
import csv
import os
import random
import re
import imghdr
import urllib.request
from PIL import Image
from nonebot import on_command, on_message, on_notice, require, get_driver, on_regex
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, Event, Bot, MessageSegment
from nonebot.params import State, CommandArg, ArgPlainText, Arg, ArgStr
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.matcher import Matcher
from nonebot.params import State
from src.libraries.image import *
from src.libraries.tool import *


def record_txt(dict, flag, img=NULL):
    # 0发文字 1发gif,2发png
    if flag == 0:
        return Message([
            MessageSegment(type='text', data={
                       "text":  f"由用户: {dict['adder']} 添加于: {dict['time']}\n"}),
            MessageSegment(type='text', data={
                "text":  f"{dict['context']}"}),
        ])
    elif flag == 1:
        return Message([
            MessageSegment(type='text', data={
                       "text":  f"由用户: {dict['adder']} 添加于: {dict['time']}\n"}),
            MessageSegment(type='image', data={
                "file":   f"file:///{img}"}),
        ])
    else:
        return Message([
            MessageSegment(type='text', data={
                       "text":  f"由用户: {dict['adder']} 添加于: {dict['time']}\n"}),
            MessageSegment(type='image', data={
                "file":   f"base64://{str(image_to_base64(img), encoding='utf-8')}"}),
        ])


@event_preprocessor
async def preprocessor(bot, event, state:  T_State = State()):
    if hasattr(event, 'message_type') and event.message_type == "private" and event.sub_type != "friend":
        raise IgnoredException("not reply group temp message")


help = on_command('瓜瓜 help', aliases={'help'}, block=True)


@help.handle()
async def _(bot:  Bot, event:  Event, state:  T_State = State()):
    help_str = '''瓜瓜bot使用指南
例子中<>中内容代表需要填入项，[]中内容代表选择其中一项,()中内容代表可选项，
输入指令时均不需要携带括号本身，同时请注意指令是否需要空格

可用命令如下：

maimai相关
---------------------
1. 今日运势: 查看今日舞萌运势
2. XXXmaimaiXXX什么: 随机一首歌

3. 随个[dx/标准] [绿黄红紫白]<难度>: 随机一首指定条件的乐曲
4. 查歌 <乐曲标题的一部分>: 查询符合条件的乐曲
5. [绿黄红紫白]id<歌曲编号>: 查询乐曲信息或谱面信息

6. 定数查歌 <定数>: 查询定数对应的乐曲
7. 定数查歌 <定数下限> <定数上限>: 查询定数处于给定范围的乐曲
8. 分数线 <难度+歌曲id> <分数线>: 详情请输入“分数线 帮助”查看

9. 瓜瓜 b40/b40/查<用户名>成分: 查看自己或者某位用户的b40
10. 瓜瓜 底分分析/底分分析: 查看乐曲推荐和底分分析

11. <歌曲别名>是什么歌: 查询乐曲别名对应的乐曲
12. <歌曲别名>有什么别名: 查询乐曲的其它别名
13. 添加别名 <歌曲id> <歌曲别名>: 为指定id的歌曲添加别名

14. <标级>定数表 (仅支持8-15）: 查看某标级定数表
15. <标级>完成表  (仅支持8-15）: 查看某标级rank完成表
16. <标级>分数列表 (页号)  (仅支持8-15）: 查看某标级分数列表

17. <牌子名>进度: 查看某牌子进度
18. <牌子名>完成表: 查看牌子完成表

19. info [别名/id]: 查看单曲成绩

20.瓜瓜 <机厅名称>几/<机厅名称><人数>: 查看机厅人数纪录/纪录机厅人数
21.机厅列表: 查看记录的机厅列表
22.添加机厅 <机厅名称>: 纪录一个新的机厅
23.删除机厅 <机厅名称>: 删除一个记录的机厅

疫情相关
-------------------------
1. 疫情动态 <市名/国内>: 查看某市或者国内疫情动态
2. 风险区 <市名> <区名/关键字> (页码): 查看某地区风险区列表'''
    await help.send('瓜瓜bot使用指南生成ing')
    await help.finish(Message(
        [MessageSegment(type='image', data={
            "file":  f"base64://{str(image_to_base64(text_to_image(help_str)), encoding='utf-8')}"
        })]))


async def _group_poke(bot:  Bot, event:  Event, state:  T_State = State()) -> bool:
    value = (event.notice_type == "notify" and event.sub_type ==
             "poke" and event.target_id == int(bot.self_id))
    return value


poke = on_notice(rule=_group_poke, priority=10, block=True)


@poke.handle()
async def _(bot:  Bot, event:  Event, state:  T_State = State()):
    if event.__getattribute__('group_id') is None:
        event.__delattr__('group_id')
    await poke.send(Message([{
        "type":  "poke",
        "data":  {
            "qq":  f"{event.sender_id}"
        }
    }]))

bully_me = on_command('骂我')


@bully_me.handle()
async def _(bot:  Bot, event:  Event, state:  T_State = State()):
    list = ['爬爬爬', '一边去', '喊我本体骂', '笨比',
            '你打maimai像滴蜡熊',  '给你一拳', '你好像那个傻篮子', '你是抖m?', '绝赞给你打落', '你今天上机必被吃绝赞', '给你一脚']
    await bully_me.finish(random.choice(list))
