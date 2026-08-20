import ipaddress

def hosts_to_prefix(host_count):
    """
    Given a number of required hosts, return the smallest subnet
    prefix length (CIDR) that fits them.
    Formula: we need enough host bits so that 2^bits - 2 >= host_count
    (the -2 accounts for network + broadcast addresses).
    """
    needed = host_count + 2
    host_bits = 0
    while (2 ** host_bits) < needed:
        host_bits += 1
    prefix_length = 32 - host_bits
    return prefix_length


def plan_vlsm(base_network, departments):
    """
    base_network: string like '192.168.1.0/24'
    departments: list of (name, host_count) tuples
    Returns a list of dicts with subnet details per department.
    """
    # Sort largest host count first — required for VLSM to pack efficiently
    departments = sorted(departments, key=lambda d: d[1], reverse=True)

    network = ipaddress.ip_network(base_network)
    available = list(network.subnets(new_prefix=32))  # placeholder, replaced below
    results = []
    next_addr = network.network_address

    for name, hosts in departments:
        prefix = hosts_to_prefix(hosts)
        subnet = ipaddress.ip_network((next_addr, prefix), strict=False)
        results.append({
            "name": name,
            "hosts_needed": hosts,
            "subnet": subnet,
            "prefix": prefix,
            "usable_first": subnet.network_address + 1,
            "usable_last": subnet.broadcast_address - 1,
            "broadcast": subnet.broadcast_address,
        })
        # Move to the next available address block
        next_addr = subnet.broadcast_address + 1

    return results

def print_report(results):
    print(f"{'Department':<15}{'Hosts Needed':<15}{'Network':<20}{'Usable Range':<35}{'Broadcast':<15}")
    print("-" * 100)
    for r in results:
        usable_range = f"{r['usable_first']} - {r['usable_last']}"
        print(f"{r['name']:<15}{r['hosts_needed']:<15}{str(r['subnet']):<20}{usable_range:<35}{str(r['broadcast']):<15}")

def generate_cisco_config(results, interface="GigabitEthernet0/0"):
    config_lines = []
    vlan_id = 10
    for r in results:
        gateway_ip = r["usable_first"]
        subnet_mask = r["subnet"].netmask
        dhcp_start = r["usable_first"] + 1
        dhcp_end = r["usable_last"]

        config_lines.append(f"! --- {r['name']} (VLAN {vlan_id}) ---")
        config_lines.append(f"interface {interface}.{vlan_id}")
        config_lines.append(f" encapsulation dot1Q {vlan_id}")
        config_lines.append(f" ip address {gateway_ip} {subnet_mask}")
        config_lines.append("")
        config_lines.append(f"ip dhcp pool {r['name']}")
        config_lines.append(f" network {r['subnet'].network_address} {subnet_mask}")
        config_lines.append(f" default-router {gateway_ip}")
        config_lines.append(f" dns-server 8.8.8.8")
        config_lines.append("")
        vlan_id += 10
    return "\n".join(config_lines)

if __name__ == "__main__":
    departments = [
        ("Sales", 50),
        ("Engineering", 25),
        ("HR", 10),
        ("Guest_WiFi", 5),
    ]
    base_network = "192.168.1.0/24"

    results = plan_vlsm(base_network, departments)
    print_report(results)
    
    print("\n\n===== CISCO ROUTER CONFIG =====\n")
    print(generate_cisco_config(results))

