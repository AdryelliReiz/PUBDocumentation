def is_same_subnet(ip1, ip2):
    return ip1.split('.')[:3] == ip2.split('.')[:3]