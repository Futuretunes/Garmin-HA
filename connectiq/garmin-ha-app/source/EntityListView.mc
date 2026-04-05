// Entity list view within a domain

using Toybox.WatchUi;
using Toybox.Graphics;

class EntityListView extends WatchUi.Menu2 {

    function initialize(entities as Array, domain as String?) {
        var title = domain != null ? _domainTitle(domain) : "Entities";
        Menu2.initialize({:title => title});

        for (var i = 0; i < entities.size(); i++) {
            var entity = entities[i] as Dictionary;
            var name = entity["n"] as String;
            var state = entity["s"] as String;
            var entityId = entity["i"] as String;

            addItem(new MenuItem(
                name,
                _formatState(state, domain),
                entityId,
                null
            ));
        }
    }

    function _domainTitle(domain as String) as String {
        if (domain.equals("light")) { return "Lights"; }
        if (domain.equals("switch")) { return "Switches"; }
        if (domain.equals("climate")) { return "Climate"; }
        if (domain.equals("lock")) { return "Locks"; }
        if (domain.equals("sensor")) { return "Sensors"; }
        if (domain.equals("scene")) { return "Scenes"; }
        if (domain.equals("script")) { return "Scripts"; }
        return domain;
    }

    function _formatState(state as String, domain as String?) as String {
        if (domain != null && domain.equals("lock")) {
            return state.equals("locked") ? "Locked" : "Unlocked";
        }
        if (state.equals("on")) { return "On"; }
        if (state.equals("off")) { return "Off"; }
        if (state.equals("unavailable")) { return "Unavailable"; }
        return state;
    }
}

class EntityListDelegate extends WatchUi.Menu2InputDelegate {

    var _entities as Array;
    var _domain as String?;

    function initialize(entities as Array, domain as String?) {
        Menu2InputDelegate.initialize();
        _entities = entities;
        _domain = domain;
    }

    function onSelect(item as MenuItem) as Void {
        var entityId = item.getId() as String;
        var currentState = _getEntityState(entityId);

        if (_domain != null && Constants.isToggleable(_domain)) {
            // Toggle the entity
            var service = Constants.getToggleService(_domain, currentState);
            HAClient.callService(_domain, service, entityId, method(:onServiceResponse));
            _lastSelectedItem = item;
            _lastEntityId = entityId;
        } else {
            // Show detail view for non-toggleable entities
            var entity = _findEntity(entityId);
            if (entity != null) {
                WatchUi.pushView(
                    new EntityDetailView(entity, _domain),
                    new EntityDetailDelegate(entity, _domain),
                    WatchUi.SLIDE_LEFT
                );
            }
        }
    }

    var _lastSelectedItem as MenuItem?;
    var _lastEntityId as String?;

    function onServiceResponse(responseCode as Number, data as Dictionary or Null) as Void {
        if (responseCode == 200 && data != null && data["s"] == 1) {
            // Update the menu item subtitle with new state
            var newState = data["ns"];
            if (newState != null && _lastSelectedItem != null) {
                _lastSelectedItem.setSubLabel(_formatNewState(newState));
            }
        }
        // Refresh the entity list
        if (_domain != null) {
            HAClient.getStates(_domain, method(:onRefreshReceived));
        }
    }

    function onRefreshReceived(responseCode as Number, data as Dictionary or Null) as Void {
        if (responseCode == 200 && data != null && data["s"] == 1) {
            _entities = data["e"] as Array;
            WatchUi.switchToView(
                new EntityListView(_entities, _domain),
                new EntityListDelegate(_entities, _domain),
                WatchUi.SLIDE_IMMEDIATE
            );
        }
    }

    function _getEntityState(entityId as String) as String {
        var entity = _findEntity(entityId);
        if (entity != null) {
            return entity["s"] as String;
        }
        return "unknown";
    }

    function _findEntity(entityId as String) as Dictionary? {
        for (var i = 0; i < _entities.size(); i++) {
            var entity = _entities[i] as Dictionary;
            if ((entity["i"] as String).equals(entityId)) {
                return entity;
            }
        }
        return null;
    }

    function _formatNewState(state as String) as String {
        if (state.equals("on")) { return "On"; }
        if (state.equals("off")) { return "Off"; }
        if (state.equals("locked")) { return "Locked"; }
        if (state.equals("unlocked")) { return "Unlocked"; }
        return state;
    }
}
