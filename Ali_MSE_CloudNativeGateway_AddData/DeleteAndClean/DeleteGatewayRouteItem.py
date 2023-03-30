# -*- coding: utf-8 -*-


import argparse
import json

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

        ################## 初始化SDK
        print('------------Init client------------')
        client = Sample.create_client(parm.access_key_id, parm.access_key_secret)
        runtime = util_models.RuntimeOptions()
        print(runtime)
        print(runtime.to_map())

        ################## 查询RouteId，根据RouteName
        print('------------Get RouteId------------')
        filter_params = mse_20190531_models.ListGatewayRouteRequestFilterParams(
            gateway_unique_id=parm.gateway_unique_id
        )
        list_gateway_route_request = mse_20190531_models.ListGatewayRouteRequest(
            page_size=1500,
            page_number=1,
            filter_params=filter_params,
            accept_language='zh'
        )
        RouteId = ''
        try:
            rst = client.list_gateway_route_with_options(list_gateway_route_request, runtime)
            print('original: ', rst)
            print('json: ', json.dumps(rst.to_map()))
            for data in rst.to_map().get('body').get('Data').get('Result'):
                print(data)
                RouteId = str(data.get('Id'))
                print(RouteId)
                # 删除包含$namespace的路由条目
                if parm.namespace in data.get('Name'):
                    print('------------downline Route------------')
                    offline_gateway_route_request = mse_20190531_models.OfflineGatewayRouteRequest(
                        route_id=RouteId,
                        gateway_unique_id=parm.gateway_unique_id,
                        accept_language='zh'
                    )
                    downline_route = client.offline_gateway_route_with_options(offline_gateway_route_request, runtime)
                    print('original: ', downline_route)
                    print('json: ', json.dumps(downline_route.to_map()))
                    print('Code: ', downline_route.to_map().get('body').get('Code'))
                    print('Message: ', downline_route.to_map().get('body').get('Message'))
                    print('------------Delete Route------------')
                    delete_gateway_route_request = mse_20190531_models.DeleteGatewayRouteRequest(
                        accept_language='zh',
                        gateway_unique_id=parm.gateway_unique_id,
                        route_id=RouteId
                    )
                    delete_route = client.delete_gateway_route_with_options(delete_gateway_route_request, runtime)
                    print('original: ', delete_route)
                    print('json: ', json.dumps(delete_route.to_map()))
                    print('Code: ', delete_route.to_map().get('body').get('Code'))
                    print('Message: ', delete_route.to_map().get('body').get('Message'))
            print('Code: ', rst.to_map().get('body').get('Code'))
        except Exception as error:
            print(error)
            UtilClient.assert_as_string(error.message)
        print('------------RouteId Result: ' + RouteId + '------------')





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--access_key_id', type=str, default='')
    parser.add_argument('--access_key_secret', type=str, default='')
    parser.add_argument('--gateway_unique_id', type=str, default='gw-')
    parser.add_argument('--namespace', type=str, default='feature-4')
    parm = parser.parse_args()
    Sample.main(parm)
