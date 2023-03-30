package main

import (
	"net/http"
	"regexp"
	"strconv"
	"strings"

	"github.com/alibaba/higress/plugins/wasm-go/pkg/wrapper"
	"github.com/tetratelabs/proxy-wasm-go-sdk/proxywasm"
	"github.com/tetratelabs/proxy-wasm-go-sdk/proxywasm/types"
	"github.com/tidwall/gjson"
)

func main() {
	wrapper.SetCtx(
		"satoken-query-userinfo",
		wrapper.ParseConfigBy(parseConfig),
		wrapper.ProcessRequestHeadersBy(onHttpRequestHeaders),
	)
}

type MyConfig struct {
	white_list_skip_path []gjson.Result
}

func parseConfig(json gjson.Result, config *MyConfig, log wrapper.Log) error {
	config.white_list_skip_path = json.Get("white_list_skip_path").Array()
	return nil
}

func onHttpRequestHeaders(ctx wrapper.HttpContext, config MyConfig, log wrapper.Log) types.Action {
	log.Info("---------satoken-query-userinfo OnHttpRequestHeaders start-----------")

	proxywasm.AddHttpRequestHeader("gateway_start", "gateway_start")

	authority, _ := proxywasm.GetHttpRequestHeader(":authority")
	request_path, _ := proxywasm.GetHttpRequestHeader(":path")
	request_url := authority + request_path

	////get x-request-id set request header request_id
	x_request_id, err := proxywasm.GetHttpRequestHeader("x-request-id")
	if err != nil {
		log.Critical(request_url + " failed to get request header x-request-id")
		proxywasm.AddHttpRequestHeader("request_id", "failed to get request header x-request-id")
	}
	err = proxywasm.AddHttpRequestHeader("request_id", x_request_id)
	if err != nil {
		log.Critical(request_url + " failed to set request header request_id")
	}
	trace_str := request_url + " | " + x_request_id + " | "

	// pass whitelist
	for _, line_path_json := range config.white_list_skip_path {
		pattern_str := line_path_json.Get("path").String()
		pass, err := regexp.MatchString(pattern_str, request_path)
		if err != nil {
			log.Critical(trace_str + " failed regexp.MatchString: " + "pattern_str=" + pattern_str + "request_path=" + request_path)
		}
		if pass == true {
			log.Info(trace_str + "white_list_skip_path pass == true | " + pattern_str)
			proxywasm.AddHttpRequestHeader("gateway_end", "gateway_end")
			return types.ActionContinue
		}
	}

	// GetHttpRequestHeader satoken payload loginId
	satoken, err := proxywasm.GetHttpRequestHeader("satoken")
	if err != nil || satoken == "" || len(satoken) == 0 {
		log.Info(trace_str + "--------- is not satoken -----------")
		proxywasm.AddHttpRequestHeader("gateway_end", "gateway_end")
		log.Info(trace_str + "---------satoken-query-userinfo OnHttpRequestHeaders end-----------")
		return types.ActionContinue
	} else {
		log.Info(trace_str + "go by satoken: " + satoken)

		// get Host header split env
		var Host_env = ""
		Host, err := proxywasm.GetHttpRequestHeader("Host")
		if err != nil || strings.EqualFold(Host, "") || len(Host) == 0 {
			log.Critical(trace_str + "GetHttpRequestHeader failed not find Host")
			return types.ActionContinue
		} else {
			if strings.EqualFold(Host, "api-gateway.domain.cn") {
				Host_env = "prod"
			} else {
				//api-gateway-dev.domain.cn
				if len(strings.Split(Host, ".")) != 3 || !strings.Contains(Host, "api-gateway-") {
					log.Critical(trace_str + "Host Split failed")
					return types.ActionContinue
				} else {
					//api-gateway-dev
					domain_name_prefix := strings.Split(Host, ".")[0]
					//dev
					Host_env = strings.Split(domain_name_prefix, "api-gateway-")[1]
				}
			}
			err = proxywasm.AddHttpRequestHeader("Host_env", Host_env)
			if err != nil {
				log.Critical(trace_str + "failed to set request header Host_env:" + Host_env)
			}
		}

		// request http auth-service interface
		var client wrapper.HttpClient
		// serviceSource: k8s
		client = wrapper.NewClusterClient(wrapper.K8sCluster{
			ServiceName: "abi-cloud-middle-platform-auth-service-server",
			Namespace:   Host_env,
			Port:        8080,
		})
		request_service_headers := [][2]string{
			{"satoken", satoken},
		}
		// This http interface will get the following information set into the request header
		// 1. userLoginId == userLoginId: 23090
		// 2. userId == userId: 23078
		// 3. roleIds == userRoles: ["10341","10607"]
		// 4. SALES_MAN_CODE == employeeNo: 18490446
		// The interface verifies that the satoken is expired or invalid
		// The http request default timeout period is 500 milliseconds
		client.Get("/abi-cloud-middle-platform-auth-service/login/get/user/check-login", request_service_headers,
			func(statusCode int, responseHeaders http.Header, responseBody []byte) {
				log.Info(trace_str + "---------satoken-query-userinfo httpCallResponseCallback start-----------")

				log.Infof(trace_str+"get status: %d, request body: %s", statusCode, responseBody)

				truestatusCode := statusCode
				proxywasm.AddHttpRequestHeader("AuthServiceStatusCode", strconv.Itoa(truestatusCode))
				if err != nil {
					log.Critical(trace_str + "AuthServiceStatusCode failed to set request header")
					proxywasm.ResumeHttpRequest()
				}

				SendHttpResponseHeaders := [][2]string{
					{"Content-Type", "application/json;charset=UTF-8"},
					{"Access-Control-Allow-Origin", "*"},
					{"Access-Control-Allow-Headers", "*"},
					{"Access-Control-Allow-Methods", "*"},
					{"Access-Control-Expose-Headers", "*"},
					{"Access-Control-Allow-Credentials", "true"},
				}

				// The request did not return a 200 status code
				if truestatusCode != http.StatusOK {
					log.Errorf(trace_str+"namespace: %s abi-cloud-middle-platform-auth-service http call, truestatusCode: %d , responseBody: %s", Host_env, truestatusCode, responseBody)
					proxywasm.SendHttpResponse(uint32(truestatusCode), SendHttpResponseHeaders, []byte(responseBody), -1)
					return
				}

				// Gjson parse ResponseBody
				request_service_responseBody := string(responseBody)
				code_status := gjson.Get(string(request_service_responseBody), "code")
				SALES_MAN_CODE := gjson.Get(request_service_responseBody, "data.employeeNo").String()
				roleIds := gjson.Get(request_service_responseBody, "data.userRoles").String()
				userId := gjson.Get(request_service_responseBody, "data.userId").String()
				userLoginId := gjson.Get(request_service_responseBody, "data.userLoginId").String()
				log.Info(trace_str + "gjson parse data: code_status=" + code_status.String() + " SALES_MAN_CODE=" + SALES_MAN_CODE + " roleIds=" + roleIds + " userId=" + userId + " userLoginId=" + userLoginId)

				if code_status.Int() != http.StatusOK {
					log.Errorf(trace_str+"namespace: %s abi-cloud-middle-platform-auth-service http call, truestatusCode: %d , code_status: %s, responseBody: %s", Host_env, truestatusCode, code_status.String(), responseBody)
					proxywasm.SendHttpResponse(uint32(truestatusCode), SendHttpResponseHeaders, []byte(responseBody), -1)
					return
				}

				////set request header userLoginId
				err = proxywasm.AddHttpRequestHeader("userLoginId", userLoginId)
				if err != nil {
					log.Critical(trace_str + "failed to set request header userLoginId:" + userLoginId)
					proxywasm.ResumeHttpRequest()
				}

				////set request header roleIds
				err = proxywasm.AddHttpRequestHeader("roleIds", roleIds)
				if err != nil {
					log.Critical(trace_str + "roleIds failed to set request header")
					proxywasm.ResumeHttpRequest()
				}

				////set request header SALES_MAN_CODE
				err = proxywasm.AddHttpRequestHeader("SALES_MAN_CODE", SALES_MAN_CODE)
				if err != nil {
					log.Critical(trace_str + "SALES_MAN_CODE failed to set request header")
					proxywasm.ResumeHttpRequest()
				}

				////set request header userId
				err = proxywasm.AddHttpRequestHeader("userId", userId)
				if err != nil {
					log.Critical(trace_str + "userId failed to set request header")
					proxywasm.ResumeHttpRequest()
				}

				proxywasm.AddHttpRequestHeader("gateway_end", "gateway_end")

				log.Info(trace_str + "---------satoken-query-userinfo httpCallResponseCallback end-----------")
				proxywasm.ResumeHttpRequest()
			}, 5000)

	}

	////set request header gateway_end
	proxywasm.AddHttpRequestHeader("gateway_end", "gateway_end")

	log.Info(trace_str + "---------satoken-query-userinfo OnHttpRequestHeaders end-----------")

	// You need to wait for the asynchronous callback to complete, return to the Pause state, which can be restored by ResumeHttpRequest
	return types.ActionPause
}
