from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .client import RouterClient

_LOGGER = logging.getLogger(__name__)

class RouterDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, client: RouterClient):
        super().__init__(
            hass,
            _LOGGER,
            name="Router Data",
            update_interval=timedelta(seconds=60),
        )
        self.client = client

    async def _async_update_data(self):
        try:
            home_data = await self.client.get_home_data()
            if not home_data:
                # Attempt to re-login if session expired
                await self.client.login()
                home_data = await self.client.get_home_data()

            hosts = await self.client.get_hosts()
            return {
                "home": home_data,
                "hosts": hosts,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
