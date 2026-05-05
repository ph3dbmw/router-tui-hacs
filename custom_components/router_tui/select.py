from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RouterFirewallSelect(coordinator)])

class RouterFirewallSelect(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Router Firewall Level"
        self._attr_unique_id = "router_firewall_select"
        self._attr_options = ["Low", "Medium", "High"]
        self._attr_icon = "mdi:wall-fire"

    @property
    def current_option(self):
        firewall = self.coordinator.data.get("firewall", {})
        if not firewall:
            return "Medium"
        level = firewall.get("firewall", {}).get("level", 2)
        if level == 1: return "Low"
        if level == 2: return "Medium"
        if level == 3: return "High"
        return "Medium"

    async def async_select_option(self, option: str):
        level_map = {"Low": 1, "Medium": 2, "High": 3}
        await self.coordinator.client.put_setting("firewall", {"level": level_map[option]}, version="v2")
        await self.coordinator.async_request_refresh()
