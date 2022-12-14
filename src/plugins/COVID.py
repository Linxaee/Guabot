import re
from nonebot import on_command, on_regex
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, Event, Bot, MessageSegment
from src.libraries.image import *
from src.libraries.COVID_draw import generate, DrawPicByQueryCity
from src.libraries.COVID_data import cityList, get_data

query_by_name = on_regex(r"^疫情动态 .+$")


@query_by_name.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "疫情动态 (.+)"
    res = re.match(regex, str(event.get_message())).groups()
    img, success = await generate(res[0])
    if success == 0:
        await query_by_name.finish(Message([
            MessageSegment(type='image', data={
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"}),
        ]))
    elif success == 233:
        await query_by_name.finish(Message([
            MessageSegment(type='text', data={
                "text": "暂未查询到该地区信息！"}),
        ]))
    else:
        await query_by_name.finish(Message([
            MessageSegment(type='text', data={
                "text": "发生未知错误，请联系Bot管理员！"}),
        ]))

query_risk_area = on_regex(r'^风险区 .+ *\d?$')


@query_risk_area.handle()
async def _(bot: Bot, event: Event, state: T_State):
    city_data, internal_data = get_data()
    regex = "^风险区 (.+) *(\d)?$"
    res = re.match(regex, str(event.get_message())).groups()
    name = ''
    subName = ''
    curPage = 1
    temp = res[0].split(' ')
    for item in temp:
        if item.isdigit():
            print(item)
            curPage = int(item)
            temp.pop()
            break
    if len(temp) == 1:
        name = temp[0]
    elif len(temp) == 2:
        name = temp[0]
        subName = temp[1]
    if name in ['北京', '天津', '上海', '重庆']:
        city = city_data.by_prov_name(name)
        # subCity = city['subCity']
        # dangerousAreas = {}
        # subList = []
        # for item in subCity:
        #     dangerousAreas = item['dangerousAreas']
        #     for item in dangerousAreas['subList']:
        #         if item['level'] == '高风险':
        #             subList.append(item)
        # for item in subCity:
        #     for item in dangerousAreas['subList']:
        #         if item['level'] == '中风险':
        #             subList.append(item)
        # # 排序不知道咋比较level用不了，他妈的气死我了
        # # dangerousAreas['subList'] = sorted(subList, key=cmp_to_key(comp))
        # dangerousAreas['subList'] = subList
        # city['dangerousAreas'] = dangerousAreas
        city['city_name'] = city['prov_name']
    else:
        city = city_data.by_subCity_name(name)
        if city == 0:
            await query_risk_area.finish(Message([
                MessageSegment(type='text', data={
                    "text": "暂未查询到指定城市信息。"}),
            ]))
    img, success = await DrawPicByQueryCity(city, subName, curPage)
    if success == 0:
        await query_risk_area.finish(Message([
            MessageSegment(type='image', data={
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"}),
        ]))
    elif success == 233:
        await query_risk_area.finish(Message([
            MessageSegment(type='text', data={
                "text": "超过最大页码限制，默认显示第一页"}),
            MessageSegment(type='image', data={
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"}),

        ]))
    elif success == 555:
        await query_risk_area.finish(Message([
            MessageSegment(type='text', data={
                "text": "接口异常，请三分钟后再试。\n这个接口经常出问题，用不了就算了（恼"}),
        ]))
    elif success == 666:
        await query_risk_area.finish(Message([
            MessageSegment(type='text', data={
                "text": "未查询到该地区风险区域，应该是低风险区域捏。"})

        ]))
    else:
        await query_risk_area.finish(Message([
            MessageSegment(type='text', data={
                "text": "发生未知错误，请联系Bot管理员！"}),
        ]))
