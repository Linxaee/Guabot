# from collections import defaultdict
# import csv
# import pandas as pd
# import numpy as np
# from src.libraries.maimaidx_music import Music, get_cover_len4_id, total_list, rc_music,  get_ds_by_ra_ach

# def quchong(arr):
#     s = []
#     for i in arr:
#         if i not in s:
#             s.append(i)
#     return s

# csv_file = pd.read_csv('total_music.csv', encoding='utf-8', na_filter=False)
# alt = np.array(csv_file)
# temp_list = alt.tolist()
# # 去除''
# for i in range(len(temp_list)):
#     music = temp_list[i]
#     for i in range(len(music)):
#         str = music[i]
#         if str == '':
#             del music[i:len(music)]
#             break

# # 添加现有别名
# for i in range(len(temp_list)):
#     music = temp_list[i]
#     name = music[1]
#     result_set = anti_aliases[name]
#     for item in result_set:
#         music.append(item)
#     music = quchong(music)
#     # print(music)
#     res_set.append(music)
# # 去除重名
# # for i in range(len(temp_list)):
# #     music = temp_list[i]
# #     music = quchong(music)

# # a = np.asarray(res_set)

# # print(temp_list)
# # alt = np.array(df)
# # 转存excel文件，index参数为False，不将index列存到excel文件里
# # 写入歌曲总表
# with open('total_music.csv', 'w', newline='', encoding='utf-8') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(['id', 'name'])
#     for music_row in res_set:
#         writer.writerow(music_row)


# # csv转excel
# df = pd.read_csv('total_music.csv', encoding='utf-8')
# df.to_excel("total_music.xlsx", index=False)
# # excel转csv
# ex = pd.read_excel('total_music.xlsx')
# ex.to_csv("total_music.csv", index=False, header=True)
