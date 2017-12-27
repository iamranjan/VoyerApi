PROPERTIES = {
    "mode": "DEV", # change this to PROD to switch to using inventory hostname for management instead of tunnel
    "layer": "PIPELINE Network",
    "gateway": "vsec",
    "policy_package": "PIPELINE",
    "external_network": ["NET2"],
    "internal_network": ["VM_NETWORK", "FP", "VM_MGMT"],
    "username": "admin",
    "password": "admin123"

}
