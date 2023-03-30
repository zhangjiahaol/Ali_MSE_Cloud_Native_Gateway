# Cloud Native Gateway Automation Script

## 环境要求
```
python 3.7
pip install alibabacloud_mse20190531==3.0.46
安装脚本所依赖的各种模块
```


## 添加单个路由配置
```

cd AddRouteTable/
python3 AddGatewayRouteItem.py --access_key_id="" --access_key_secret="" --gateway_unique_id="gw-" --source_type="K8S" --namespace="feature-test" --DomainName="api-gateway-feature-test.domain.cn" --RouteName="feature-test-business-entity-service-authentoken" --RoutePath="/business-entity-service" --RouteType="PRE" --HeaderKey="authentoken" --HeaderValue="*" --HeaderType="ERGULAR" --ServiceName="abi-cloud-middle-platform-gateway-server"

```


## 根据excel内容批量添加路由配置
```

cd AddRouteTable/
python3 ReadYamlBatchAddRoutingTable.py --access_key_id="" --access_key_secret="" --excel_file="./RouteConfigList-feature-1.xlsx"

```


## 根据excel内容批量添加白名单
```

cd AddWhiteList/
python3 AddWhiteList.py --access_key_id="" --access_key_secret="" --gateway_unique_id="gw-" --excel_file="./AddWhiteList.xlsx"

```



## 删除和清理网关配置
```

# 根据namespace批量删除服务
cd DeleteAndClean/
python3 DeleteGatewayServiceItem.py --access_key_id="" --access_key_secret="" --gateway_unique_id="gw-" --namespace="feature-test" 

# 根据namespace批量删除路由条目
cd DeleteAndClean/
python3 DeleteGatewayRouteItem.py --access_key_id="" --access_key_secret="" --gateway_unique_id="gw-" --namespace="feature-test"

```


## 导出云原生网关实例下的所有路由表
```
cd ExportExcelRouteTable/
python3 ExportExcelRouteTable.py --access_key_id="" --access_key_secret="" --excel_file="./AutoGenerate_RouteList.xls" --gateway_unique_id="gw-"
```