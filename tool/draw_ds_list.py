# from asyncio.windows_events import NULL
# from importlib.metadata import version
# import math

# import requests
# from PIL import Image, ImageDraw, ImageFont, ImageFilter
# from src.libraries.maimaidx_music import Music, get_cover_len4_id, total_list, rc_music,  get_ds_by_ra_ach
# from src.libraries.tool import *
# from src.libraries.image import *


# # 绘制定数表
# ds_dict = {
#     "15": [14.0, 15.0],
#     "14+": [14.0, 15.0],
#     "14": [14.0, 15.0],
#     "13+": [13.7, 13.9],
#     "13": [13.0, 13.6],
#     "12+": [12.7, 12.9],
#     "12": [12.0, 12.6],
#     "11+": [11.7, 11.9],
#     "11": [11.0, 11.6],
#     "10+": [10.7, 10.9],
#     "10": [10.0, 10.6],
#     "9+": [9.7, 9.9],
#     "9": [9.0, 9.6],
#     "8+": [8.7, 8.9],
#     "8": [8.0, 8.6],
# }
# color_dict = {
#     "Bas": (69, 193, 36),
#     "Adv": (248, 176, 8),
#     "Exp": (255, 90, 102),
#     "Mst": (159, 81, 220),
#     "ReM": (226, 209, 240),
# }


# def inner_level_q(ds1, ds2=None):
#     result_set = []
#     diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'ReM']
#     if ds2 is not None:
#         music_data = total_list.filter(ds=(ds1, ds2))
#     else:
#         music_data = total_list.filter(ds=ds1)
#     for music in sorted(music_data, key=lambda i: int(i['id'])):
#         for i in music.diff:
#             result_set.append(
#                 {"id": music['id'], "title": music['title'], "ds": music['ds'][i], "diff_label": diff_label[i], "diff_index": i, "level": music['level'][i], "type": music['type'], "achievement": 0})
#     return result_set


# def contact_img(src_img, len):
#     pic_dir = 'src/static/mai/pic/'
#     bg_img = Image.open(
#         pic_dir + 'UI_UNL_BG.png').convert('RGBA')
#     src_w, src_h = src_img.size
#     bg_w, bg_h = bg_img.size
#     # 生成等长白布
#     temp_img = Image.new('RGB', (src_w, src_h+len), (255, 255, 255))
#     box = (0, 0, bg_w, len)
#     bg_img = bg_img.crop(box)
#     temp_img.paste(src_img, (0, 0))
#     temp_img.paste(bg_img, (0, src_h))
#     if len > bg_h:
#         diff = len-bg_h
#         temp_img.paste(bg_img, (0, src_h+diff))
#     # src_img.paste(bg_img, (0, src_h), bg_img)
#     # src_img.show()
#     return temp_img


# def draw_ds_list(ds: str):
#     ds_range = ds_dict[ds]
#     # 筛出范围内的乐曲
#     music_list = inner_level_q(ds_range[0], ds_range[1])
#     # 按定数排序
#     music_list = sorted(music_list, key=lambda i: i['ds'], reverse=True)
#     # 计算出每种定数各有多少个
#     ds_num_list = []
#     count = 0
#     cur_ds = ds_range[1]
#     for i in range(len(music_list)):
#         music = music_list[i]
#         if cur_ds == music['ds']:
#             count = count + 1
#         else:
#             ds_num_list.append(count)
#             count = 1
#             cur_ds = music['ds']
#         if i == len(music_list)-1:
#             ds_num_list.append(count)
#             count = 1
#     print(ds_num_list)
#     if ds == '15' or ds == '14' or ds == '14+':
#         ds = '14-15'
#     pic_dir = 'src/static/mai/pic/'
#     cover_dir = 'src/static/mai/cover/'
#     bg_img = Image.open(
#         pic_dir + 'UI_UNL_BG.png').convert('RGBA')
#     gua_logo = resizePic(Image.open(
#         pic_dir + 'gua_logo.png').convert('RGBA'), 0.4)
#     bg_draw = ImageDraw.Draw(bg_img)
#     adobe = 'src/static/adobe_simhei.otf'
#     mft = 'src/static/msyh.ttc'

#     bg_w, bg_h = bg_img.size
#     # print(bg_h)
#     # 板块间隔
#     block_margin = 30
#     # 单体间隔
#     item_margin = 15
#     # 每行个数
#     row_num = 10
#     # 单个封面大小
#     item_len = 75

#     title_font = ImageFont.truetype(adobe, 70, encoding='utf-8')
#     bg_draw.text((470, 80), f'{ds}定数表', 'black', title_font)
#     bg_img.paste(gua_logo, (270, -10), gua_logo)

#     auth_font = ImageFont.truetype(adobe, 22, encoding='utf-8')
#     auth = 'Generated by Guabot\nGuagua & Linxae'
#     bg_draw.text((20, 20),
#                  f'{auth}', 'black', auth_font)

#     dx_img = Image.open(
#         pic_dir + 'UI_UPE_Infoicon_DeluxeMode.png').convert('RGBA')
#     dx_img = dx_img.resize((40, 11))

#     index = 0
#     margin_top = 200
#     margin_left = 150
#     ds_font = ImageFont.truetype(adobe, 48, encoding='utf-8')
#     cur_ds = ds_range[1]
#     # 已绘制总高度
#     cur_bg_h = 200
#     for ds_num in ds_num_list:
#         cur_row_h = int(math.ceil(ds_num/10)*80+item_margin*(ds_num/10))
#         cur_bg_h = cur_bg_h+cur_row_h+block_margin
#         if cur_bg_h > bg_h:
#             # 拼接背景
#             bg_img = contact_img(bg_img, cur_bg_h-bg_h)
#             bg_draw = ImageDraw.Draw(bg_img)
#             bg_w, bg_h = bg_img.size
#         bg_draw.text((margin_left-120, margin_top+15),
#                      f'{"%.1f" % cur_ds}', 'black', ds_font)
#         for num in range(ds_num):
#             music = music_list[index]
#             i = num % row_num
#             j = num // row_num
#             id = music.get('id')
#             item = Image.open(
#                 cover_dir + f'{get_cover_len4_id(id)}.png').convert('RGBA')
#             diff = music['diff_label']
#             if diff != 'Mst':
#                 # 图片添加边框
#                 item = image_border(item, 'a', 40, color_dict[diff])
#             item = item.resize((item_len, item_len))
#             if music['type'] == 'DX':
#                 item.paste(dx_img, (35, 0), dx_img)
#             bg_img.paste(item, (margin_left+i*(item_margin+item_len),
#                                 margin_top+j*(item_margin+item_len)))
#             index = index+1
#         # 当前块行高
#         margin_top = margin_top+cur_row_h+block_margin
#         cur_ds = cur_ds - 0.1

#     bg_img.save(f'src/static/mai/ds_list/{ds}.png')
#     # bg_img.show()


# if __name__ == '__main__':
#     for k in ds_dict:
#         draw_ds_list(k)