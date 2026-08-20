# VLSM Subnet Planner and Cisco Configuration Generator

A Python tool that calculates Variable Length Subnet Masking (VLSM) allocations and generates matching Cisco router-on-a-stick and DHCP configuration.

## The problem

Giving every department the same subnet size wastes IPv4 addresses. VLSM solves this by assigning each department the smallest subnet that satisfies its host requirement.

This tool:

- Sorts departments from largest to smallest.
- Calculates the smallest suitable CIDR prefix.
- Allocates consecutive, non-overlapping subnets.
- Displays the usable host range and broadcast address.
- Generates Cisco subinterface and DHCP pool configuration.

## Example scenario

The included example divides `192.168.1.0/24` among four departments:

| Department | Hosts required | Allocated subnet | Usable range | Broadcast |
|---|---:|---|---|---|
| Sales | 50 | `192.168.1.0/26` | `192.168.1.1–192.168.1.62` | `192.168.1.63` |
| Engineering | 25 | `192.168.1.64/27` | `192.168.1.65–192.168.1.94` | `192.168.1.95` |
| HR | 10 | `192.168.1.96/28` | `192.168.1.97–192.168.1.110` | `192.168.1.111` |
| Guest Wi-Fi | 5 | `192.168.1.112/29` | `192.168.1.113–192.168.1.118` | `192.168.1.119` |

## How the calculation works

For each department, the program finds enough host bits to satisfy:

```text
2^host_bits - 2 >= required_hosts
```

The two subtracted addresses are the network and broadcast addresses. The prefix length is:

```text
prefix_length = 32 - host_bits
```

Departments are allocated from largest to smallest so that larger address blocks are placed first and the available space is used efficiently.

## Requirements

- Python 3.8 or later
- No third-party packages

The program uses Python's built-in `ipaddress` module.

## Run the project

```bash
python3 vlsm_planner.py
```

The program prints the subnet plan followed by Cisco IOS configuration.

## Customize the input

Edit the values at the bottom of `vlsm_planner.py`:

```python
departments = [
    ("Sales", 50),
    ("Engineering", 25),
    ("HR", 10),
    ("Guest_WiFi", 5),
]

base_network = "192.168.1.0/24"
```

Replace the names, host counts, or base network with the requirements for your own design.

## Example Cisco output

```cisco
! --- Sales (VLAN 10) ---
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.1.1 255.255.255.192

ip dhcp pool Sales
 network 192.168.1.0 255.255.255.192
 default-router 192.168.1.1
 dns-server 8.8.8.8
```

The first usable address becomes the VLAN gateway. VLAN IDs begin at 10 and increase by 10 for each department.

## Functions

| Function | Purpose |
|---|---|
| `hosts_to_prefix()` | Finds the smallest CIDR prefix for a host requirement |
| `plan_vlsm()` | Sorts and allocates the department subnets |
| `print_report()` | Prints the formatted addressing table |
| `generate_cisco_config()` | Generates Cisco subinterface and DHCP configuration |

## Verification

Confirm the generated plan before deploying it:

- Each subnet is inside the chosen base network.
- No subnets overlap.
- Each subnet supports the requested number of hosts.
- Gateway addresses match the Cisco subinterface configuration.
- VLAN IDs match the switch configuration.

Useful Cisco commands after applying the configuration:

```cisco
show ip interface brief
show ip dhcp pool
show ip dhcp binding
show running-config | section interface
show running-config | section dhcp
```

## Current limitations

- Input values are edited directly in the Python file.
- The script currently targets IPv4.
- It does not write the results to CSV or a configuration file.
- The generated configuration assumes router-on-a-stick using one physical interface.
- Results should be reviewed before use in a production network.

## What this demonstrates

- IPv4 subnetting and VLSM
- CIDR prefix calculation
- Network, usable-host, and broadcast address calculation
- Efficient subnet allocation
- Python automation with the `ipaddress` module
- Cisco router subinterfaces
- DHCP pool generation
