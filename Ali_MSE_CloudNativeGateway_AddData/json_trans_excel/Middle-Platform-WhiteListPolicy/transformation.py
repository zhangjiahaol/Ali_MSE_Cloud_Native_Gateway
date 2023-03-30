# -*- coding: utf-8 -*-

# json转excel，执行后直接复制粘贴到excel

import json

path = "./middle-platform-WhiteListPolicy-prod.json"

f = open(path, encoding="utf-8")
content = f.read()

path_list = []

#读取json文件格式化后放到list列表里面path_list
data = json.loads(content)
for json in data:
    path = str(json).replace("GET#", "").replace("POST#", "").replace("PUT#", "").replace("**", ".*").replace("//", "/")
    path_list.append(path)


#去重
remove_duplication_list = list(set(path_list))
for item in remove_duplication_list:
    print(item)