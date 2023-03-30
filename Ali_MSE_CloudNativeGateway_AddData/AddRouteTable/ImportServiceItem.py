# -*- coding: utf-8 -*-

# python ImportServiceItem.py --access_key_id="" --access_key_secret="" --gateway_unique_id="gw-a06af4618a754dca9137dd74a3e6e0b1" --accept_language="zh" --source_type="K8S" --namespace="feature-test" --name="business-entity-service"

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
        client = Sample.create_client(parm.access_key_id, parm.access_key_secret)
        service_list_0 = mse_20190531_models.ImportServicesRequestServiceList(
            name=parm.name,
            namespace=parm.namespace
        )
        import_services_request = mse_20190531_models.ImportServicesRequest(
            gateway_unique_id=parm.gateway_unique_id,
            accept_language=parm.accept_language,
            source_type=parm.source_type,
            service_list=[
                service_list_0
            ]
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            rst = client.import_services_with_options(import_services_request, runtime)
            print('original: ', rst)
            print('json: ', json.dumps(rst.to_map()))
            Code = rst.to_map().get('body').get('Code')
            print('Code: ', Code)
            print('Message: ', rst.to_map().get('body').get('Message'))
            if Code == 200:
                print("Result Import Service Succeeded Code: {}".format(Code))
            else:
                print("Result Import Service Failed Code: {}".format(Code))
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
    parser.add_argument('--gateway_unique_id', type=str, default='gw-')
    parser.add_argument('--source_type', type=str, default='K8S')
    parser.add_argument('--accept_language', type=str, default='zh')

    parser.add_argument('--namespace', type=str, default='uat')
    parser.add_argument('--name', type=str, default='abi-cloud-bees-order-frontend')
    parm = parser.parse_args()
    Sample.main(parm)

