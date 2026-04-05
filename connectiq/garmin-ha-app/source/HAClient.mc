// HTTP communication with Home Assistant webhook

using Toybox.Communications;
using Toybox.Lang;

module HAClient {
    // Track if a request is in flight to avoid BLE_QUEUE_FULL
    var _requestInFlight = false;

    function getStates(domain as String, callback as Method) as Void {
        var params = {
            "action" => Constants.ACTION_GET_STATES,
            "domain" => domain
        };
        _makeRequest(params, callback);
    }

    function getStatesPage(domain as String, page as Number, callback as Method) as Void {
        var params = {
            "action" => Constants.ACTION_GET_STATES,
            "domain" => domain,
            "page" => page,
            "page_size" => 15
        };
        _makeRequest(params, callback);
    }

    function callService(domain as String, service as String, entityId as String, callback as Method) as Void {
        var params = {
            "action" => Constants.ACTION_CALL_SERVICE,
            "domain" => domain,
            "service" => service,
            "entity_id" => entityId
        };
        _makeRequest(params, callback);
    }

    function callServiceWithData(domain as String, service as String, entityId as String, data as Dictionary, callback as Method) as Void {
        var params = {
            "action" => Constants.ACTION_CALL_SERVICE,
            "domain" => domain,
            "service" => service,
            "entity_id" => entityId,
            "data" => data
        };
        _makeRequest(params, callback);
    }

    function getDashboard(callback as Method) as Void {
        var params = {
            "action" => Constants.ACTION_GET_DASHBOARD
        };
        _makeRequest(params, callback);
    }

    function _makeRequest(params as Dictionary, callback as Method) as Void {
        var url = Settings.getWebhookUrl();
        if (url.length() == 0) {
            callback.invoke(Communications.INVALID_HTTP_BODY_IN_NETWORK_RESPONSE, null);
            return;
        }

        if (_requestInFlight) {
            // Queue is busy, skip this request
            return;
        }

        var options = {
            :method => Communications.HTTP_REQUEST_METHOD_POST,
            :headers => {
                "Content-Type" => Communications.REQUEST_CONTENT_TYPE_JSON
            },
            :responseType => Communications.HTTP_RESPONSE_CONTENT_TYPE_JSON
        };

        // Add API key header if configured
        var apiKey = Settings.getApiKey();
        if (apiKey.length() > 0) {
            options[:headers]["X-GarminHA-Key"] = apiKey;
        }

        _requestInFlight = true;
        Communications.makeWebRequest(url, params, options, method(:_onResponse));
        // Store callback for use in response handler
        _pendingCallback = callback;
    }

    var _pendingCallback as Method?;

    function _onResponse(responseCode as Number, data as Dictionary or Null) as Void {
        _requestInFlight = false;
        var callback = _pendingCallback;
        _pendingCallback = null;

        if (callback != null) {
            callback.invoke(responseCode, data);
        }
    }
}
