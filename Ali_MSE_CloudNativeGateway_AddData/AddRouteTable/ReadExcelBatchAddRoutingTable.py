# -*- coding: utf-8 -*-
import argparse
import time
import xlrd2
import subprocess


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def main(parm):
        print('----------------------------')
        print('Parameter List: ', parm)
        print('----------------------------')

        workbook = xlrd2.open_workbook(filename=parm.excel_file)
        # 获取工作薄中所有的sheet名称
        sheet_names = workbook.sheet_names()
        print('sheet_names: {}'.format(sheet_names))
        # 获取第一个sheet表格
        table = workbook.sheets()[0]
        # 获取sheet中有效行数
        row = table.nrows
        print('获取第一个sheet中有效行数: ' + str(row))
        # 获取sheet中有效列数
        col = table.ncols
        print('获取第一个sheet中有效列数: ' + str(col))

        # 循环获取每行的数据
        for row in range(row):
            if row != 0:
                # init excel field parm
                print('正在处理第{}行: '.format(row))
                NameSpace = table.cell_value(row, 0)
                DomainName = table.cell_value(row, 1)
                RouteName = table.cell_value(row, 2)
                RoutePath = table.cell_value(row, 3)
                RouteType = table.cell_value(row, 4)
                ServiceName = table.cell_value(row, 5)
                AgreementType = table.cell_value(row, 6)
                ServicePort = str(int(float(table.cell_value(row, 7))))
                HeaderKey = table.cell_value(row, 8)
                HeaderValue = table.cell_value(row, 9)
                HeaderType = table.cell_value(row, 10)
                Rewrite_pathType = table.cell_value(row, 11)
                Rewrite_path = table.cell_value(row, 12)
                print('gateway_unique_id: {}; NameSpace: {}; DomainName: {}; RouteName: {}; RoutePath: {}; RouteType: {}; ServiceName: {}; AgreementType: {}; ServicePort: {}; HeaderKey: {}; '
                      'HeaderValue: {}; HeaderType: {}; Rewrite_pathType: {}; Rewrite_path: {}; '.format(parm.gateway_unique_id, NameSpace, DomainName, RouteName,
                                                                                  RoutePath, RouteType, ServiceName, AgreementType, ServicePort, HeaderKey,
                                                                                      HeaderValue, HeaderType, Rewrite_pathType, Rewrite_path))

                # exec AddGatewayRouteItem.py
                try:
                    print('-------------------AddGatewayRouteItem.py-------------------')
                    Command = 'python AddGatewayRouteItem.py --gateway_unique_id="{}" --namespace="{}" --DomainName="{}" --RouteName="{}" --RoutePath="{}" --RouteType="{}" --ServiceName="{}" --AgreementType="{}" --ServicePort="{}" --HeaderKey="{}" --HeaderValue="{}" --HeaderType="{}" --Rewrite_pathType="{}" --Rewrite_path="{}"'\
                                                   .format(parm.gateway_unique_id, NameSpace, DomainName, RouteName, RoutePath, RouteType, ServiceName, AgreementType, ServicePort, HeaderKey, HeaderValue, HeaderType, Rewrite_pathType, Rewrite_path)
                    print(Command)
                    p = subprocess.Popen(Command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf8")
                    print(p.stdout.read())

                except Exception as error:
                    print(error)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--access_key_id', type=str, default='')
    parser.add_argument('--access_key_secret', type=str, default='')

    ### bees-dev
    parser.add_argument('--gateway_unique_id', type=str, default='gw-')
    ### bees-uat
    #parser.add_argument('--gateway_unique_id', type=str, default='gw-')
    ### bees-prod
    #parser.add_argument('--gateway_unique_id', type=str, default='gw-')

    parser.add_argument('--excel_file', type=str, default="./temp/RouteConfigList-temp.xlsx")
    parm = parser.parse_args()
    Sample.main(parm)
