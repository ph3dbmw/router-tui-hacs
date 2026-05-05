from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        RouterHostsSensor(coordinator),
        RouterMeshSensor(coordinator),
        RouterEndpointsSensor(coordinator),
        RouterNatRulesSensor(coordinator),
        RouterStaticLeasesSensor(coordinator),
        RouterWifi24Sensor(coordinator),
        RouterWifi5Sensor(coordinator)
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

class RouterEndpointsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Router Advanced Endpoints"
        self._attr_unique_id = "router_advanced_endpoints"

    @property
    def native_value(self):
        endpoints = self.coordinator.data.get("all_endpoints", {})
        return f"{len(endpoints)} Active Endpoints"
        
    @property
    def extra_state_attributes(self):
        return self.coordinator.data.get("all_endpoints", {})

class RouterNatRulesSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Router Port Forwarding Rules"
        self._attr_unique_id = "router_port_forwarding"
        self._attr_icon = "mdi:port"

    @property
    def native_value(self):
        rules = self.coordinator.data.get("all_endpoints", {}).get("nat_rules", [])
        if isinstance(rules, list):
            # Sometimes it's a list, sometimes dict with 'list' key
            return len(rules)
        if isinstance(rules, dict):
            rules_list = rules.get("nat", {}).get("portforwarding", {}).get("list", [])
            return len(rules_list)
        return 0
        
    @property
    def extra_state_attributes(self):
        return self.coordinator.data.get("all_endpoints", {}).get("nat_rules", {})

class RouterStaticLeasesSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Router Static DHCP Leases"
        self._attr_unique_id = "router_static_leases"
        self._attr_icon = "mdi:ip-network"

    @property
    def native_value(self):
        leases = self.coordinator.data.get("all_endpoints", {}).get("static_leases", {})
        if isinstance(leases, dict):
            l = leases.get("dhcp", {}).get("clients", {}).get("list", [])
            return len(l)
        return 0

class RouterWifi24Sensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Router 2.4GHz Wi-Fi Status"
        self._attr_unique_id = "router_wifi_24"
        self._attr_icon = "mdi:wifi"

    @property
    def native_value(self):
        home = self.coordinator.data.get("home", {})
        ssids = home.get("ssids", [])
        for s in ssids:
            if s.get("radio") == "2_4GHZ" and s.get("type") == "Primary":
                return s.get("ssidStatus", "Unknown")
        return "Unknown"
        
    @property
    def extra_state_attributes(self):
        home = self.coordinator.data.get("home", {})
        for s in home.get("ssids", []):
            if s.get("radio") == "2_4GHZ" and s.get("type") == "Primary":
                return s
        return {}

class RouterWifi5Sensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Router 5GHz Wi-Fi Status"
        self._attr_unique_id = "router_wifi_5"
        self._attr_icon = "mdi:wifi-strength-4"

    @property
    def native_value(self):
        home = self.coordinator.data.get("home", {})
        ssids = home.get("ssids", [])
        for s in ssids:
            if s.get("radio") == "5GHZ" and s.get("type") == "Primary":
                return s.get("ssidStatus", "Unknown")
        return "Unknown"
        
    @property
    def extra_state_attributes(self):
        home = self.coordinator.data.get("home", {})
        for s in home.get("ssids", []):
            if s.get("radio") == "5GHZ" and s.get("type") == "Primary":
                return s
        return {}
