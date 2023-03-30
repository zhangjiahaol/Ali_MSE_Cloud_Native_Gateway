# -*- coding: utf-8 -*-


import argparse
import codecs
import json
import sys

import xlrd2
import xlwt as xlwt
from alibabacloud_mse20190531.client import Client as mse20190531Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_mse20190531 import models as mse_20190531_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
            access_key_id: str,
            access_key_secret: str,
    ) -> mse20190531Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 您的 AccessKey ID,
            access_key_id=access_key_id,
            # 您的 AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # 访问的域名
        config.endpoint = f'mse.cn-shanghai.aliyuncs.com'
        return mse20190531Client(config)

    @staticmethod
    def main(parm) -> None:
        print('----------------------------')
        print('Parameter List: ', parm)
        print('----------------------------')

        ####初始化excel操作对象
        workbook = xlwt.Workbook(encoding="utf-8")
        sheet = workbook.add_sheet("Sheet1")

        # 写入标题
        for col, column in enumerate(["NameSpace", "DomainName", "RouteName", "RoutePath", "RouteType", "ServiceName", "AgreementType", "ServicePort", "HeaderKey", "HeaderValue", "HeaderType", "Rewrite_pathType", "Rewrite_path"]):
            sheet.write(0, col, column)

        ################## 初始化SDK
        print('------------Init client------------')
        client = Sample.create_client(parm.access_key_id, parm.access_key_secret)
        runtime = util_models.RuntimeOptions()
        print(runtime)
        print(runtime.to_map())

        ################## 查询所有路由表
        print('------------Get all route table------------')
        filter_params = mse_20190531_models.ListGatewayRouteRequestFilterParams(
            gateway_unique_id=parm.gateway_unique_id
        )
        list_gateway_route_request = mse_20190531_models.ListGatewayRouteRequest(
            page_size=1500,
            page_number=1,
            filter_params=filter_params,
            accept_language='zh'
        )
        try:
            rst = client.list_gateway_route_with_options(list_gateway_route_request, runtime)
            #print('json: ', json.dumps(rst.to_map()))
            print('TotalSize: ', rst.to_map().get('body').get('Data').get('TotalSize'))
            print('Code: ', rst.to_map().get('body').get('Code'))

            row = 0
            for obj in rst.to_map().get('body').get('Data').get('Result'):
                #print(json.dumps(obj))
                print(obj.get('Name'))
                row = row + 1
                print("正在写入第{}行数据".format(row))
                Id = obj.get('Id')
                NameSpace = obj.get('RouteServices')[0].get('Namespace')
                sheet.write(row, 0, NameSpace)
                DomainName = obj.get('DomainName')
                sheet.write(row, 1, DomainName)
                RouteName = obj.get('Name')
                sheet.write(row, 2, RouteName)
                RoutePath = obj.get('RoutePredicates').get('PathPredicates').get('Path')
                sheet.write(row, 3, RoutePath)
                RouteType = obj.get('RoutePredicates').get('PathPredicates').get('Type')
                sheet.write(row, 4, RouteType)
                ServiceName = obj.get('RouteServices')[0].get('Name')
                sheet.write(row, 5, ServiceName)
                AgreementType = obj.get('RouteServices')[0].get('AgreementType')
                sheet.write(row, 6, AgreementType)
                ServicePort = obj.get('RouteServices')[0].get('ServicePort')
                sheet.write(row, 7, ServicePort)
                if obj.get('RoutePredicates').get('HeaderPredicates'):
                    HeaderKey = obj.get('RoutePredicates').get('HeaderPredicates')[0].get('Key')
                    sheet.write(row, 8, HeaderKey)
                    HeaderValue = obj.get('RoutePredicates').get('HeaderPredicates')[0].get('Value')
                    sheet.write(row, 9, HeaderValue)
                    HeaderType = obj.get('RoutePredicates').get('HeaderPredicates')[0].get('Type')
                    sheet.write(row, 10, HeaderType)


                #查询路由详情
                print('-------------get route detail-------------------')
                get_gateway_route_detail_request = mse_20190531_models.GetGatewayRouteDetailRequest(
                    route_id=Id,
                    gateway_unique_id=parm.gateway_unique_id,
                    accept_language='zh'
                )
                route_detail_rst = client.get_gateway_route_detail_with_options(get_gateway_route_detail_request, runtime)
                print('Code: ', route_detail_rst.to_map().get('body').get('Code'))
                if route_detail_rst.to_map().get('body').get('Data').get('HTTPRewrite'):
                    Rewrite_pathType = route_detail_rst.to_map().get('body').get('Data').get('HTTPRewrite').get('PathType')
                    sheet.write(row, 11, Rewrite_pathType)
                    Rewrite_path = route_detail_rst.to_map().get('body').get('Data').get('HTTPRewrite').get('Path')
                    sheet.write(row, 12, Rewrite_path)


        except Exception as error:
            print(error)
            UtilClient.assert_as_string(error.message)

        #save excel file
        workbook.save(parm.excel_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--access_key_id', type=str, default='')
    parser.add_argument('--access_key_secret', type=str, default='')
    parser.add_argument('--gateway_unique_id', type=str, default='gw-')
    parser.add_argument('--excel_file', type=str, default="./AutoGenerate_RouteList.xls")
    parm = parser.parse_args()
    Sample.main(parm)
