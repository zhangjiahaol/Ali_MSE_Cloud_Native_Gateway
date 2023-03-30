package main

import (
	"strings"

	"github.com/alibaba/higress/plugins/wasm-go/pkg/wrapper"
	"github.com/tetratelabs/proxy-wasm-go-sdk/proxywasm"
	"github.com/tetratelabs/proxy-wasm-go-sdk/proxywasm/types"
)

func main() {
	wrapper.SetCtx(
		"authtk-path-rewrite",
		wrapper.ProcessRequestHeadersBy(onHttpRequestHeaders),
	)
}

type MyConfig struct{}

func onHttpRequestHeaders(ctx wrapper.HttpContext, config MyConfig, log wrapper.Log) types.Action {
	log.Info("---------authtk-path-rewrite OnHttpRequestHeaders start-----------")

	authority, _ := proxywasm.GetHttpRequestHeader(":authority")
	request_path, _ := proxywasm.GetHttpRequestHeader(":path")
	request_url := authority + request_path

	////get x-request-id set request header request_id
	x_request_id, err := proxywasm.GetHttpRequestHeader("x-request-id")
	if err != nil {
		log.Critical(request_url + " failed to get request header x-request-id")
		proxywasm.AddHttpRequestHeader("request_id", "failed to get request header x-request-id")
	}
	trace_str := request_url + " | " + x_request_id + " | "

	//get header: authentoken
	authentoken, err := proxywasm.GetHttpRequestHeader("authentoken")
	if err != nil || authentoken == "" || len(authentoken) == 0 {
		log.Info(trace_str + "--------- is not authentoken no rewrite -----------")
		////set request header Used of marking.
		err = proxywasm.AddHttpRequestHeader("rewrite", "no rewrite")
		log.Info(trace_str + "---------authtk-path-rewrite OnHttpRequestHeaders end-----------")
		return types.ActionContinue
	} else {
		log.Info(trace_str + "go by authentoken: " + authentoken)
		////set request header Used of marking.
		err = proxywasm.AddHttpRequestHeader("rewrite", "authentoken")
		if err != nil {
			log.Critical(trace_str + "failed to set request header rewrite")
		}

		//original request_path
		request_path, err := proxywasm.GetHttpRequestHeader(":path")
		if err != nil {
			log.Critical(trace_str + "failed to get request header")
		}

		// replace
		log.Info("rewrite path add prefix: " + "/authentoken-" + strings.TrimPrefix(request_path, "/"))
		err = proxywasm.ReplaceHttpRequestHeader(":path", "/authentoken-"+strings.TrimPrefix(request_path, "/"))
		if err != nil {
			log.Critical(trace_str + "failed to ReplaceHttpRequestHeader")
		}

		// replace request_path
		request_path, err = proxywasm.GetHttpRequestHeader(":path")
		if err != nil {
			log.Critical(trace_str + "failed to get request header")
		}

		//rewrite path goto abi-cloud-middle-platform-gateway-server
		log.Info(trace_str + "rewrite path goto abi-cloud-middle-platform-gateway-server: " + authentoken)

		log.Info(trace_str + "---------authtk-path-rewrite OnHttpRequestHeaders end-----------")
		return types.ActionContinue
	}
}
