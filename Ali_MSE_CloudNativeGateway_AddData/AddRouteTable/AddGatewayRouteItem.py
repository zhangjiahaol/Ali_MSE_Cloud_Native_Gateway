# -*- coding: utf-8 -*-

# python3 AddGatewayRouteItem.py --access_key_id="" --access_key_secret="" --gateway_unique_id="gw-a06af4618a754dca9137dd74a3e6e0b1" --source_type="K8S" --namespace="feature-test"--DomainName="api-gateway-feature-test.domain.cn" --RouteName="feature-test-business-entity-service-authentoken" --RoutePath="/business-entity-service" --RouteType="PRE" --ServiceName="abi-cloud-middle-platform-gateway-server" --HeaderKey="authentoken" --HeaderValue="*" --HeaderType="ERGULAR" --Rewrite_pathType="PRE" --Rewrite_path="/"


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

        ################## 导入服务来源
        print('------------Import Services------------')
        service_list_0 = mse_20190531_models.ImportServicesRequestServiceList(
            name=parm.ServiceName,
            namespace=parm.namespace
        )
        import_services_request = mse_20190531_models.ImportServicesRequest(
            gateway_unique_id=parm.gateway_unique_id,
            accept_language='zh',
            source_type=parm.source_type,
            service_list=[
                service_list_0
            ]
        )
        try:
            rst = client.import_services_with_options(import_services_request, runtime)
            print('original: ', rst)
            print('json: ', json.dumps(rst.to_map()))
            Code = rst.to_map().get('body').get('Code')
            print('Code: ', Code)
            Message = rst.to_map().get('body').get('Message')
            print('Message: ', Message)
            if Code == 200:
                print("Result Import Service Succeeded Code: {}".format(Code))
            elif Message in "已有重名服务存在":
                print("Result Import Service already existed Code: {}".format(Code))
            else:
                print("Result Import Service Failed Code: {}".format(Code))
        except Exception as error:
            # 如有需要，请打印 error
            print(error)
            UtilClient.assert_as_string(error.message)

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
                if data.get('Name') in parm.DomainName:
                    print(data.get('Name'))
                    DomainId = str(data.get('Id'))
            print('Code: ', rst.to_map().get('body').get('Code'))
            print('Message: ', rst.to_map().get('body').get('Message'))
        except Exception as error:
            print(error)
            UtilClient.assert_as_string(error.message)
        print('------------DomainId Result: ' + DomainId + '------------')

        ################## 查询ServiceId和GatewayId，根据ServiceName
        print('------------Get ServiceId------------')
        filter_params = mse_20190531_models.ListGatewayServiceRequestFilterParams(
            source_type=parm.source_type,
            name=parm.ServiceName,
            namespace=parm.namespace,
            gateway_unique_id=parm.gateway_unique_id
        )
        list_gateway_service_request = mse_20190531_models.ListGatewayServiceRequest(
            filter_params=filter_params
        )
        ServiceId = ''
        GatewayId = ''
        try:
            rst = client.list_gateway_service_with_options(list_gateway_service_request, runtime)
            print('original: ', rst)
            print('json: ', json.dumps(rst.to_map()))
            print(rst.to_map().get('body').get('Data').get('Result')[0].get('Name'))
            ServiceId = str(rst.to_map().get('body').get('Data').get('Result')[0].get('Id'))
            GatewayId = rst.to_map().get('body').get('Data').get('Result')[0].get('GatewayId')
            print('Code: ', rst.to_map().get('body').get('Code'))
            print('Message: ', rst.to_map().get('body').get('Message'))
        except Exception as error:
            print(error)
            UtilClient.assert_as_string(error.message)
        print('------------ServiceId Result: ' + ServiceId + '------------')

        ################## 添加路由条目
        print('------------AddGatewayRoute------------')
        if parm.HeaderKey:
            predicates_header_predicates_0 = mse_20190531_models.AddGatewayRouteRequestPredicatesHeaderPredicates(
                key=parm.HeaderKey,
                value=parm.HeaderValue,
                type=parm.HeaderType
            )
        predicates_path_predicates = mse_20190531_models.AddGatewayRouteRequestPredicatesPathPredicates(
            path=parm.RoutePath,
            type=parm.RouteType,
            ignore_case=True
        )
        if parm.HeaderKey:
            predicates = mse_20190531_models.AddGatewayRouteRequestPredicates(
                path_predicates=predicates_path_predicates,
                header_predicates=[
                    predicates_header_predicates_0
                ]
            )
        else:
            predicates = mse_20190531_models.AddGatewayRouteRequestPredicates(
                path_predicates=predicates_path_predicates
            )
        services_0 = mse_20190531_models.AddGatewayRouteRequestServices(
            service_id=ServiceId,
            service_port=int(float(parm.ServicePort)),
            agreement_type=parm.AgreementType,
            name=parm.ServiceName,
            source_type=parm.source_type,
            namespace=parm.namespace
        )
        add_gateway_route_request = mse_20190531_models.AddGatewayRouteRequest(
            gateway_id=GatewayId,
            name=parm.RouteName,
            services=[
                services_0
            ],
            domain_id=DomainId,
            predicates=predicates
        )
        try:
            rst = client.add_gateway_route_with_options(add_gateway_route_request, runtime)
            print('original: ', rst)
            print('json: ', json.dumps(rst.to_map()))
            Code = rst.to_map().get('body').get('Code')
            print('Code: ', Code)
            print('Message: ', rst.to_map().get('body').get('Message'))
            if Code == 200:
                print("Result Add Route Succeeded Code: {}".format(Code))
            else:
                print("Result Add Route Failed Code: {}".format(Code))
        except Exception as error:
            print(error)
            UtilClient.assert_as_string(error.message)

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
                if data.get('Name') in parm.RouteName:
                    print(data.get('Name'))
                    RouteId = str(data.get('Id'))
                    print(RouteId)
            print('Code: ', rst.to_map().get('body').get('Code'))
            print('Message: ', rst.to_map().get('body').get('Message'))
        except Exception as error:
            print(error)
            UtilClient.assert_as_string(error.message)
        print('------------RouteId Result: ' + RouteId + '------------')

        ################## 发布路由条目
        print('------------Publish RouteConfig------------')
        apply_gateway_route_request = mse_20190531_models.ApplyGatewayRouteRequest(
            route_id=RouteId,
            gateway_unique_id=parm.gateway_unique_id,
            accept_language='zh'
        )
        try:
            rst = client.apply_gateway_route_with_options(apply_gateway_route_request, runtime)
            print('original: ', rst)
            print('json: ', json.dumps(rst.to_map()))
            print('Code: ', rst.to_map().get('body').get('Code'))
            print('Message: ', rst.to_map().get('body').get('Message'))
        except Exception as error:
            # 如有需要，请打印 error
            print(error)
            UtilClient.assert_as_string(error.message)

        ################## 增加路由跨域策略
        print('------------Add Route Cross domain policy------------')
        cors_json = mse_20190531_models.UpdateGatewayRouteCORSRequestCorsJSON(
            status='on',
            allow_credentials=True,
            time_unit='h',
            unit_num=24,
            expose_headers='*',
            allow_headers='*',
            allow_origins='*',
            allow_methods='GET,POST,PUT,DELETE,HEAD,OPTIONS,PATCH'
        )
        update_gateway_route_corsrequest = mse_20190531_models.UpdateGatewayRouteCORSRequest(
            id=RouteId,
            cors_json=cors_json,
            gateway_unique_id=parm.gateway_unique_id,
            accept_language='zh'
        )
        try:
            rst = client.update_gateway_route_corswith_options(update_gateway_route_corsrequest, runtime)
            print('original: ', rst)
            print('json: ', json.dumps(rst.to_map()))
            print('Code: ', rst.to_map().get('body').get('Code'))
            print('Message: ', rst.to_map().get('body').get('Message'))
        except Exception as error:
            print(error)
            UtilClient.assert_as_string(error.message)

        ################## 增加路由重写策略
        if parm.Rewrite_path:
            print('------------Add Route Rewrite policy------------')
            update_gateway_route_httprewrite_request = mse_20190531_models.UpdateGatewayRouteHTTPRewriteRequest(
                id=RouteId,
                gateway_unique_id=parm.gateway_unique_id,
                accept_language='zh',
                http_rewrite_json='{"pathType":"'+parm.Rewrite_pathType+'","path":"'+parm.Rewrite_path+'","status":"on"}'
            )
            try:
                rst = client.update_gateway_route_httprewrite_with_options(update_gateway_route_httprewrite_request, runtime)
                print('original: ', rst)
                print('json: ', json.dumps(rst.to_map()))
                print('Code: ', rst.to_map().get('body').get('Code'))
                print('Message: ', rst.to_map().get('body').get('Message'))
            except Exception as error:
                print(error)
                UtilClient.assert_as_string(error.message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--access_key_id', type=str, default='')
    parser.add_argument('--access_key_secret', type=str, default='')
    # bees-dev
    parser.add_argument('--gateway_unique_id', type=str, default='gw-')
    # bees-uat
    #parser.add_argument('--gateway_unique_id', type=str, default='gw-')
    # bees-prod
    # parser.add_argument('--gateway_unique_id', type=str, default='gw-')

    parser.add_argument('--source_type', type=str, default='K8S')


    ### add route
    parser.add_argument('--namespace', type=str, default='prod')
    parser.add_argument('--DomainName', type=str, default='api-gateway-feature-1.domain.cn')

    ### 路由名称不能超过63个字符长度
    parser.add_argument('--RouteName', type=str, default='feature-1-bees-bff-service-authentoken')
    parser.add_argument('--RoutePath', type=str, default='/authentoken-abi-cloud-bees-bff-service')
    parser.add_argument('--RouteType', type=str, default='PRE')

    parser.add_argument('--HeaderKey', type=str, default='')
    parser.add_argument('--HeaderValue', type=str, default='')
    parser.add_argument('--HeaderType', type=str, default='ERGULAR')

    parser.add_argument('--Rewrite_pathType', type=str, default='PRE')
    parser.add_argument('--Rewrite_path', type=str, default='/abi-cloud-bees-bff-service')

    parser.add_argument('--ServiceName', type=str, default='abi-cloud-middle-platform-gateway-server')
    #parser.add_argument('--ServiceName', type=str, default='abi-cloud-bees-order-frontend')
    parser.add_argument('--AgreementType', type=str, default='HTTP')
    parser.add_argument('--ServicePort', type=str, default='8080')

    parm = parser.parse_args()
    Sample.main(parm)
