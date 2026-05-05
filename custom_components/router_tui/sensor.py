from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        RouterHostsSensor(coordinator),
        RouterFirewallSensor(coordinator),
        RouterGuestWifiSensor(coordinator),
        RouterMeshSensor(coordinator)
    ]
    
    async_add_entities(entities)

class RouterHostsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Router Connected Hosts"
        self._attr_unique_id = "router_hosts_sensor"

    @property
    def native_value(self):
        hosts = self.coordinator.data.get("hosts", [])
        return len(hosts)
        
    @property
    def extra_state_attributes(self):
        return {
            "all_hosts": self.coordinator.data.get("hosts", []),
            "home_data": self.coordinator.data.get("home", {})
        }

class RouterFirewallSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Router Firewall Level"
        self._attr_unique_id = "router_firewall_sensor"

    @property
    def native_value(self):
        firewall = self.coordinator.data.get("firewall", {})
        level = firewall.get("firewall", {}).get("level", "Unknown")
        return level

class RouterGuestWifiSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Router Guest Wi-Fi"
        self._attr_unique_id = "router_guest_wifi_sensor"

    @property
    def native_value(self):
        guest = self.coordinator.data.get("guest_wifi", {})
        status = guest.get("wireless", {}).get("guest", {}).get("settings", {}).get("ssidStatus", "Unknown")
        return status
        
    @property
    def extra_state_attributes(self):
        return self.coordinator.data.get("guest_wifi", {})

class RouterMeshSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Router Mesh Nodes"
        self._attr_unique_id = "router_mesh_sensor"

    @property
    def native_value(self):
        mesh = self.coordinator.data.get("mesh_nodes", [])
        return len(mesh)
        
    @property
    def extra_state_attributes(self):
        return {"nodes": self.coordinator.data.get("mesh_nodes", [])}
