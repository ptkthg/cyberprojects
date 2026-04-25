from __future__ import annotations


def generate_kql(ioc: str, ioc_type: str) -> str:
    if ioc_type == "ipv4":
        return (
            "DeviceNetworkEvents\n"
            f'| where RemoteIP == "{ioc}"\n'
            "| project Timestamp, DeviceName, InitiatingProcessAccountName, "
            "InitiatingProcessFileName, RemoteIP, RemotePort, ActionType"
        )

    if ioc_type in {"domain", "url"}:
        return (
            "DeviceNetworkEvents\n"
            f'| where RemoteUrl has "{ioc}"\n'
            "| project Timestamp, DeviceName, InitiatingProcessAccountName, "
            "InitiatingProcessFileName, RemoteUrl, RemoteIP, RemotePort, ActionType"
        )

    if ioc_type in {"md5", "sha1", "sha256"}:
        return (
            "DeviceFileEvents\n"
            f'| where SHA256 == "{ioc}" or SHA1 == "{ioc}" or MD5 == "{ioc}"\n'
            "| project Timestamp, DeviceName, InitiatingProcessAccountName, FileName, "
            "FolderPath, SHA256, SHA1, MD5, ActionType"
        )

    return "// IOC type not supported for automatic KQL generation"
