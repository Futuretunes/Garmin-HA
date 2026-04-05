// Main application entry point

using Toybox.Application;
using Toybox.WatchUi;
using Toybox.System;

class GarminHAApp extends Application.AppBase {

    function initialize() {
        AppBase.initialize();
    }

    function onStart(state as Dictionary?) as Void {
    }

    function onStop(state as Dictionary?) as Void {
    }

    function getInitialView() as [Views] or [Views, InputDelegates] {
        if (!Settings.isConfigured()) {
            return [new ErrorView("Configure settings\nin Garmin Connect\nmobile app"), new ErrorDelegate()];
        }
        return [new MainMenuView(), new MainMenuDelegate()];
    }

    function onSettingsChanged() as Void {
        // Restart the app view when settings change
        if (Settings.isConfigured()) {
            WatchUi.switchToView(new MainMenuView(), new MainMenuDelegate(), WatchUi.SLIDE_IMMEDIATE);
        }
    }
}
