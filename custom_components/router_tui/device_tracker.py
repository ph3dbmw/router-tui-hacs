from homeassistant.components.device_tracker import ScannerEntity, SourceType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    hosts = coordinator.data.get("hosts", [])
    entities = []
    for host in hosts:
        mac = host.get("macaddress") or host.get("MACAddress")
        if mac:
            entities.append(RouterDeviceTracker(coordinator, host))
            
    async_add_entities(entities)

class RouterDeviceTracker(CoordinatorEntity, ScannerEntity):
    def __init__(self, coordinator, host_data):
        super().__init__(coordinator)
        self.host_data = host_data
        self._mac = self.host_data.get("macaddress") or self.host_data.get("MACAddress")
        self._attr_unique_id = f"router_tui_{self._mac}"
        
    @property
    def name(self):
        return self.host_data.get("hostname") or self.host_data.get("HostName") or f"Device {self._mac}"
        
    @property
    def mac_address(self):
        return self._mac
        
    @property
    def ip_address(self):
        return self.host_data.get("ipaddress") or self.host_data.get("IPAddress")
        
    @property
    def source_type(self):
        return SourceType.ROUTER
        
    @property
    def is_connected(self):
        hosts = self.coordinator.data.get("hosts", [])
        for h in hosts:
            mac = h.get("macaddress") or h.get("MACAddress")
            if mac == self._mac:
                status = str(h.get("status") or h.get("Active") or "").lower()
                return status in ("active", "true", "1", "up")
        return False
