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
from nonebot.adapters.cqhttp import Message, Event, Bot, MessageSegment
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.matcher import Matcher
from src.libraries.image import *
from src.libraries.tool import *


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


help = on_command('瓜瓜 help', aliases={'help', '/help'})


@help.handle()
async def _(bot: Bot, event: Event, state: T_State):
    help_str = '''瓜瓜bot使用指南
例子中<>中内容代表需要填入项，[]中内容代表选择其中一项,()中内容代表可选项，
输入指令时均不需要携带括号本身，同时请注意指令是否需要空格

可用命令如下：
maimai相关
---------------------
1. 今日运势
查看今日舞萌运势
例：今日运势

2. XXXmaimaiXXX什么
随机一首歌
例：maimai什么歌最难

3. 随个[dx/标准] [绿黄红紫白]<难度> 
随机一首指定条件的乐曲
例：随个红13

4. 查歌 <乐曲标题的一部分> 
查询符合条件的乐曲
例：查歌 奏者

5. [绿黄红紫白]id<歌曲编号>
查询乐曲信息或谱面信息
例：红id823

6. 定数查歌 <定数> 
查询定数对应的乐曲
例：定数查歌 13

7. 定数查歌 <定数下限> <定数上限>
查询定数处于给定范围的乐曲
例：定数查歌 13.0 13.2

8. 分数线 <难度+歌曲id> <分数线> 
详情请输入“分数线 帮助”查看

9. 瓜瓜 b40/b40/查<用户名>成分
查看自己或者某位用户的b40
例：查Linxae成分

10. 瓜瓜 底分分析/底分分析
查看乐曲推荐和底分分析

11. <歌曲别名>是什么歌
查询乐曲别名对应的乐曲
例：太空熊是什么歌

12. <歌曲别名>有什么别名
查询乐曲的其它别名
例：太空熊有什么别名

13. 添加别名 <歌曲id> <歌曲别名>
为指定id的歌曲添加别名
例：添加别名 823 奏者背中提琴语

14. <标级>定数表 (仅支持8-15）
查看某标级定数表
例：14+定数表

15. <标级>完成表  (仅支持8-15）
查看某标级rank完成表
例：14+完成表

16. <标级>分数列表 (页号)  (仅支持8-15）
查看某标级分数列表
例：13分数列表 / 14+分数列表 

17. <牌子名>进度
查看某牌子进度
例：堇神进度

18. <牌子名>完成表
查看牌子完成表
例：堇神完成表

娱乐相关
---------------------------
1. 瓜瓜 来点龙 / 来点龙图 / /dragon /随个龙
随机一张龙图

2. 瓜瓜 来点fu / 来点fufu / /fufu /随个fu
随机一张fufu

3. 群友圣经
随机一份群友圣经

4. 瓜瓜 添加圣经 <需添加内容> 
为本群添加圣经
例：瓜瓜 添加圣经 哦哦哦哦哦哦 / 一张图片

疫情相关
-------------------------
1. 疫情动态 <市名/国内>
查看某市或者国内疫情动态
例：疫情动态 成都 / 疫情动态 国内

2. 风险区 <市名> <区名/关键字> (页码)
查看某地区风险区列表
例：风险区 成都 新都 / 风险区 成都 / 风险区 成都 2'''
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
    group_id = event.get_session_id().split('_')[1]
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

    for res in res_list:
        if res['group_id'] != group_id:
            res_list.remove(res)
    if len(res_list) == 0:
        await sb_records.finish(
            '''
本群还没有圣经，可以通过如下指令添加:
瓜瓜 添加圣经 <文字/图片>
或者
瓜瓜 添加圣经
在bot回复后发送<文字/图片>
''')
    # 随机选择一条
    random.shuffle(res_list)
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
    return img_type, file_time

# 添加到csv


def add_to_csv(group_id, time, adder, context):
    file = open('src/static/friends_sb_records.csv',
                'a', encoding='utf-8', newline='')
    wf = csv.writer(file, delimiter=' ')
    wf.writerow([group_id, time, adder, context])
    file.close()


add_record = on_command('瓜瓜 添加圣经')


@add_record.handle()
async def _(bot: Bot, event: Event, state: T_State):
    raw_args = str(event.get_message()).strip()
    if event.message_type == "private":
        await add_record.finish("只允许群聊添加哦")
    else:
        if raw_args:
            state["context"] = raw_args  # 如果用户发送了参数则直接赋值


@add_record.got("context", prompt="请发送要添加的文本或图片")
async def arg_handle(bot: Bot, event: Event, state: T_State):
    # 群聊id
    group_id = event.get_session_id().split('_')[1]
    current_time = get_current_time()
    try:
        # 判断是否是图片消息
        if 'CQ:image' in state["context"]:
            pattern = re.compile(r'http.+')  # 匹配图片链接
            res = f'{state["context"]}'
            url = pattern.search(res).group()[:-1]  # search图片请求url
            state["context"] = url  # 将参数存入state以阻止后续再向用户询问参数
            img_type, file_time = add_to_folder(state["context"])   # 存入文件夹
            add_to_csv(group_id, current_time,
                       event.get_user_id(), f'file-img-{file_time}.{img_type}')  # 写入csv
            await add_record.finish("圣经已添加")
        else:
            # 文字消息则直接写入
            context = state["context"]
            add_to_csv(group_id, current_time,
                       event.get_user_id(), context)
            await add_record.finish("圣经已添加")
    except IOError as e:
        await add_record.finish("发生未知错误,请联系bot管理员")
