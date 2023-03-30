# -*- coding: utf-8 -*-

# json转excel，执行后直接复制粘贴到excel

import json

file = open("./all.txt")

path_list = []

for line in file:
    path_list.append(line)


#去重
remove_duplication_list = list(set(path_list))
for item in remove_duplication_list:
    print(item)