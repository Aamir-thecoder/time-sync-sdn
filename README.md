# time-sync-sdn
# Network Time Synchronization System (Team 4)

## Project Overview
This project implements a custom UDP-based time synchronization protocol. Clients calculate round-trip delays and clock offsets to align their time with a reference server. The system is deployed within a Mininet emulated network and managed by a POX SDN controller.

## Team Members
* Aamir Syed (PES2UG25CS007)
* Aarush vishwanath calamuri (PES2UG25CS011)
* Abhiveer verma (PES2UG25CS024)

## System Architecture
* **Protocol:** UDP Sockets (No external APIs utilized)
* **Network Emulation:** Mininet
* **Control Plane:** POX SDN Controller (l2_learning module)
* **Topology:** 1 Server and 2 Clients connected to an Open vSwitch (OVS). Links are configured with controlled latency (10ms, 20ms, and 50ms) to test synchronization math under simulated network lag.

## How to Run the Project
1. Start the POX Controller in Terminal 1:
   `python3 pox/pox.py forwarding.l2_learning`
2. Start the Mininet Topology in Terminal 2:
   `sudo python3 topology.py`
3. Execute the server in the Mininet CLI:
   `mininet> server python3 server.py &`
4. Execute the client in the Mininet CLI:
   `mininet> client1 python3 client.py 10.0.0.1`

## Evaluation Results
The system accurately calculates network latency. When querying the server from Client 1 (20ms link + 10ms server link = 60ms expected round-trip physical delay), the socket application calculated a Round-Trip Delay of 67.402ms, accounting for exact wire latency plus local processing time.
