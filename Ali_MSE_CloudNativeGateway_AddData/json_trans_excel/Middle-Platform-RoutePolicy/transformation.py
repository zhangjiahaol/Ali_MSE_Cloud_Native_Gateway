# -*- coding: utf-8 -*-

# json转excel，执行后直接复制粘贴到excel

import json
env = "prod"
path = "./middle-platform-RoutePolicy-" + env + ".json"

f = open(path, encoding="utf-8")
content = f.read()

data = json.loads(content)
for json in data:
    #print(json)
    RouteName = env + '-' + str(json['path']).replace('abi-cloud-', '').replace('/**', '').replace('/', '') + '-jwt'
    path = str(json['path']).replace('/**', '')
    ServiceName = str(json['uri']).replace('http://', '').replace(':8080', '')

    if 'stripPrefix' in json:
        print(RouteName + str("\t") + path + str("\t") + ServiceName + str("\t") + 'PRE' + str("\t") + str(json['stripPrefix']).replace('1','/'))
    else:
        print(RouteName + str("\t") + path + str("\t") + ServiceName)

    if len(RouteName) > 60:
        print('路由名称不能大于60个字符: ' + str(len(RouteName)))
