from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

ROUTER_DEVICE_INFO = DeviceInfo(
    identifiers={(DOMAIN, "sagemcom_router")},
    name="Sagemcom F@st Router",
    manufacturer="Sagemcom",
    model="F@st Router",
)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        RouterHostsSensor(coordinator),
        RouterMeshSensor(coordinator),
        RouterEndpointsSensor(coordinator),
        RouterNatRulesSensor(coordinator),
        RouterStaticLeasesSensor(coordinator),
        RouterWifi24Sensor(coordinator),
        RouterWifi5Sensor(coordinator),
        RouterWifi24DataSentSensor(coordinator),
        RouterWifi24DataReceivedSensor(coordinator),
        RouterWifi5DataSentSensor(coordinator),
        RouterWifi5DataReceivedSensor(coordinator),
        RouterExternalIPSensor(coordinator),
        RouterWifi24ClientsSensor(coordinator),
        RouterWifi5ClientsSensor(coordinator),
        RouterSerialNumberSensor(coordinator),
        RouterSoftwareVersionSensor(coordinator),
        RouterUptimeSensor(coordinator),
        RouterLocalIpSensor(coordinator),
        RouterCpuLoadSensor(coordinator),
        RouterMemoryUsageSensor(coordinator),
        RouterPrimaryDnsSensor(coordinator),
        RouterSecondaryDnsSensor(coordinator)
    ]
    
    async_add_entities(entities)

class RouterHostsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Connected Hosts"
        self._attr_unique_id = "router_hosts_sensor"
        self._attr_device_info = ROUTER_DEVICE_INFO

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
        self._attr_name = "Mesh Nodes"
        self._attr_unique_id = "router_mesh_sensor"
        self._attr_device_info = ROUTER_DEVICE_INFO

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
        self._attr_name = "Advanced Endpoints"
        self._attr_unique_id = "router_advanced_endpoints"
        self._attr_device_info = ROUTER_DEVICE_INFO

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
        self._attr_name = "Port Forwarding Rules"
        self._attr_unique_id = "router_port_forwarding"
        self._attr_icon = "mdi:port"
        self._attr_device_info = ROUTER_DEVICE_INFO

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
        self._attr_name = "Static DHCP Leases"
        self._attr_unique_id = "router_static_leases"
        self._attr_icon = "mdi:ip-network"
        self._attr_device_info = ROUTER_DEVICE_INFO

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
        self._attr_name = "2.4GHz Wi-Fi Status"
        self._attr_unique_id = "router_wifi_24"
        self._attr_icon = "mdi:wifi"
        self._attr_device_info = ROUTER_DEVICE_INFO

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
        self._attr_name = "5GHz Wi-Fi Status"
        self._attr_unique_id = "router_wifi_5"
        self._attr_icon = "mdi:wifi-strength-4"
        self._attr_device_info = ROUTER_DEVICE_INFO

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

def extract_bytes(data: dict, keys: list) -> int:
    def _search(d):
        if not isinstance(d, dict): return None
        for k, v in d.items():
            if str(k).lower() in keys:
                try: return int(v)
                except: pass
            if isinstance(v, dict):
                res = _search(v)
                if res is not None: return res
        return None
    res = _search(data)
    return res if res else 0

class RouterWifi24DataSentSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "2.4GHz Upload (Sent) Data"
        self._attr_unique_id = "router_wifi_24_sent"
        self._attr_icon = "mdi:upload-network"
        self._attr_device_class = "data_size"
        self._attr_native_unit_of_measurement = "B"
        self._attr_device_info = ROUTER_DEVICE_INFO

    @property
    def native_value(self):
        stats = self.coordinator.data.get("all_endpoints", {}).get("wifi_24_stats", {})
        return extract_bytes(stats, ["rxbytes", "bytesreceived"])

class RouterWifi24DataReceivedSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "2.4GHz Download (Received) Data"
        self._attr_unique_id = "router_wifi_24_recv"
        self._attr_icon = "mdi:download-network"
        self._attr_device_class = "data_size"
        self._attr_native_unit_of_measurement = "B"
        self._attr_device_info = ROUTER_DEVICE_INFO

    @property
    def native_value(self):
        stats = self.coordinator.data.get("all_endpoints", {}).get("wifi_24_stats", {})
        return extract_bytes(stats, ["txbytes", "bytessent"])

class RouterWifi5DataSentSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "5GHz Upload (Sent) Data"
        self._attr_unique_id = "router_wifi_5_sent"
        self._attr_icon = "mdi:upload-network"
        self._attr_device_class = "data_size"
        self._attr_native_unit_of_measurement = "B"
        self._attr_device_info = ROUTER_DEVICE_INFO

    @property
    def native_value(self):
        stats = self.coordinator.data.get("all_endpoints", {}).get("wifi_5_stats", {})
        return extract_bytes(stats, ["rxbytes", "bytesreceived"])

class RouterWifi5DataReceivedSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "5GHz Download (Received) Data"
        self._attr_unique_id = "router_wifi_5_recv"
        self._attr_icon = "mdi:download-network"
        self._attr_device_class = "data_size"
        self._attr_native_unit_of_measurement = "B"
        self._attr_device_info = ROUTER_DEVICE_INFO

    @property
    def native_value(self):
        stats = self.coordinator.data.get("all_endpoints", {}).get("wifi_5_stats", {})
        return extract_bytes(stats, ["txbytes", "bytessent"])

class RouterExternalIPSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Public IP / WAN IP"
        self._attr_unique_id = "router_external_ip"
        self._attr_icon = "mdi:web"
        self._attr_device_info = ROUTER_DEVICE_INFO

    @property
    def native_value(self):
        endpoints = self.coordinator.data.get("all_endpoints", {})
        
        # 1. Try 'open' endpoint (used by app.py)
        open_data = endpoints.get("open")
        if open_data and isinstance(open_data, list) and len(open_data) > 0 and isinstance(open_data[0], dict):
            ip = open_data[0].get("wan_ipv4")
            if ip and ip != "N/A":
                return ip

        # 2. Fallback to others
        for ep in ["connection", "wan", "deviceinfo"]:
            data = endpoints.get(ep, {})
            if isinstance(data, dict):
                ip = str(data.get("ipaddress") or data.get("IPAddress") or "")
                if ip and not ip.startswith("192.168.") and not ip.startswith("10.") and not ip.startswith("172."):
                    return ip
                for k, v in data.items():
                    if isinstance(v, dict):
                        ip = str(v.get("ipaddress") or v.get("IPAddress") or "")
                        if ip and not ip.startswith("192.168.") and not ip.startswith("10.") and not ip.startswith("172."):
                            return ip
        return "Unknown"

class RouterWifi24ClientsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "2.4GHz Connected Devices"
        self._attr_unique_id = "router_wifi_24_clients"
        self._attr_icon = "mdi:devices"
        self._attr_device_info = ROUTER_DEVICE_INFO

    def _get_clients(self):
        clients = []
        wireless_list = self.coordinator.data.get("home", {}).get("wirelessListDevice", [])
        for dev in wireless_list:
            links = dev.get("linkDevices", [])
            for link in links:
                if str(link.get("band", "")).startswith("2.4"):
                    clients.append(dev)
                    break
        return clients

    @property
    def native_value(self):
        return len(self._get_clients())

    @property
    def extra_state_attributes(self):
        return {"devices": self._get_clients()}

class RouterWifi5ClientsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "5GHz Connected Devices"
        self._attr_unique_id = "router_wifi_5_clients"
        self._attr_icon = "mdi:devices"
        self._attr_device_info = ROUTER_DEVICE_INFO

    def _get_clients(self):
        clients = []
        wireless_list = self.coordinator.data.get("home", {}).get("wirelessListDevice", [])
        for dev in wireless_list:
            links = dev.get("linkDevices", [])
            for link in links:
                if str(link.get("band", "")).startswith("5"):
                    clients.append(dev)
                    break
        return clients

    @property
    def native_value(self):
        return len(self._get_clients())

    @property
    def extra_state_attributes(self):
        return {"devices": self._get_clients()}

class RouterSerialNumberSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Serial Number"
        self._attr_unique_id = "router_serial_number"
        self._attr_icon = "mdi:barcode"
        self._attr_device_info = ROUTER_DEVICE_INFO

    @property
    def native_value(self):
        open_data = self.coordinator.data.get("all_endpoints", {}).get("open")
        if open_data and isinstance(open_data, list) and len(open_data) > 0 and isinstance(open_data[0], dict):
            return open_data[0].get("serial_number", "Unknown")
        return "Unknown"

class RouterSoftwareVersionSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Software Version"
        self._attr_unique_id = "router_software_version"
        self._attr_icon = "mdi:update"
        self._attr_device_info = ROUTER_DEVICE_INFO

    @property
    def native_value(self):
        open_data = self.coordinator.data.get("all_endpoints", {}).get("open")
        if open_data and isinstance(open_data, list) and len(open_data) > 0 and isinstance(open_data[0], dict):
            return open_data[0].get("internal_firmware_version", open_data[0].get("firmware", "Unknown"))
        return "Unknown"

class RouterUptimeSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Uptime"
        self._attr_unique_id = "router_uptime"
        self._attr_icon = "mdi:clock-outline"
        self._attr_device_info = ROUTER_DEVICE_INFO
        self._attr_device_class = "duration"
        self._attr_native_unit_of_measurement = "s"

    @property
    def native_value(self):
        open_data = self.coordinator.data.get("all_endpoints", {}).get("open")
        if open_data and isinstance(open_data, list) and len(open_data) > 0 and isinstance(open_data[0], dict):
            try:
                return int(open_data[0].get("uptime", 0))
            except:
                pass
        return None

class RouterLocalIpSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Local IPv4 Address"
        self._attr_unique_id = "router_local_ipv4"
        self._attr_icon = "mdi:ip-network"
        self._attr_device_info = ROUTER_DEVICE_INFO

    @property
    def native_value(self):
        open_data = self.coordinator.data.get("all_endpoints", {}).get("open")
        if open_data and isinstance(open_data, list) and len(open_data) > 0 and isinstance(open_data[0], dict):
            return open_data[0].get("gateway_ip", "Unknown")
        return "Unknown"

class RouterCpuLoadSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "CPU load (%)"
        self._attr_unique_id = "router_cpu_load"
        self._attr_icon = "mdi:cpu-64-bit"
        self._attr_device_info = ROUTER_DEVICE_INFO

    @property
    def native_value(self):
        return "Unknown"

class RouterMemoryUsageSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Memory usage (%)"
        self._attr_unique_id = "router_memory_usage"
        self._attr_icon = "mdi:memory"
        self._attr_device_info = ROUTER_DEVICE_INFO

    @property
    def native_value(self):
        return "Unknown"

class RouterPrimaryDnsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Primary DNS Server"
        self._attr_unique_id = "router_primary_dns"
        self._attr_icon = "mdi:dns"
        self._attr_device_info = ROUTER_DEVICE_INFO

    @property
    def native_value(self):
        data = self.coordinator.data.get("all_endpoints", {}).get("dns_v4")
        try:
            if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                dns = data[0].get("DNS", {})
                mode = dns.get("dnsMode", "DYNAMIC")
                if mode == "DYNAMIC":
                    dyn = dns.get("dynamic", [])
                    s = dyn[0].get("server", "") if (dyn and isinstance(dyn, list) and isinstance(dyn[0], dict)) else ""
                else:
                    s = dns.get("static", {}).get("servers", "")
                servers = [x.strip() for x in s.split(",") if x.strip()]
                return servers[0] if len(servers) > 0 else "Unknown"
        except:
            pass
        return "Unknown"

class RouterSecondaryDnsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Secondary DNS Server"
        self._attr_unique_id = "router_secondary_dns"
        self._attr_icon = "mdi:dns"
        self._attr_device_info = ROUTER_DEVICE_INFO

    @property
    def native_value(self):
        data = self.coordinator.data.get("all_endpoints", {}).get("dns_v4")
        try:
            if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                dns = data[0].get("DNS", {})
                mode = dns.get("dnsMode", "DYNAMIC")
                if mode == "DYNAMIC":
                    dyn = dns.get("dynamic", [])
                    s = dyn[0].get("server", "") if (dyn and isinstance(dyn, list) and isinstance(dyn[0], dict)) else ""
                else:
                    s = dns.get("static", {}).get("servers", "")
                servers = [x.strip() for x in s.split(",") if x.strip()]
                return servers[1] if len(servers) > 1 else "Unknown"
        except:
            pass
        return "Unknown"
