import ipaddress

def is_same_subnet(ip1, ip2, subnet_mask='255.255.255.0'):
    net1 = ipaddress.IPv4Network(f"{ip1}/{subnet_mask}", strict=False)
    net2 = ipaddress.IPv4Network(f"{ip2}/{subnet_mask}", strict=False)
    return net1.network_address == net2.network_address
