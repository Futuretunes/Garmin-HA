// Error display view

using Toybox.WatchUi;
using Toybox.Graphics;

class ErrorView extends WatchUi.View {

    var _message as String;

    function initialize(message as String) {
        View.initialize();
        _message = message;
    }

    function onUpdate(dc as Dc) as Void {
        dc.setColor(Constants.COLOR_TEXT, Constants.COLOR_BG);
        dc.clear();

        var width = dc.getWidth();
        var height = dc.getHeight();
        var centerX = width / 2;

        // Error icon (X mark)
        dc.setColor(Constants.COLOR_ERROR, Graphics.COLOR_TRANSPARENT);
        dc.setPenWidth(4);
        var iconCenterY = height * 0.32;
        var iconSize = 20;
        dc.drawLine(centerX - iconSize, iconCenterY - iconSize, centerX + iconSize, iconCenterY + iconSize);
        dc.drawLine(centerX - iconSize, iconCenterY + iconSize, centerX + iconSize, iconCenterY - iconSize);
        dc.setPenWidth(1);

        // Error message
        dc.setColor(Constants.COLOR_TEXT, Graphics.COLOR_TRANSPARENT);
        dc.drawText(centerX, height * 0.50, Graphics.FONT_SMALL, _message, Graphics.TEXT_JUSTIFY_CENTER);

        // Back hint
        dc.setColor(Constants.COLOR_SUBTITLE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(centerX, height * 0.75, Graphics.FONT_XTINY, "Press BACK to return", Graphics.TEXT_JUSTIFY_CENTER);
    }
}

class ErrorDelegate extends WatchUi.BehaviorDelegate {

    function initialize() {
        BehaviorDelegate.initialize();
    }

    function onBack() as Boolean {
        WatchUi.popView(WatchUi.SLIDE_RIGHT);
        return true;
    }
}
