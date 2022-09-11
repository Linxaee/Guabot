import json
import numpy as np
import random
from typing import Dict, List, Optional, Union, Tuple, Any
from copy import deepcopy
from src.libraries.tool import computeRa, print_to_json

import requests


def get_cover_len4_id(mid) -> str:
    mid = int(mid)
    if 10001 <= mid:
        mid -= 10000
    return f'{mid:04d}'


def cross(checker: List[Any], elem: Optional[Union[Any, List[Any]]], diff):
    ret = False
    diff_ret = []
    if not elem or elem is Ellipsis:
        return True, diff
    if isinstance(elem, List):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if __e in elem:
                diff_ret.append(_j)
                ret = True
    elif isinstance(elem, Tuple):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem[0] <= __e <= elem[1]:
                diff_ret.append(_j)
                ret = True
    else:
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem == __e:
                return True, [_j]
    return ret, diff_ret


def in_or_equal(checker: Any, elem: Optional[Union[Any, List[Any]]]):
    if elem is Ellipsis:
        return True
    if isinstance(elem, List):
        return checker in elem
    elif isinstance(elem, Tuple):
        return elem[0] <= checker <= elem[1]
    else:
        return checker == elem


def get_ds_by_ra_ach(ra, achievement):
    ds = -1
    for i in np.arange(1.0, 15.0, 0.1):
        cur_ra = computeRa(i, achievement)
        if cur_ra - ra >= 0 and cur_ra - ra <= 2:
            ds = i
            break
    return round(ds, 1)


async def login_prober(qq, username, password):
    json_dir = 'src/static/mai/user_account_json/'
    url = 'https://www.diving-fish.com/api/maimaidxprober/login'
    payload = {'username': username, 'password': password}
    res = requests.post(url, json=payload)
    status = json.loads(res.text)
    if status['message'] != '登录成功':
        return -3
    else:
        cookie = requests.utils.dict_from_cookiejar(res.cookies)
        with open(f'{json_dir}{qq}_account.json', 'w', encoding='utf-8') as f:
            user_account = {
                "username": username,
                "password": password,
                "cookie": cookie,
            }
            f.write(json.dumps(user_account, ensure_ascii=False))
            f.close()
            return 1


async def get_user_data(qq: str):
    json_dir = 'src/static/mai/user_account_json/'
    url = 'https://www.diving-fish.com/api/maimaidxprober/player/records'
    try:
        with open(f'{json_dir}{qq}_account.json', 'r', encoding='utf-8') as f:
            user_account = json.loads(f.read())
            f.close()
    except FileNotFoundError:
        return None, 0
    cookie = 'jwt_token='+user_account['cookie']['jwt_token']
    headers = {"Cookie": cookie}
    res = requests.get(url, headers=headers)
    records = json.loads(res.text)['records']
    return records, 1


class Chart(Dict):
    tap: Optional[int] = None
    slide: Optional[int] = None
    hold: Optional[int] = None
    touch: Optional[int] = None
    brk: Optional[int] = None
    charter: Optional[int] = None

    def __getattribute__(self, item):
        if item == 'tap':
            return self['notes'][0]
        elif item == 'hold':
            return self['notes'][1]
        elif item == 'slide':
            return self['notes'][2]
        elif item == 'touch':
            return self['notes'][3] if len(self['notes']) == 5 else 0
        elif item == 'brk':
            return self['notes'][-1]
        elif item == 'charter':
            return self['charter']
        return super().__getattribute__(item)

# 推荐乐曲


class rc_music(Dict):
    id: Optional[str] = None
    title: Optional[str] = None
    ds: Optional[List[float]] = None
    level: Optional[List[str]] = None
    genre: Optional[str] = None
    type: Optional[str] = None
    is_new: Optional[bool] = None
    artist: Optional[str] = None
    achievement: Optional[float] = None
    diff: Optional[int] = []
    diffs_label: Optional[str] = None

    def __getattribute__(self, item):

        if item in self:
            return self[item]
        return super().__getattribute__(item)


class Music(Dict):
    id: Optional[str] = None
    title: Optional[str] = None
    ds: Optional[List[float]] = None
    level: Optional[List[str]] = None
    genre: Optional[str] = None
    type: Optional[str] = None
    bpm: Optional[float] = None
    version: Optional[str] = None
    is_new: Optional[bool] = None
    charts: Optional[List[Chart]] = None
    release_date: Optional[str] = None
    artist: Optional[str] = None

    diff: List[int] = []

    def __getattribute__(self, item):
        if item in {'genre', 'artist', 'release_date', 'bpm', 'version', 'is_new'}:
            if item == 'version':
                return self['basic_info']['from']
            return self['basic_info'][item]
        elif item in self:
            return self[item]
        return super().__getattribute__(item)


class MusicList(List[Music]):
    def by_id(self, music_id: str) -> Optional[Music]:
        for music in self:
            if music.id == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[Music]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def random(self):
        return random.choice(self)

    def filter(self,
               *,
               level: Optional[Union[str, List[str]]] = ...,
               ds: Optional[Union[float, List[float],
                                  Tuple[float, float]]] = ...,
               title_search: Optional[str] = ...,
               genre: Optional[Union[str, List[str]]] = ...,
               bpm: Optional[Union[float, List[float],
                                   Tuple[float, float]]] = ...,
               type: Optional[Union[str, List[str]]] = ...,
               diff: List[int] = ...,
               ):
        new_list = MusicList()
        for music in self:
            diff2 = diff
            music = deepcopy(music)
            ret, diff2 = cross(music.level, level, diff2)
            if not ret:
                continue
            ret, diff2 = cross(music.ds, ds, diff2)
            if not ret:
                continue
            if not in_or_equal(music.genre, genre):
                continue
            if not in_or_equal(music.type, type):
                continue
            if not in_or_equal(music.bpm, bpm):
                continue
            if title_search is not Ellipsis and title_search.lower() not in music.title.lower():
                continue
            music.diff = diff2
            new_list.append(music)
        return new_list


obj = requests.get(
    'https://www.diving-fish.com/api/maimaidxprober/music_data').json()
total_list: MusicList = MusicList(obj)
for i in range(len(total_list)):
    total_list[i] = Music(total_list[i])
    for j in range(len(total_list[i].charts)):
        total_list[i].charts[j] = Chart(total_list[i].charts[j])
