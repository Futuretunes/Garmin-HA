// Root menu showing entity domain categories

using Toybox.WatchUi;
using Toybox.Graphics;

class MainMenuView extends WatchUi.Menu2 {

    function initialize() {
        Menu2.initialize({:title => "Garmin HA"});

        addItem(new MenuItem("Lights", null, :lights, null));
        addItem(new MenuItem("Switches", null, :switches, null));
        addItem(new MenuItem("Climate", null, :climate, null));
        addItem(new MenuItem("Locks", null, :locks, null));
        addItem(new MenuItem("Sensors", null, :sensors, null));
        addItem(new MenuItem("Scenes", null, :scenes, null));
        addItem(new MenuItem("Scripts", null, :scripts, null));
    }
}

class MainMenuDelegate extends WatchUi.Menu2InputDelegate {

    function initialize() {
        Menu2InputDelegate.initialize();
    }

    function onSelect(item as MenuItem) as Void {
        var id = item.getId();
        var domain = _getDomain(id);

        if (domain != null) {
            WatchUi.pushView(
                new LoadingView("Loading..."),
                new LoadingDelegate(),
                WatchUi.SLIDE_LEFT
            );
            HAClient.getStates(domain, method(:onStatesReceived));
            _currentDomain = domain;
        }
    }

    var _currentDomain as String?;

    function onStatesReceived(responseCode as Number, data as Dictionary or Null) as Void {
        if (responseCode == 200 && data != null && data["s"] == 1) {
            var entities = data["e"] as Array;
            if (entities.size() > 0) {
                WatchUi.switchToView(
                    new EntityListView(entities, _currentDomain),
                    new EntityListDelegate(entities, _currentDomain),
                    WatchUi.SLIDE_LEFT
                );
            } else {
                WatchUi.switchToView(
                    new ErrorView("No entities found"),
                    new ErrorDelegate(),
                    WatchUi.SLIDE_LEFT
                );
            }
        } else {
            var msg = "Connection error";
            if (responseCode == -104) {
                msg = "Phone not connected";
            } else if (responseCode == -402) {
                msg = "Response too large";
            } else if (responseCode < 0) {
                msg = "Network error\n(" + responseCode + ")";
            } else if (responseCode >= 400) {
                msg = "Server error\n(" + responseCode + ")";
            }
            WatchUi.switchToView(
                new ErrorView(msg),
                new ErrorDelegate(),
                WatchUi.SLIDE_LEFT
            );
        }
    }

    function _getDomain(id as Symbol) as String? {
        switch (id) {
            case :lights:   return Constants.DOMAIN_LIGHT;
            case :switches: return Constants.DOMAIN_SWITCH;
            case :climate:  return Constants.DOMAIN_CLIMATE;
            case :locks:    return Constants.DOMAIN_LOCK;
            case :sensors:  return Constants.DOMAIN_SENSOR;
            case :scenes:   return Constants.DOMAIN_SCENE;
            case :scripts:  return Constants.DOMAIN_SCRIPT;
        }
        return null;
    }
}
