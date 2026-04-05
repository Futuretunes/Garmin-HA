// App settings management

using Toybox.Application;
using Toybox.Application.Properties;

module Settings {
    function getHAUrl() as String {
        var url = Properties.getValue("ha_url") as String;
        if (url == null || url.length() == 0) {
            return "";
        }
        // Strip trailing slash
        if (url.substring(url.length() - 1, url.length()).equals("/")) {
            url = url.substring(0, url.length() - 1);
        }
        return url;
    }

    function getWebhookId() as String {
        var id = Properties.getValue("webhook_id") as String;
        return id != null ? id : "";
    }

    function getApiKey() as String {
        var key = Properties.getValue("api_key") as String;
        return key != null ? key : "";
    }

    function getRefreshInterval() as Number {
        var interval = Properties.getValue("refresh_interval") as Number;
        return interval != null && interval >= 10 ? interval : 30;
    }

    function getWebhookUrl() as String {
        var url = getHAUrl();
        var webhookId = getWebhookId();
        if (url.length() == 0 || webhookId.length() == 0) {
            return "";
        }
        return url + "/api/webhook/" + webhookId;
    }

    function isConfigured() as Boolean {
        return getHAUrl().length() > 0 && getWebhookId().length() > 0;
    }
}
