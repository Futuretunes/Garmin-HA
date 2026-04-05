// Detail view for a single entity

using Toybox.WatchUi;
using Toybox.Graphics;

class EntityDetailView extends WatchUi.View {

    var _entity as Dictionary;
    var _domain as String?;

    function initialize(entity as Dictionary, domain as String?) {
        View.initialize();
        _entity = entity;
        _domain = domain;
    }

    function onUpdate(dc as Dc) as Void {
        dc.setColor(Constants.COLOR_TEXT, Constants.COLOR_BG);
        dc.clear();

        var width = dc.getWidth();
        var height = dc.getHeight();
        var centerX = width / 2;

        var name = _entity["n"] as String;
        var state = _entity["s"] as String;
        var entityId = _entity["i"] as String;

        // Entity name
        dc.setColor(Constants.COLOR_TEXT, Graphics.COLOR_TRANSPARENT);
        dc.drawText(centerX, height * 0.25, Graphics.FONT_MEDIUM, name, Graphics.TEXT_JUSTIFY_CENTER);

        // State with color
        var stateColor = _getStateColor(state);
        dc.setColor(stateColor, Graphics.COLOR_TRANSPARENT);
        dc.drawText(centerX, height * 0.42, Graphics.FONT_LARGE, _formatState(state), Graphics.TEXT_JUSTIFY_CENTER);

        // Entity ID
        dc.setColor(Constants.COLOR_SUBTITLE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(centerX, height * 0.62, Graphics.FONT_XTINY, entityId, Graphics.TEXT_JUSTIFY_CENTER);

        // Action hint
        if (_domain != null && Constants.isToggleable(_domain)) {
            dc.setColor(Constants.COLOR_LOADING, Graphics.COLOR_TRANSPARENT);
            dc.drawText(centerX, height * 0.78, Graphics.FONT_SMALL, "Press START to toggle", Graphics.TEXT_JUSTIFY_CENTER);
        }
    }

    function _getStateColor(state as String) as Number {
        if (state.equals("on") || state.equals("unlocked") || state.equals("home")) {
            return Constants.COLOR_ON;
        }
        if (state.equals("off") || state.equals("locked") || state.equals("away")) {
            return Constants.COLOR_OFF;
        }
        if (state.equals("unavailable")) {
            return Constants.COLOR_ERROR;
        }
        return Constants.COLOR_TEXT;
    }

    function _formatState(state as String) as String {
        if (state.equals("on")) { return "ON"; }
        if (state.equals("off")) { return "OFF"; }
        if (state.equals("locked")) { return "LOCKED"; }
        if (state.equals("unlocked")) { return "UNLOCKED"; }
        return state.toUpper();
    }
}

class EntityDetailDelegate extends WatchUi.BehaviorDelegate {

    var _entity as Dictionary;
    var _domain as String?;

    function initialize(entity as Dictionary, domain as String?) {
        BehaviorDelegate.initialize();
        _entity = entity;
        _domain = domain;
    }

    function onSelect() as Boolean {
        if (_domain != null && Constants.isToggleable(_domain)) {
            var entityId = _entity["i"] as String;
            var currentState = _entity["s"] as String;
            var service = Constants.getToggleService(_domain, currentState);
            HAClient.callService(_domain, service, entityId, method(:onToggleResponse));
            return true;
        }
        return false;
    }

    function onToggleResponse(responseCode as Number, data as Dictionary or Null) as Void {
        if (responseCode == 200 && data != null && data["s"] == 1) {
            var newState = data["ns"];
            if (newState != null) {
                _entity["s"] = newState;
                WatchUi.requestUpdate();
            }
        }
    }

    function onBack() as Boolean {
        WatchUi.popView(WatchUi.SLIDE_RIGHT);
        return true;
    }
}
