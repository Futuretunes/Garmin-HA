// Constants for Garmin HA app

module Constants {
    // Domain mappings
    const DOMAIN_LIGHT = "light";
    const DOMAIN_SWITCH = "switch";
    const DOMAIN_CLIMATE = "climate";
    const DOMAIN_LOCK = "lock";
    const DOMAIN_SENSOR = "sensor";
    const DOMAIN_SCENE = "scene";
    const DOMAIN_SCRIPT = "script";

    // Webhook actions
    const ACTION_GET_STATES = "get_states";
    const ACTION_CALL_SERVICE = "call_service";
    const ACTION_GET_DASHBOARD = "get_dashboard";

    // Colors (AMOLED optimized)
    const COLOR_ON = 0x00FF00;       // Green
    const COLOR_OFF = 0x888888;      // Grey
    const COLOR_LOCKED = 0xFF0000;   // Red
    const COLOR_UNLOCKED = 0x00FF00; // Green
    const COLOR_ERROR = 0xFF4444;    // Light red
    const COLOR_LOADING = 0x4488FF;  // Blue
    const COLOR_BG = 0x000000;       // Black (AMOLED)
    const COLOR_TEXT = 0xFFFFFF;     // White
    const COLOR_SUBTITLE = 0xAAAAAA; // Light grey

    // Toggleable domains
    function isToggleable(domain as String) as Boolean {
        return domain.equals(DOMAIN_LIGHT) ||
               domain.equals(DOMAIN_SWITCH) ||
               domain.equals(DOMAIN_LOCK) ||
               domain.equals(DOMAIN_SCENE) ||
               domain.equals(DOMAIN_SCRIPT);
    }

    // Get the toggle service for a domain
    function getToggleService(domain as String, currentState as String) as String {
        if (domain.equals(DOMAIN_LOCK)) {
            return currentState.equals("locked") ? "unlock" : "lock";
        }
        if (domain.equals(DOMAIN_SCENE) || domain.equals(DOMAIN_SCRIPT)) {
            return "turn_on";
        }
        return "toggle";
    }
}
