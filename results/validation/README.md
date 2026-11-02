# Validation Evidence

This folder contains screenshots captured during the project's Mininet/POX validation.

## Connectivity (`connectivity/`)

- `mininet_connectivity.png`: Mininet host-to-switch port mapping and `pingall` output showing 0% packet loss (6/6 received).

## Synchronization (`synchronization/`)

- `udp_synchronization.png`: Successful UDP timestamp exchanges from Client 1 and Client 2, including RTT and estimated clock-offset outputs.

## Dynamic QoS (`dynamic_qos/`)

- `activation_recovery.png`: POX traffic-monitor output showing congestion detection, transition to ACTIVE, congestion clearing and return to NORMAL.
- `flow_rules.png`: OVS flow-table output showing the four high-priority UDP/9999 enqueue rules (priority 60000).
- `queue1_forwarding.png`: Client synchronization output together with OVS queue statistics showing synchronization packets in Queue 1 with zero Queue 1 errors during the captured test.

These screenshots document observed runs. Their displayed measurements are examples from those runs and are not guarantees for every machine or execution.
