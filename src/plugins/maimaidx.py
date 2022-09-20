from collections import defaultdict
import datetime
from operator import truth
import time
import traceback

from nonebot import on_command, on_regex
from nonebot.typing import T_State
from nonebot.adapters import Event, Bot
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.params import State, CommandArg, Command
from src.libraries.maimai_pic_draw_func import create_plate_text, draw_com_list, draw_plate_img, draw_score_list, draw_single_record, get_plate_ach
from src.libraries.tool import hash, resizePic
from src.libraries.maimaidx_music import *
from src.libraries.image import *
from src.libraries.maimai_best_40 import generate
from src.libraries.maimai_pic_draw_func import draw_recommend_pic
import re


def song_txt(music: Music):
    return Message([
        MessageSegment(type='text', data={
                       'text': f"{music.id}. {music.title}\n"}),
        MessageSegment(type='image', data={
                       "file": f"https://www.diving-fish.com/covers/{get_cover_len4_id(music.id)}.png"}),
        MessageSegment(type='text', data={
                       "text" f"\n{'/'.join(music.level)}"}),
    ])


def inner_level_q(ds1, ds2=None):
    result_set = []
    diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'ReM']
    if ds2 is not None:
        music_data = total_list.filter(ds=(ds1, ds2))
    else:
        music_data = total_list.filter(ds=ds1)
    for music in sorted(music_data, key=lambda i: int(i['id'])):
        for i in music.diff:
            result_set.append(
                (music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
    return result_set


inner_level = on_command('inner_level ', aliases={'定数查歌 '})


@inner_level.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    argv = str(event.get_message()).strip().split(" ")
    if len(argv) > 2 or len(argv) == 0:
        await inner_level.finish("命令格式为\n定数查歌 <定数>\n定数查歌 <定数下限> <定数上限>")
        return
    if len(argv) == 1:
        result_set = inner_level_q(float(argv[0]))
    else:
        result_set = inner_level_q(float(argv[0]), float(argv[1]))
    if len(result_set) > 50:
        await inner_level.finish(f"结果过多（{len(result_set)} 条），请缩小搜索范围。")
        return
    s = ""
    for elem in result_set:
        s += f"{elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})\n"
    await inner_level.finish(s.strip())


spec_rand = on_regex(r"^随个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?")


@spec_rand.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    level_labels = ['绿', '黄', '红', '紫', '白']
    regex = "随个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)"
    res = re.match(regex, str(event.get_message()).lower())
    try:
        if res.groups()[0] == "dx":
            tp = ["DX"]
        elif res.groups()[0] == "sd" or res.groups()[0] == "标准":
            tp = ["SD"]
        else:
            tp = ["SD", "DX"]
        level = res.groups()[2]
        if res.groups()[1] == "":
            music_data = total_list.filter(level=level, type=tp)
        else:
            music_data = total_list.filter(
                level=level, diff=['绿黄红紫白'.index(res.groups()[1])], type=tp)
        if len(music_data) == 0:
            rand_result = "没有这样的乐曲哦。"
        else:
            rand_result = song_txt(music_data.random())
        await spec_rand.send(rand_result)
    except Exception as e:
        print(e)
        await spec_rand.finish("随机命令错误，请检查语法")


mr = on_regex(r".*maimai.*什么")


@mr.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    await mr.finish(song_txt(total_list.random()))


search_music = on_regex(r"^查歌.+")


@search_music.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    regex = "查歌(.+)"
    name = re.match(regex, str(event.get_message())).groups()[0].strip()
    if name == "":
        return
    res = total_list.filter(title_search=name)
    if len(res) == 0:
        await search_music.send("没有找到这样的乐曲。")
    elif len(res) < 50:
        search_result = ""
        for music in sorted(res, key=lambda i: int(i['id'])):
            search_result += f"{music['id']}. {music['title']}\n"
        await search_music.finish(Message([
            MessageSegment(type='text', data={"text": search_result.strip()})
        ]))
    else:
        await search_music.send(f"结果过多（{len(res)} 条），请缩小查询范围。")

query_chart = on_regex(r"^([绿黄红紫白]?)id([0-9]+)")


@query_chart.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    regex = "([绿黄红紫白]?)id([0-9]+)"
    groups = re.match(regex, str(event.get_message())).groups()
    level_labels = ['绿', '黄', '红', '紫', '白']
    if groups[0] != "":
        try:
            level_index = level_labels.index(groups[0])
            level_name = ['Basic', 'Advanced',
                          'Expert', 'Master', 'Re: MASTER']
            name = groups[1]
            music = total_list.by_id(name)
            chart = music['charts'][level_index]
            ds = music['ds'][level_index]
            level = music['level'][level_index]
            file = f"https://www.diving-fish.com/covers/{get_cover_len4_id(music['id'])}.png"
            if len(chart['notes']) == 4:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
BREAK: {chart['notes'][3]}
谱师: {chart['charter']}'''
            else:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
TOUCH: {chart['notes'][3]}
BREAK: {chart['notes'][4]}
谱师: {chart['charter']}'''
            await query_chart.send(Message([
                MessageSegment(type='text', data={
                    "text": f"{music['id']}. {music['title']}\n"}),
                MessageSegment(type='text', data={
                    "file": f"{file}"}),
                MessageSegment(type='text', data={
                    "text": msg}),
            ]))
        except Exception:
            await query_chart.send("未找到该谱面")
    else:
        name = groups[1]
        music = total_list.by_id(name)
        try:
            file = f"https://www.diving-fish.com/covers/{get_cover_len4_id(music['id'])}.png"
            await query_chart.send(Message([
                MessageSegment(type='text', data={
                    "text": f"{music['id']}. {music['title']}\n"}),
                MessageSegment(type='image', data={
                    "file": f"{file}"}),
                MessageSegment(type='text', data={
                    "text": f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}"}),
            ]))
        except Exception:
            await query_chart.send("未找到该乐曲")


def get_today_events():
    data = ''
    with open('src/static/public/today_events.log', 'r', encoding='utf-8') as f:
        data = f.read()
        # str对象不可变，先变为数组再join成字符串
        list_str = []
        for char in data:
            if char == '\'':
                char = '\"'
            list_str.append(char)
        data = ''.join(list_str)
        f.close()
    data_dict = json.loads(data)
    res = data_dict['result']
    res = random.sample(res, 2)
    return res


wm_list = ['拼机', '推分', '越级', '下埋', '夜勤',
           '干饭',  '收歌', '睡觉', '喝可乐', '学习', '打apex', '打csgo', '打lol', '睡大觉', ]


jrwm = on_command('今日舞萌', aliases={'今日mai', '今日运势'})


@jrwm.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    events_list = get_today_events()
    qq = int(event.get_user_id())
    h = hash(qq)
    rp = h % 100
    wm_value = []
    for i in range(11):
        wm_value.append(h & 3)
        h >>= 2
    s = f"今日人品值：{rp}\n"
    for i in range(11):
        if wm_value[i] == 3:
            s += f'宜 {wm_list[i]}\n'
        elif wm_value[i] == 0:
            s += f'忌 {wm_list[i]}\n'
    s += f'历史上的今天：\n'
    for i in range(len(events_list)):
        event = events_list[i]
        date = event['date']
        title = event['title']
        s += f'{date} {title}\n'
    s += "今日推荐歌曲："
    music = total_list[h % len(total_list)]
    await jrwm.finish(Message([
        MessageSegment(type='text', data={
                       "text": s}),
    ] + song_txt(music)))

query_score = on_command('分数线')


@query_score.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    r = "([绿黄红紫白])(id)?([0-9]+)"
    argv = str(event.get_message()).strip().split(" ")
    print(argv)
    if len(argv) == 2 and argv[1] == '帮助':
        s = '''此功能为查找某首歌分数线设计。
命令格式：分数线 <难度+歌曲id> <分数线>
例如：分数线 紫799 100
命令将返回分数线允许的 TAP GREAT 容错以及 BREAK 50落等价的 TAP GREAT 数。
以下为 TAP GREAT 的对应表：
GREAT/GOOD/MISS
TAP\t1/2.5/5
HOLD\t2/5/10
SLIDE\t3/7.5/15
TOUCH\t1/2.5/5
BREAK\t5/12.5/25(外加200落)'''
        await query_score.send(Message([
            MessageSegment(type='image', data={
                "file": f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"}),
        ]))
    elif len(argv) == 2:
        try:
            grp = re.match(r, argv[0]).groups()
            level_labels = ['绿', '黄', '红', '紫', '白']
            level_labels2 = ['Basic', 'Advanced',
                             'Expert', 'Master', 'Re:MASTER']
            level_index = level_labels.index(grp[0])
            chart_id = grp[2]
            line = float(argv[1])
            music = total_list.by_id(chart_id)
            chart: Dict[Any] = music['charts'][level_index]
            tap = int(chart['notes'][0])
            slide = int(chart['notes'][2])
            hold = int(chart['notes'][1])
            touch = int(chart['notes'][3]) if len(chart['notes']) == 5 else 0
            brk = int(chart['notes'][-1])
            total_score = 500 * tap + slide * 1500 + hold * 1000 + touch * 500 + brk * 2500
            break_bonus = 0.01 / brk
            break_50_reduce = total_score * break_bonus / 4
            reduce = 101 - line
            if reduce <= 0 or reduce >= 101:
                raise ValueError
            await query_chart.send(f'''{music['title']} {level_labels2[level_index]}
分数线 {line}% 允许的最多 TAP GREAT 数量为 {(total_score * reduce / 10000):.2f}(每个-{10000 / total_score:.4f}%),
BREAK 50落(一共{brk}个)等价于 {(break_50_reduce / 100):.3f} 个 TAP GREAT(-{break_50_reduce / total_score * 100:.4f}%)''')
        except Exception:
            await query_chart.send("格式错误，输入“分数线 帮助”以查看帮助信息")


best_40_pic = on_command('瓜瓜 b40', aliases={'b40', 'B40', '逼40'}, block=True)


@best_40_pic.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    payload = {'qq': str(event.get_user_id())}
    img, success = await generate(payload)
    if success == 400:
        await best_40_pic.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    elif success == 403:
        await best_40_pic.send("该用户禁止了其他人获取数据。")
    else:
        await best_40_pic.send('生成中，请稍等')
        await best_40_pic.send(Message([
            MessageSegment(type='image', data={
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"})]), at_sender=True)

best_40_pic_cf = on_regex('查.+成分')


@best_40_pic_cf.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    regex = "查(.+)成分"
    res = re.match(regex, str(event.get_message())
                   ).groups()[0].strip().lower()
    username = res
    if username == "":
        await best_40_pic_cf.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    else:
        payload = {'username': username}
    img, success = await generate(payload)
    if success == 400:
        await best_40_pic_cf.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    elif success == 403:
        await best_40_pic_cf.send("该用户禁止了其他人获取数据。")
    else:
        await best_40_pic_cf.send('生成中，请稍等')
        await best_40_pic_cf.send(Message([
            MessageSegment(type='image', data={
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"})
        ]), at_sender=True)
# best_50_pic = on_command('b50')
# @best_50_pic.handle()
# async def _(bot: Bot, event: Event, state: T_State = State()):
#     username = str(event.get_message()).strip()
#     if username == "":
#         payload = {'qq': str(event.get_user_id()), 'b50': True}
#     else:
#         payload = {'username': username, 'b50':  True}
#     img, success = await generate50(payload)
#     if success == 400:
#         await best_50_pic.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
#     elif success == 403:
#         await best_50_pic.send("该用户禁止了其他人获取数据。")
#     else:
#         await best_50_pic.send(Message([
#             {
#                 "type": "image",
#                 "data": {
#                     "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
#                 }
#             }
#         ]))

# ------------------------------------------------自编写区-----------------------------------------------------------

# 推分推荐

recommend_score = on_command('瓜瓜 底分分析', block=True)


@recommend_score.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    payload = {'qq': str(event.get_user_id())}
    img, success = await draw_recommend_pic(payload)
    if success == 400:
        await recommend_score.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    elif success == 403:
        await recommend_score.send("该用户禁止了其他人获取数据。")
    else:
        await recommend_score.send('生成中，请稍等')
        await recommend_score.send(Message([
            MessageSegment(type='image', data={
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"})
        ]), at_sender=True)


def get_aliases():
    f = open('src/static/aliases.csv', 'r', encoding='utf-8')
    tmp = f.readlines()
    f.close()
    for t in tmp:
        arr = t.strip().split('\t')
        for i in range(len(arr)):
            if arr[i] != "":
                music_aliases[arr[i].lower()].append(arr[0])
                anti_aliases[arr[0].lower()].append(arr[i])
    return music_aliases, anti_aliases


music_aliases = defaultdict(list)
anti_aliases = defaultdict(list)
music_aliases, anti_aliases = get_aliases()

# xx是什么歌
find_song = on_regex(r".+是什么歌")


@find_song.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    regex = "(.+)是什么歌"
    name = re.match(regex, str(event.get_message())
                    ).groups()[0].strip().lower()
    if name not in music_aliases:
        await find_song.finish("未找到此歌曲\n可能是已经寄了")
    result_set = music_aliases[name]
    if len(result_set) == 1:
        music = total_list.by_title(result_set[0])
        if (music == None):
            await find_song.finish("未找到此歌曲\n可能是已经寄了")
        await find_song.finish(Message([
            MessageSegment(type='text', data={
                "data": {"text": "您要找的是不是"}})
        ] + song_txt(music)))
    else:
        s = '\n'.join(result_set)
        await find_song.finish(f"您要找的可能是以下歌曲中的其中一首：\n{ s }")

find_aliases = on_regex(r".+有什么别名")


@find_aliases.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    regex = "(.+)有什么别名"
    name = re.match(regex, str(event.get_message())
                    ).groups()[0].strip().lower()
    s = f'{name}的别名有：\n'
    if name in music_aliases:
        result_set1 = music_aliases[name]
        if len(result_set1) == 1:
            music = total_list.by_title(result_set1[0])
            if (music == None):
                await find_song.finish('''
未找到此歌曲，可能是已经寄了（确认没有删除的话可通过添加别名指令自行添加）
添加别名 <歌曲id> <别名>
例：添加别名 114514 下北泽
                ''')
            name = music.title.lower()
        else:
            await find_song.finish(f"这个别名有很多歌,请用id查询\n或者你也可以试试：\n {name}是什么歌")
    elif name not in anti_aliases:
        await find_aliases.finish('''
未找到此歌曲，可能是已经寄了（确认没有删除的话可通过添加别名指令自行添加）
添加别名 <歌曲id> <别名>
例：添加别名 114514 下北泽
                ''')
    result_set = anti_aliases[name]
    s = s + ' / '.join(result_set)
    await find_aliases.finish(s)


adds = on_command('添加别名')
# white_list2 = ['702611663']


@adds.handle()
async def _(bot: Bot, event: Event, state: T_State, args: Message = CommandArg()):
    req = args.extract_plain_text().strip().split(" ")
    # req = state
    dest_song = total_list.by_id(req[0])
    tmp2 = ''
    if (len(req) == 2):
        f = open('src/static/aliases.csv', 'r', encoding='utf-8')
        tmp = f.readlines()
        for t in tmp:
            arr = t.strip().split('\t')
            if arr[0] == dest_song.title:
                t = t.replace('\n', '')
                t = t + "\t" + req[1] + '\n'
                print(t)
            tmp2 = tmp2 + t
        f.close()
        with open('src/static/aliases.csv', 'w', encoding='utf-8') as q:
            q.writelines(tmp2)
            q.close()
        music_aliases, anti_aliases = get_aliases()
        await adds.finish("收到(´-ω-`)别名添加成功")
    await adds.finish("命令错误捏\n例 添加别名 114514 田所浩二")


ds_dict = {
    "15": "14-15",
    "14+": "14-15",
    "14": "14-15",
    "13+": "13+",
    "13": "13",
    "12+": "12+",
    "12": "12",
    "11+": "11+",
    "11": "11",
    "10+": "10+",
    "10": "10",
    "9+": "9+",
    "9": "9",
    "8+": "8+",
    "8": "8",
}
# xx定数表
ds_list = on_regex(r".+定数表")


@ds_list.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    list_dir = 'src/static/mai/ds_list/'
    regex = "(.+)定数表"
    ds = re.match(regex, str(event.get_message())
                  ).groups()[0].strip().lower()
    if ds not in ds_dict:
        await ds_list.finish('暂时只支持8-15的定数表查询捏')
    else:
        file_name = ds_dict[ds]
        img = Image.open(list_dir+f'{file_name}.png')
        await ds_list.finish([
            MessageSegment(type='image', data={
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            })
        ])

# xx完成表
com_list = on_regex(r".+完成表", priority=5)


@com_list.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    qq = str(event.get_user_id())
    regex = "(.+)完成表"
    ds = re.match(regex, str(event.get_message())
                  ).groups()[0].strip().lower()
    if ds not in ds_dict:
        await com_list.finish('暂时只支持8-15的完成表查询捏')
    else:
        com_img, success = await draw_com_list(ds, qq)
        if success == 400:
            await com_list.finish("未找到此玩家，请确保此玩家的qq号和查分器中的qq号相同。")
        elif success == 403:
            await com_list.finish("该用户禁止了其他人获取数据。")
        elif success == 1:
            await com_list.send('生成中，请稍等')
            await com_list.finish([
                MessageSegment(type='image', data={
                    "file": f"base64://{str(image_to_base64(com_img), encoding='utf-8')}"
                })
            ], at_sender=True)

# 登录查分器
# 现在不再需要登录了
# login = on_regex(r"查分器登录 .+ *\d?", rule=to_me())


# @login.handle()
# async def _(bot: Bot, event: Event, state: T_State = State()):
#     # if event.message_type != "private":
#     #     await login.finish("只允许私聊登录哦")
#     # else:
#     qq = str(event.get_user_id())
#     regex = "^查分器登录 (.+) *(\d)?$"
#     res = re.match(regex, str(event.get_message())).groups()
#     list = res[0].split(' ')
#     if len(list) == 2:
#         account = list[0]
#         password = list[1]
#         success = await login_prober(qq, account, password)
#         if success == -3:
#             await login.finish("用户名或密码错误")
#         else:
#             await login.finish("登陆成功，用户数据已记录")
#     else:
#         await login.finish("登录格式错误，请重新输入")

# XX分数列表
score_list = on_regex(r".+分数列表")


@score_list.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    qq = str(event.get_user_id())
    regex = "(.+)分数列表(.+)?"
    groups = re.match(regex, str(event.get_message())
                      ).groups()
    ds = groups[0].strip().lower()
    cur_page = 1
    if groups[1] != '' and groups[1] != None:
        cur_page = groups[1].strip().lower()
        if not str.isdigit(cur_page):
            await ds_list.finish('请输入正确的数字页码')
        else:
            cur_page = int(groups[1])
    if ds not in ds_dict:
        await ds_list.finish('暂时只支持8-15的分数列表查询捏')
    else:
        com_img, success = await draw_score_list(ds, qq, cur_page)
        if success == 400:
            await score_list.finish("未找到此玩家，请确保此玩家的qq号和查分器中的qq号相同。")
        elif success == 403:
            await score_list.finish("该用户禁止了其他人获取数据。")
        elif success == 1:
            await score_list.send('生成中，请稍等')
            await score_list.finish([
                MessageSegment(type='image', data={
                    "file": f"base64://{str(image_to_base64(com_img), encoding='utf-8')}"
                })
            ], at_sender=True)
        elif success == 233:
            await score_list.finish([
                MessageSegment(type='text', data={
                    "text": "超过最大页码限制，默认显示第一页"
                }),
                MessageSegment(type='image', data={
                    "file": f"base64://{str(image_to_base64(com_img), encoding='utf-8')}"
                })
            ], at_sender=True)
        elif success == -1:
            await score_list.finish('你在该难度没有游玩记录捏', at_sender=True)


# xx牌子完成表
plate_com_list = on_regex(
    r"([真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉舞熊華华爽煌霸])([极将者神舞]{1,2})完成表", priority=1)


@ plate_com_list.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    regex = '([真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉舞熊華华爽煌霸])([极将者神舞]{1,2})'
    match = re.match(regex, str(event.get_message())).groups()
    prefix = match[0]
    prefix = '舞' if match[0] == '霸' else prefix
    suffix = match[1]
    if len(suffix) == 2:
        if suffix != '舞舞':
            await plate_com_list.finish('暂时没有这种牌子捏')
    full_name = f'{prefix}{suffix}'
    if full_name in ['真将']:
        await plate_com_list.finish('暂时没有这种牌子捏')
    if prefix in ['霸']:
        await plate_com_list.finish('跑霸者你是想累死我吗.jpg')
    music_list, success = await get_plate_ach(match, prefix, str(event.get_user_id()))
    if success == 400:
        await plate_com_list.finish("未找到此玩家，请确保此玩家的qq号和查分器中的qq号相同。")
    elif success == 403:
        await plate_com_list.finish("该用户禁止了其他人获取数据。")
    elif success == 1:
        await plate_com_list.send('生成中，请稍等')
        img = await draw_plate_img(match, music_list)
        await ds_list.finish([
            MessageSegment(type='image', data={
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            })
        ], at_sender=True)

# xx牌子进度
plate_progress_list = on_regex(
    r"([真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉舞熊華华爽煌霸])([极将者神舞]{1,2})进度", priority=1)


@ plate_progress_list.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    regex = '([真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉舞熊華华爽煌霸])([极将者神舞]{1,2})进度'
    match = re.match(regex, str(event.get_message())).groups()
    prefix = match[0]
    prefix = '舞' if match[0] == '霸' else prefix
    suffix = match[1]
    if len(suffix) == 2:
        if suffix != '舞舞':
            await plate_progress_list.finish('暂时没有这种牌子捏')
    full_name = f'{prefix}{suffix}'
    if full_name in ['真将', '霸者', '霸极', '霸将', '霸神']:
        await plate_progress_list.finish('暂时没有这种牌子捏')
    music_list, success = await get_plate_ach(match, prefix, str(event.get_user_id()))
    if success == 400:
        await plate_progress_list.finish("未找到此玩家，请确保此玩家的qq号和查分器中的qq号相同。")
    elif success == 403:
        await plate_progress_list.finish("该用户禁止了其他人获取数据。")
    elif success == 1:
        await plate_progress_list.send('生成中，请稍等')
        message = await create_plate_text(match, music_list)
        await plate_progress_list.finish(message, at_sender=True)


# 单曲成绩
def init_score(music):
    single_records = []
    for index in range(len(music.ds)):
        ds = music.ds[index]
        single_records.append({'achievements': 0, 'fc': '', 'fs': '', 'id': music.id,
                              'level': music.level[index], 'level_index': index, 'title': music.title, 'type': music.type, "ds": ds})
    return single_records


single_score = on_regex(r"info(.+)")


@single_score.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    qq = str(event.get_user_id())
    regex = 'info(.+)'
    res = re.match(regex, str(event.get_message())).groups()
    aliases = res[0].strip()
    # 判断给定参数是id还是别称
    if str.isdigit(aliases):
        music = total_list.by_id(aliases)
        if music == None:
            await single_score.finish('未找到此id对应的歌曲')
        else:
            await single_score.send('生成中，请稍等')
            # 若找到歌则取对应版本歌曲记录
            records, success = await get_user_plate_records(qq, [music.version])
            if success == 400:
                await single_score.finish("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
            elif success == 403:
                await single_score.finish("该用户禁止了其他人获取数据。")
            # 初始化记录列表
            single_records = init_score(music)
            # 寻找记录中是否有该曲记录，有则覆盖记录列表
            for song in records:
                if song['id'] == int(music.id):
                    for item in single_records:
                        if item['level_index'] == song['level_index']:
                            item['achievements'] = song['achievements']
                            item['fc'] = song['fc']
                            item['fs'] = song['fs']
            img, success = await draw_single_record(music.id, single_records)
            if success == 1:
                await single_score.finish([
                    MessageSegment(type='image', data={
                        "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"})], at_sender=True)
            else:
                await single_score.finish('发生未知错误，请联系bot管理员')
    else:
        if aliases not in music_aliases:
            await single_score.finish('未找到此别名对应的歌曲，可以更换成id进行尝试')
        else:
            # 读取别名对应的歌曲
            await single_score.send('生成中，请稍等')
            result_set = music_aliases[aliases]
            if len(result_set) == 1:
                # 若对应唯一
                music = total_list.by_title(result_set[0])
                # 若找到歌则取对应版本歌曲记录
                records, success = await get_user_plate_records(qq, [music.version])
                if success == 400:
                    await single_score.finish("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
                elif success == 403:
                    await single_score.finish("该用户禁止了其他人获取数据。")
                # 初始化记录列表
                single_records = init_score(music)
                # 寻找记录中是否有该曲记录，有则覆盖记录列表
                for song in records:
                    if song['id'] == int(music.id):
                        for item in single_records:
                            if item['level_index'] == song['level_index']:
                                item['achievements'] = song['achievements']
                                item['fc'] = song['fc']
                                item['fs'] = song['fs']
                img, success = await draw_single_record(music.id, single_records)
                if success == 1:
                    await single_score.finish([
                        MessageSegment(type='image', data={
                            "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"}),
                    ], at_sender=True)
                else:
                    await single_score.finish('发生未知错误，请联系bot管理员')
            else:
                s = '\n'.join(result_set)
                await find_song.finish(f"您要找的可能是以下歌曲中的其中一首：\n{ s },可以通过对应id进行查询")


# 机厅人数记录
def get_play_field_field_data():
    with open('src/static/mai/play_field_record.json', 'r', encoding='utf-8') as file:
        name_list = []
        try:
            raw_data = json.load(file)
            field_data = raw_data['record']
            file.close()
            if len(field_data) != 0:
                for item in field_data:
                    name_list.append(item['name'])
        except:
            print('机厅人数模块错误')
        finally:
            return name_list, raw_data, field_data


# 查询机厅人数/记录机厅人数
play_field_record = on_regex(rf"^瓜瓜 (\D+)([几|\d]+)",  priority=5)


@play_field_record.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    name_list, raw_data, field_data = get_play_field_field_data()
    qq = str(event.get_user_id())
    regex = f"^瓜瓜 (\D+)([几|\d]+)"
    res = re.match(regex, str(event.get_message()).strip()).groups()
    print(res)
    name = res[0].strip()
    arg = res[1].strip()
    if name not in name_list:
        await play_field_record.finish('暂时没有这个机厅捏，可以通过添加机厅指令自行添加。')
    if str.isdigit(arg):
        if int(arg) > 20:
            await play_field_record.finish(f'你找{arg}人来{name}我看看')
        tm = time.time()
        for record in field_data:
            if record['name'] == name:
                record['cur_people'] = arg
                record['record_time'] = tm
                record['recorder'] = qq
                break
        try:
            with open('src/static/mai/play_field_record.json', 'w', encoding='utf-8') as file:
                file.write(json.dumps(raw_data))
                file.close()
        except:
            await play_field_record.finish('发生未知错误，请联系bot管理员')
        await play_field_record.finish(f'收到,现在{name}有{arg}人')

    elif arg == '几':
        hrx = datetime.datetime.now().hour
        miny = datetime.datetime.now().minute
        if hrx < 10:
            await play_field_record.finish(
                f'才他妈{hrx}点{miny}，你要堵门？')
        temp = None
        for record in field_data:
            if record['name'] == name:
                temp = record
        name = temp['name']
        cur_people = temp['cur_people']
        recorder = temp['recorder']
        record_time = float(temp['record_time'])
        hour = int((time.time()-record_time)/3600)
        minute = int((time.time() - record_time) / 60 - 60 * hour)
        second = int(time.time() - record_time - 3600 * hour - 60 * minute)
        await play_field_record.finish(
            f'{name}现在有 {cur_people} 人\n由用户 {recorder} 最后更新于：\n{hour}小时{minute}分钟{second}秒前')


add_play_field = on_regex(rf"^添加机厅.+",  priority=4)


@add_play_field.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    name_list, raw_data, field_data = get_play_field_field_data()
    qq = str(event.get_user_id())
    regex = f"^添加机厅(.+)"
    res = re.match(regex, str(event.get_message()).strip()).groups()
    name = res[0].strip()
    for char in name:
        if str.isdigit(char):
            await add_play_field.finish('请勿添加不含数字机厅名哦')
        #
    for item in field_data:
        if name == item['name']:
            await add_play_field.finish('该机厅已存在，请勿重复添加')
    field_data.append({
        "name": name,
        "cur_people": 0,
        "record_time": time.time(),
        "recorder": qq
    })
    with open('src/static/mai/play_field_record.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(raw_data))
        file.close()
        name_list = get_play_field_field_data()
    await add_play_field.finish('机厅已经添加')


query_play_field = on_command('机厅列表')


@query_play_field.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    name_list, raw_data, field_data = get_play_field_field_data()
    text = '现有机厅：\n'
    for item in field_data:
        name = item['name']
        text += f'{name}\n'
    await query_play_field.finish(text)


delete_play_field = on_regex(r'删除机厅.+')


@delete_play_field.handle()
async def _(bot: Bot, event: Event, state: T_State = State()):
    name_list, raw_data, field_data = get_play_field_field_data()
    regex = '删除机厅(.+)'
    res = re.match(regex, str(event.get_message()).strip()).groups()
    name = res[0].strip()
    if name not in name_list:
        await delete_play_field.finish('暂时没有这个机厅捏，可以通过添加机厅指令自行添加。')
    try:
        with open('src/static/mai/play_field_record.json', 'w', encoding='utf-8') as file:
            field_data = raw_data['record']
            for i in range(len(field_data)):
                item = field_data[i]
                print(item['name'])
                if item['name'] == name:
                    del field_data[i]
            file.write(json.dumps(raw_data))
            file.close()
    except Exception as e:
        traceback.print_exc()
        print('机厅人数模块错误')
    await query_play_field.finish('已删除')
