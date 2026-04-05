// Loading spinner view

using Toybox.WatchUi;
using Toybox.Graphics;
using Toybox.Timer;

class LoadingView extends WatchUi.View {

    var _message as String;
    var _dotCount = 0;
    var _timer as Timer.Timer?;

    function initialize(message as String) {
        View.initialize();
        _message = message;
    }

    function onShow() as Void {
        _timer = new Timer.Timer();
        _timer.start(method(:onTimer), 500, true);
    }

    function onHide() as Void {
        if (_timer != null) {
            _timer.stop();
            _timer = null;
        }
    }

    function onTimer() as Void {
        _dotCount = (_dotCount + 1) % 4;
        WatchUi.requestUpdate();
    }

    function onUpdate(dc as Dc) as Void {
        dc.setColor(Constants.COLOR_TEXT, Constants.COLOR_BG);
        dc.clear();

        var width = dc.getWidth();
        var height = dc.getHeight();
        var centerX = width / 2;
        var centerY = height / 2;

        // Draw loading animation (rotating dots)
        var radius = 30;
        for (var i = 0; i < 8; i++) {
            var angle = (i * 45 + _dotCount * 45) * Math.PI / 180.0;
            var x = centerX + (radius * Math.cos(angle)).toNumber();
            var y = centerY - 30 + (radius * Math.sin(angle)).toNumber();
            var dotSize = (i == 0) ? 5 : 3;
            var color = (i == 0) ? Constants.COLOR_LOADING : Constants.COLOR_SUBTITLE;
            dc.setColor(color, Graphics.COLOR_TRANSPARENT);
            dc.fillCircle(x, y, dotSize);
        }

        // Message
        dc.setColor(Constants.COLOR_TEXT, Graphics.COLOR_TRANSPARENT);
        dc.drawText(centerX, centerY + 20, Graphics.FONT_SMALL, _message, Graphics.TEXT_JUSTIFY_CENTER);
    }
}

class LoadingDelegate extends WatchUi.BehaviorDelegate {

    function initialize() {
        BehaviorDelegate.initialize();
    }

    function onBack() as Boolean {
        WatchUi.popView(WatchUi.SLIDE_RIGHT);
        return true;
    }
}
