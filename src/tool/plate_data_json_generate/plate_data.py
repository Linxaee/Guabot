# from src.libraries.maimaidx_music import *
# from src.libraries.tool import *
# from src.libraries.image import *
# from xml.etree import ElementTree as ET
# # 获取舞系全曲id


# def get_all_music():
#     # ET去打开xml文件
#     tree = ET.parse("MusicGroup.xml")
#     # 获取根标签
#     root = tree.getroot()
#     all_list = []
#     for child in root.iter('id'):
#         all_list.append(int(child.text))
#     return all_list
# # 获取舞系reid


# def get_rem_music():
#     # ET去打开xml文件
#     tree = ET.parse("MusicGroup(1).xml")
#     # 获取根标签
#     root = tree.getroot()
#     rem_list = []
#     for child in root.iter('id'):
#         rem_list.append(int(child.text))
#     return rem_list


# plate_to_version = {
#     '初': 'maimai',
#     '真': 'maimai PLUS',
#     '超': 'maimai GreeN',
#     '檄': 'maimai GreeN PLUS',
#     '橙': 'maimai ORANGE',
#     '暁': 'maimai ORANGE PLUS',
#     '晓': 'maimai ORANGE PLUS',
#     '桃': 'maimai PiNK',
#     '櫻': 'maimai PiNK PLUS',
#     '樱': 'maimai PiNK PLUS',
#     '紫': 'maimai MURASAKi',
#     '菫': 'maimai MURASAKi PLUS',
#     '堇': 'maimai MURASAKi PLUS',
#     '白': 'maimai MiLK',
#     '雪': 'MiLK PLUS',
#     '輝': 'maimai FiNALE',
#     '辉': 'maimai FiNALE',
#     '熊': 'maimai でらっくす',
#     # '華': 'maimai でらっくす',
#     # '华': 'maimai でらっくす',
#     '華': 'maimai でらっくす PLUS',
#     '华': 'maimai でらっくす PLUS',
#     '爽': 'maimai でらっくす Splash',
#     '煌': 'maimai でらっくす Splash',
#     # '煌': 'maimai でらっくす Splash PLUS',
# }

# plate_version = {
#     '真': ['maimai', 'maimai PLUS'],
#     '超': ['maimai GreeN'],
#     '檄': ['maimai GreeN PLUS'],
#     '橙': ['maimai ORANGE'],
#     '暁': ['maimai ORANGE PLUS'],
#     '晓': ['maimai ORANGE PLUS'],
#     '桃': ['maimai PiNK'],
#     '櫻': ['maimai PiNK PLUS'],
#     '樱': ['maimai PiNK PLUS'],
#     '紫': ['maimai MURASAKi'],
#     '菫': ['maimai MURASAKi PLUS'],
#     '堇': ['maimai MURASAKi PLUS'],
#     '白': ['maimai MiLK'],
#     '雪': ['MiLK PLUS'],
#     '輝': ['maimai FiNALE'],
#     '辉': ['maimai FiNALE'],
#     '舞': ['maimai', 'maimai PLUS', 'maimai GreeN', 'maimai GreeN PLUS',
#           'maimai ORANGE', 'maimai ORANGE PLUS', 'maimai PiNK', 'maimai PiNK PLUS',
#           'maimai MURASAKi', 'maimai MURASAKi PLUS', 'maimai MiLK', 'MiLK PLUS', 'maimai FiNALE'],
#     '熊': ['maimai でらっくす'],
#     '華': ['maimai でらっくす'],
#     '华': ['maimai でらっくす'],
#     # '華': 'maimai でらっくす PLUS',
#     # '华': 'maimai でらっくす PLUS',
#     '爽': ['maimai でらっくす Splash'],
#     '煌': ['maimai でらっくす Splash'],
#     # '煌': 'maimai でらっくす Splash PLUS',
# }

# plate_pic_index = {
#     '真': ['006101', '006102', '006103'],
#     '超': ['006104', '006105', '006106', '006107'],
#     '檄': ['006108', '006109', '006110', '006111'],
#     '橙': ['006112', '006113', '006114', '006115'],
#     '暁': ['006116', '006117', '006118', '006119'],
#     '晓': ['006116', '006117', '006118', '006119'],
#     '桃': ['006120', '006121', '006122', '006123'],
#     '櫻': ['006124', '006125', '006126', '006127'],
#     '樱': ['006124', '006125', '006126', '006127'],
#     '紫': ['006128', '006129', '006130', '006131'],
#     '菫': ['006132', '006133', '006134', '006135'],
#     '堇': ['006132', '006133', '006134', '006135'],
#     '白': ['006136', '006137', '006138', '006139'],
#     '雪': ['006140', '006141', '006142', '006143'],
#     '輝': ['006144', '006145', '006146', '006147'],
#     '辉': ['006144', '006145', '006146', '006147'],
#     '舞': ['006149', '006150', '006151', '006152', '006148'],
#     '熊': ['055101', '055102', '055103', '055104'],
#     '華': ['109101', '109102', '109103', '109104'],
#     '华': ['109101', '109102', '109103', '109104'],
#     # '華': 'maimai でらっくす PLUS',
#     # '华': 'maimai でらっくす PLUS',
#     '爽': ['159101', '159102', '159103', '159104'],
#     '煌': ['209101', '209102', '209103', '209104'],
#     # '煌': 'maimai でらっくす Splash PLUS',
# }

# plate_index = {
#     '者': 4,
#     '极': 0,
#     '将': 1,
#     '神': 2,
#     '舞舞': 3
# }


# def save_plate_dict():
#     all_list = get_all_music()
#     rem_list = get_rem_music()
#     plate_dict = {}
#     ban_id = [70, 341, 451, 455, 460, 853, 792]
#     for key in plate_version:
#         # 选出当前牌子版本列表
#         version_list = plate_version[key]
#         # print(version_list)
#         plate_dict[key] = {}
#         music_list = []
#         total_num = 0
#         re_num = 0
#         for version in version_list:
#             # 当前版本所有的歌
#             music_list_temp = total_list.filter(version=version)
#             if key == '舞':
#                 for i in range(len(music_list_temp)):
#                     music = music_list_temp[i]
#                     if int(music['id']) in all_list:
#                         total_num = total_num + 1
#                     for ds_index in range(len(music['ds'])):
#                         ds = music['ds'][ds_index]
#                         if (ds_index == 4 and int(music['id']) not in rem_list) or int(music['id']) not in all_list:
#                             continue
#                         else:
#                             music_list.append({"song_id": music['id'], "title": music['title'], "ds": music['ds'][ds_index], "level_index": ds_index, 'level': music['level'][ds_index],
#                                                "achievements": 0, "fc": '', "fs": ''})

#             else:
#                 for i in range(len(music_list_temp)):
#                     music = music_list_temp[i]
#                     if int(music['id']) in ban_id:
#                         continue
#                     else:
#                         total_num = total_num + 1
#                     for ds_index in range(len(music['ds'])):
#                         ds = music['ds'][ds_index]
#                         if ds_index == 4:
#                             continue
#                         else:
#                             music_list.append({"song_id": music['id'], "title": music['title'], "ds": music['ds'][ds_index], "level_index": ds_index, 'level': music['level'][ds_index],
#                                                "achievements": 0, "fc": '', "fs": ''})

#             # print(f'{version}:'+str(i))
#         plate_dict[key]['music_list'] = music_list
#         plate_dict[key]['num'] = len(music_list)
#         plate_dict[key]['total_num'] = total_num
#         # plate_dict[key]['re_num'] = re_num
#     with open('src/static/mai/plate/plate_dict.json', 'w') as f:
#         json.dump(plate_dict, f)
#         f.close()

# if __name__ == '__main__':
#     save_plate_dict()
