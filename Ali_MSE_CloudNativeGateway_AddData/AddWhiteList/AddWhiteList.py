# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import argparse
import json
import sys

from typing import List

import xlrd2
from alibabacloud_mse20190531.client import Client as mse20190531Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_mse20190531 import models as mse_20190531_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


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
            # 必填，您的 AccessKey ID,
            access_key_id=access_key_id,
            # 必填，您的 AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # 访问的域名
        config.endpoint = f'mse.cn-shanghai.aliyuncs.com'
        return mse20190531Client(config)

    @staticmethod
    def main(
        args: List[str],
    ) -> None:
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
                DomainName = table.cell_value(row, 0)
                path = table.cell_value(row, 1)
                print("DomainName: {}; path: {}; ".format(DomainName, path))

                ################## 初始化SDK
                print('------------Init client------------')
                client = Sample.create_client(parm.access_key_id, parm.access_key_secret)
                runtime = util_models.RuntimeOptions()
                print(runtime)
                print(runtime.to_map())

                ################## 查询DomainId，根据DomainName
                print('------------Get DomainId------------')
                list_gateway_domain_request = mse_20190531_models.ListGatewayDomainRequest(
                    gateway_unique_id=parm.gateway_unique_id
                )
                DomainId = ''
                try:
                    rst = client.list_gateway_domain_with_options(list_gateway_domain_request, runtime)
                    print('original: ', rst)
                    print('json: ', json.dumps(rst.to_map()))
                    for data in rst.to_map().get('body').get('Data'):
                        if data.get('Name') in DomainName:
                            print(data.get('Name'))
                            DomainId = str(data.get('Id'))
                    print('Code: ', rst.to_map().get('body').get('Code'))
                    print('Message: ', rst.to_map().get('body').get('Message'))
                except Exception as error:
                    print(error)
                    UtilClient.assert_as_string(error.message)
                print('------------DomainId Result: ' + DomainId + '------------')

                #根据excel，批量添加白名单
                print('------------Add WhiteList------------')
                add_auth_resource_request = mse_20190531_models.AddAuthResourceRequest(
                    auth_id=parm.auth_id,
                    path=path,
                    gateway_unique_id=parm.gateway_unique_id,
                    match_type='ERGULAR',
                    accept_language='zh',
                    domain_id=DomainId
                )
                try:
                    # 复制代码运行请自行打印 API 的返回值
                    rst = client.add_auth_resource_with_options(add_auth_resource_request, runtime)
                    print('original: ', rst)
                    print('json: ', json.dumps(rst.to_map()))
                    print('Code: ', rst.to_map().get('body').get('Code'))
                    print('Message: ', rst.to_map().get('body').get('Message'))
                except Exception as error:
                    # 如有需要，请打印 error
                    print(error)
                    UtilClient.assert_as_string(error.message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--access_key_id', type=str, default='')
    parser.add_argument('--access_key_secret', type=str, default='')
    # bees-dev
    # parser.add_argument('--gateway_unique_id', type=str, default='gw-')
    # bees-uat
    #parser.add_argument('--gateway_unique_id', type=str, default='gw-')
    # bees-prod
    parser.add_argument('--gateway_unique_id', type=str, default='gw-')

    # bees-dev
    #parser.add_argument('--auth_id', type=int, default=154)
    # bees-uat
    #parser.add_argument('--auth_id', type=int, default=187)
    # bees-prod
    parser.add_argument('--auth_id', type=int, default=308)
    #excel内容需要手动去重
    parser.add_argument('--excel_file', type=str, default="./AddWhiteList.xlsx")
    parm = parser.parse_args()
    Sample.main(parm)
