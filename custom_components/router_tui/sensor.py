from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        RouterHostsSensor(coordinator),
    ]
    
    async_add_entities(entities)

class RouterHostsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Router Connected Hosts"
        self._attr_unique_id = f"router_hosts_sensor"

    @property
    def native_value(self):
        hosts = self.coordinator.data.get("hosts", [])
        return len(hosts)
        
    @property
    def extra_state_attributes(self):
        return {
            "all_hosts": self.coordinator.data.get("hosts", [])
        }
