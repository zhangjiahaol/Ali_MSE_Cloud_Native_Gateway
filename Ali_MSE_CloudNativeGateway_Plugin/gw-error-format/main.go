package main

import (
	"errors"

	"github.com/alibaba/higress/plugins/wasm-go/pkg/wrapper"
	"github.com/tetratelabs/proxy-wasm-go-sdk/proxywasm"
	"github.com/tetratelabs/proxy-wasm-go-sdk/proxywasm/types"
	"github.com/tidwall/gjson"
)

func main() {
	wrapper.SetCtx(
		"gw-error-format",
		wrapper.ParseConfigBy(parseConfig),
		wrapper.ProcessResponseHeadersBy(onHttpResponseHeader),
		wrapper.ProcessResponseBodyBy(onHttpResponseBody),
	)
}

type MyConfig struct {
	rules      []gjson.Result
	set_header []gjson.Result
}

func parseConfig(json gjson.Result, config *MyConfig, log wrapper.Log) error {
	config.set_header = json.Get("set_header").Array()
	config.rules = json.Get("rules").Array()
	for _, item := range config.rules {
		log.Info("config.rules: " + item.String())
		// judge config is empty
		if item.Get("match.statuscode").String() == "" {
			return errors.New("missing match.statuscode in config")
		}
		if item.Get("replace.statuscode").String() == "" {
			return errors.New("missing replace.statuscode in config")
		}
	}

	return nil
}

func onHttpResponseHeader(ctx wrapper.HttpContext, config MyConfig, log wrapper.Log) types.Action {
	var DontReadResponseBody = false
	// judge statuscode
	for _, item := range config.rules {
		current_statuscode, err := proxywasm.GetHttpResponseHeader(":status")
		if err != nil {
			log.Critical("failed GetHttpResponseHeader :status")
		}
		config_match_statuscode := item.Get("match.statuscode").String()
		config_replace_statuscode := item.Get("replace.statuscode").String()

		switch current_statuscode {
		//case "403", "503":
		case config_match_statuscode:
			// If the response header `x-envoy-upstream-service-time`  is not found,  the request has  not  been  forwarded to the  backend  service
			_, err := proxywasm.GetHttpResponseHeader("x-envoy-upstream-service-time")
			if err != nil {
				proxywasm.RemoveHttpResponseHeader("content-length")
				// replace statuscode
				err = proxywasm.ReplaceHttpResponseHeader(":status", config_replace_statuscode)
				if err != nil {
					log.Critical("failed ReplaceHttpResponseHeader :status")
				}
				// replace ResponseHeader
				for _, item_header := range config.set_header {
					item_header.ForEach(func(key, value gjson.Result) bool {
						err := proxywasm.ReplaceHttpResponseHeader(key.String(), value.String())
						if err != nil {
							log.Critical("failed ReplaceHttpResponseHeader" + item_header.String())
						}
						return true
					})
				}
			} else {
				ctx.DontReadResponseBody()
			}
			return types.ActionContinue
		default:
			DontReadResponseBody = true
		}
	}

	if DontReadResponseBody == true {
		ctx.DontReadResponseBody()
	}
	return types.ActionContinue
}

func onHttpResponseBody(ctx wrapper.HttpContext, config MyConfig, body []byte, log wrapper.Log) types.Action {
	bodyStr := string(body)

	// judge responsebody
	for _, item := range config.rules {
		config_match_responsebody := item.Get("match.responsebody").String()
		config_replace_responsebody := item.Get("replace.responsebody").String()
		log.Debug("bodyStr: " + bodyStr)
		log.Debug("config_match_responsebody: " + config_match_responsebody)
		if bodyStr == config_match_responsebody {
			log.Debug(bodyStr)
			// Replace ResponseBody
			err := proxywasm.ReplaceHttpResponseBody([]byte(config_replace_responsebody))
			if err != nil {
				log.Critical("failed config_replace_responsebody" + config_replace_responsebody)
			}
			return types.ActionContinue
		}
	}

	return types.ActionContinue
}
