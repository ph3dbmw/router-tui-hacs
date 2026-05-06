from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN
import logging

ROUTER_DEVICE_INFO = DeviceInfo(
    identifiers={(DOMAIN, "sagemcom_router")},
    name="Sagemcom F@st Router",
    manufacturer="Sagemcom",
    model="F@st Router",
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        RouterBandSteeringSwitch(coordinator),
        RouterGuestWifiSwitch(coordinator),
        RouterUpnpSwitch(coordinator)
    ]
    
    async_add_entities(entities)

class RouterBandSteeringSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Band Steering"
        self._attr_unique_id = "router_band_steering"
        self._attr_icon = "mdi:router-wireless"
        self._attr_device_info = ROUTER_DEVICE_INFO
        
    @property
    def is_on(self):
        bs = self.coordinator.data.get("band_steering", {})
        if not bs:
            return False
        return bs.get("BandSteeringEnable") == "true"
        
    async def async_turn_on(self, **kwargs):
        await self.coordinator.client.set_band_steering(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.client.set_band_steering(False)
        await self.coordinator.async_request_refresh()
        
class RouterUpnpSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "UPnP"
        self._attr_unique_id = "router_upnp"
        self._attr_icon = "mdi:network"
        self._attr_device_info = ROUTER_DEVICE_INFO
        
    @property
    def is_on(self):
        upnp = self.coordinator.data.get("all_endpoints", {}).get("upnp", {})
        if not upnp:
            return False
        return upnp.get("upnp", {}).get("enable") == True or upnp.get("upnp", {}).get("enable") == "true"
        
    async def async_turn_on(self, **kwargs):
        await self.coordinator.client.put_setting("advanced/upnp", {"enable": "true"})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.client.put_setting("advanced/upnp", {"enable": "false"})
        await self.coordinator.async_request_refresh()

class RouterGuestWifiSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Guest Wi-Fi"
        self._attr_unique_id = "router_guest_wifi_switch"
        self._attr_icon = "mdi:wifi-account"
        self._attr_device_info = ROUTER_DEVICE_INFO
        
    @property
    def is_on(self):
        guest = self.coordinator.data.get("guest_wifi", {})
        if not guest:
            return False
        status = guest.get("wireless", {}).get("guest", {}).get("settings", {}).get("ssidStatus")
        return status == "UP"
        
    async def async_turn_on(self, **kwargs):
        guest = self.coordinator.data.get("guest_wifi", {})
        settings = guest.get("wireless", {}).get("guest", {}).get("settings", {}) if guest else {}
        payload = {
            "ssidName": settings.get("ssidName", "Guest"),
            "password": settings.get("password", ""),
            "ssidStatus": "UP"
        }
        await self.coordinator.client.post_setting("wireless/guest/settings", payload)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        guest = self.coordinator.data.get("guest_wifi", {})
        settings = guest.get("wireless", {}).get("guest", {}).get("settings", {}) if guest else {}
        payload = {
            "ssidName": settings.get("ssidName", "Guest"),
            "password": settings.get("password", ""),
            "ssidStatus": "DOWN"
        }
        await self.coordinator.client.post_setting("wireless/guest/settings", payload)
        await self.coordinator.async_request_refresh()
