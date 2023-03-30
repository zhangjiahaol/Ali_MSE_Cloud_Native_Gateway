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

        ################## 查询ServiceId和GatewayId，根据ServiceName
        print('------------Get ServiceId------------')
        filter_params = mse_20190531_models.ListGatewayServiceRequestFilterParams(
            source_type='K8S',
            #name='',
            namespace=parm.namespace,
            gateway_unique_id=parm.gateway_unique_id
        )
        list_gateway_service_request = mse_20190531_models.ListGatewayServiceRequest(
            filter_params=filter_params,
            page_number=1,
            page_size=1500
        )
        ServiceId = ''
        try:
            rst = client.list_gateway_service_with_options(list_gateway_service_request, runtime)
            print('original: ', rst)
            print('json: ', json.dumps(rst.to_map()))
            print('Code: ', rst.to_map().get('body').get('Code'))
            for obj in rst.to_map().get('body').get('Data').get('Result'):
                ServiceId = obj.get('Id')
                print(ServiceId)

                #删除service
                print('----------------delete service---------------')
                delete_gateway_service_request = mse_20190531_models.DeleteGatewayServiceRequest(
                    service_id=ServiceId,
                    gateway_unique_id=parm.gateway_unique_id,
                    accept_language='zh'
                )
                rst = client.delete_gateway_service_with_options(delete_gateway_service_request, runtime)
                print('original: ', rst)
                print('json: ', json.dumps(rst.to_map()))
                print('Code: ', rst.to_map().get('body').get('Code'))

        except Exception as error:
            print(error)
            UtilClient.assert_as_string(error.message)
        print('------------ServiceId Result: ' + ServiceId + '------------')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--access_key_id', type=str, default='')
    parser.add_argument('--access_key_secret', type=str, default='')
    parser.add_argument('--gateway_unique_id', type=str, default='gw-')
    parser.add_argument('--namespace', type=str, default='feature-test')
    parm = parser.parse_args()
    Sample.main(parm)
