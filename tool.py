# import os
# root_path = os.path.split(os.path.realpath(__file__))[0]


# class BatchRename():

#     def rename(self):
#         path = "src/static/mai/cover"
#         filelist = os.listdir(path)
#         total_num = len(filelist)
#         # i = 0
#         for item in filelist:
#             if item.endswith('.jpeg'):
#                 src = os.path.join(os.path.abspath(path), item)
#                 dst = os.path.join(os.path.abspath(path), item[:-6] + '.jpeg')
#                 try:
#                     os.rename(src, dst)

#                 except:
#                     continue
#         # print('total %d to rename & converted %d png' % (total_num, i))


# if __name__ == '__main__':
#     # demo = BatchRename()
#     # demo.rename()

# from src.libraries.COVID_data import get_level_data

# if __name__ == '__main__':
#     get_level_data()