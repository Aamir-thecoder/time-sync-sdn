# Classroom Demo Guide — Network Time Synchronization System

This guide is for a presenter who needs to demonstrate the project in a fixed order. It lists the terminal setup, commands to run, evidence to show, and short explanations for the evaluator.

## Before the demonstration — check and install prerequisites

Use the Ubuntu VM for the demonstration. The commands below check the required software first and install only missing Ubuntu packages.


### 1. Check Python, Git, Mininet, Open vSwitch and iperf3

Run this block in a normal Ubuntu terminal (not at the `mininet>` prompt):

```bash
missing=()

command -v python3 >/dev/null 2>&1 || missing+=(python3)
command -v git >/dev/null 2>&1 || missing+=(git)
command -v mn >/dev/null 2>&1 || missing+=(mininet)
command -v ovs-vsctl >/dev/null 2>&1 || missing+=(openvswitch-switch)
command -v ovs-ofctl >/dev/null 2>&1 || missing+=(openvswitch-switch)
command -v iperf3 >/dev/null 2>&1 || missing+=(iperf3)

# Remove duplicate package names from the missing list.
missing=($(printf '%s\n' "${missing[@]}" | awk 'NF && !seen[$0]++'))

if [ "${#missing[@]}" -gt 0 ]; then
    echo "Installing missing packages: ${missing[*]}"
    sudo apt update
    sudo apt install -y "${missing[@]}"
else
    echo "All required command-line tools are already installed."
fi
```

Check the installed versions/commands:

```bash
python3 --version
git --version
mn --version
ovs-vsctl --version 
ovs-ofctl --version 
iperf3 --version 
```

The Ubuntu packages used above are `mininet`, `openvswitch-switch` and `iperf3`; Mininet's installation guide also documents installing Mininet and starting Open vSwitch on Ubuntu/Debian. See the [Mininet installation guide](https://mininet.org/download/).


### 2. Check Open vSwitch service

Check whether Open vSwitch is running:

```bash
systemctl is-active openvswitch-switch
```

If the output is `active`, continue to the next step.

If it is not running, start the service:

```bash
sudo systemctl enable --now openvswitch-switch
```

### 3. Check POX and install if missing

Check whether POX is already installed:

```bash
ls ~/pox/pox.py
```

If the file exists, POX is installed.

If it is missing, clone the official POX repository:

```bash
git clone https://github.com/noxrepo/pox.git ~/pox
```

Verify the installation:

```bash
ls ~/pox/pox.py
```


If a `~/pox` directory already exists but does not contain `pox.py`, inspect that directory before cloning; do not overwrite or delete an existing POX folder blindly. POX's official repository documents running the controller through `pox.py`: [POX on GitHub](https://github.com/noxrepo/pox).


### 4. Clone the Project Repository

Clone the project from GitHub:

```bash
git clone https://github.com/Aamir-thecoder/time-sync-sdn.git ~/time-sync-sdn
```

Navigate to the project directory:

```bash
cd ~/time-sync-sdn
```

Check that the project files are present:

```bash
ls
```

Make sure the following files are present:

- `topology.py`
- `server.py`
- `client.py`
- `qos_setup.py`
- `dynamic_qos.py`
- `benchmark_client.py`
- `docs/`
- `results/`


### 5. Link the Dynamic QoS Component to POX

POX needs access to `dynamic_qos.py` to load the controller component.

Create a symbolic link:

```bash
ln -sf ~/time-sync-sdn/dynamic_qos.py ~/pox/pox/dynamic_qos.py
```

Verify the link:

```bash
ls -l ~/pox/pox/dynamic_qos.py
```

The file should point to `~/time-sync-sdn/dynamic_qos.py`.

### 6. Verify the Project Files

Navigate to the project directory:

```bash
cd ~/time-sync-sdn
```

Check that the Python files have valid syntax:

```bash
python3 -m py_compile topology.py server.py client.py qos_setup.py dynamic_qos.py benchmark_client.py
```

If the command finishes without errors, the Python files pass the syntax check.

### 7. Prepare the Terminals

Before starting the system:

- Keep the project folder at `~/time-sync-sdn` and POX at `~/pox`.
- Open two terminal windows: one for POX and one for Mininet. A third terminal is optional.
- Keep both terminals open while the system is running.
- Commands shown at the `mininet>` prompt must be entered in the Mininet terminal.

**Important:** Start Mininet from the project directory so its hosts can access project files using relative paths such as `./server.py` and `./client.py`.

After Mininet starts, verify the working directory:

```text
server pwd
client1 pwd
client2 pwd
```

All three should show a path ending in `/time-sync-sdn`.

## Start the System — Exact Terminal Order

### Terminal 1: POX Controller with Dynamic QoS

```bash
cd ~/pox
python3 ./pox.py forwarding.l2_learning dynamic_qos
```

Wait for messages indicating that the Dynamic QoS monitor has started and POX is listening for OpenFlow connections.

The configured thresholds are:

- **Activation:** Traffic at or above 6 Mbps for 2 consecutive samples.
- **Deactivation:** Traffic at or below 3.5 Mbps for 3 consecutive samples.

Keep this terminal open. During the demonstration, use it to show congestion detection, QoS activation and automatic recovery.


### Terminal 2: Mininet Topology


```bash
cd ~/time-sync-sdn
sudo mn -c
sudo python3 topology.py
```

Wait for the `mininet>` prompt. The topology should automatically invoke `qos_setup.py` and attach QoS queues to the three switch ports.

At `mininet>` run:

```text
nodes
net
pingall
```

Expected topology:

- Server: `10.0.0.1`, connected to switch port 1, configured delay 10 ms.
- Client 1: `10.0.0.2`, connected to switch port 2, configured delay 20 ms.
- Client 2: `10.0.0.3`, connected to switch port 3, configured delay 50 ms.

The `pingall` test should show connectivity between all hosts.

### Verify QoS Queue Configuration

After Mininet starts, verify that QoS is attached to all three switch ports:

```bash
sh ovs-vsctl --columns=name,qos list Port
```

The output should show QoS attached to:

- `s1-eth1` — Server
- `s1-eth2` — Client 1
- `s1-eth3` — Client 2

This confirms that `qos_setup.py` automatically created and attached the QoS configurations.

---


## Demonstration 1 — UDP Time Synchronization and Multiple Clients

At the `mininet>` prompt, start the reference time server:

```bash
server python3 -u ./server.py &
```

Verify that the server is running:

```bash
server pgrep -af server.py
```

Run Client 1:

```bash
client1 python3 -u ./client.py 10.0.0.1
```

Run Client 2:

```bash
client2 python3 -u ./client.py 10.0.0.1
```

Both clients should display the four timestamps, calculated RTT, and estimated clock offset.

### Simultaneous Client Test

Run both clients in the background to generate requests at approximately the same time:

```bash
client1 python3 -u ./client.py 10.0.0.1 > /tmp/client1.log 2>&1 &
client2 python3 -u ./client.py 10.0.0.1 > /tmp/client2.log 2>&1 &
```

Wait briefly and display both results:

```bash
client1 sleep 1
client1 cat /tmp/client1.log
client2 cat /tmp/client2.log
```

Both clients should complete their synchronization requests successfully.

**Explanation:**

> The clients communicate with a common UDP reference server. The server receives timestamp requests and sends responses containing the required timestamps. Each client calculates its RTT and estimates its clock offset. The application supports multiple clients communicating with the same server.

---

## Demonstration 2 — Dynamic QoS Prioritization Under Congestion

Start an iperf3 server on the reference-server host:

```bash
server iperf3 -s -p 5201 &
```

Generate competing TCP traffic from Client 1:

```bash
client1 iperf3 -c 10.0.0.1 -p 5201 -t 60 &
```

Watch Terminal 1 (POX). When monitored traffic reaches or exceeds 6 Mbps for two consecutive samples, the controller should detect congestion and activate the high-priority UDP synchronization rules.

### Verify OpenFlow Rules

While congestion is active, run:

```bash
sh ovs-ofctl -O OpenFlow10 dump-flows s1
```

The output should contain four high-priority rules with priority `60000`.

These rules classify UDP synchronization traffic on port `9999` and direct matching packets to Queue 1.

### Verify Queue 1 Forwarding

While TCP traffic is still running, execute:

```bash
client1 python3 -u ./client.py 10.0.0.1
client2 python3 -u ./client.py 10.0.0.1
```

Check the queue statistics:

```bash
sh ovs-ofctl -O OpenFlow10 queue-stats s1
```

Queue 1 packet counters should increase as synchronization requests and responses are processed.

**Explanation:**

> The POX controller monitors OpenFlow port statistics and detects congestion based on measured traffic rates. When the activation threshold is reached, it automatically installs high-priority flow rules that direct UDP synchronization traffic to Queue 1, giving it priority over ordinary traffic.

---

## Demonstration 3 — Automatic Recovery and Performance Evaluation

### Automatic Recovery

Allow the competing TCP traffic to finish.

Watch Terminal 1 (POX). When traffic remains at or below 3.5 Mbps for three consecutive samples, the controller should detect that congestion has cleared and automatically remove the special prioritization rules.

Verify the flow table:

```bash
sh ovs-ofctl -O OpenFlow10 dump-flows s1
```

The four special UDP prioritization rules should no longer be present.

The QoS queues remain configured on Open vSwitch; only the special OpenFlow rules are removed.

**Explanation:**

> The controller uses separate activation and deactivation thresholds to implement hysteresis. This prevents frequent switching between QoS states. When congestion clears, the controller automatically removes the temporary prioritization rules and returns synchronization traffic to normal queueing.

### Performance Evaluation

The project compares synchronization performance under competing TCP traffic in two configurations:

- **Baseline:** POX runs without the Dynamic QoS component.
- **Dynamic QoS:** POX monitors congestion and automatically prioritizes synchronization traffic.

Both configurations use the same Mininet topology, TCP load duration and benchmark settings.

The benchmark collects 50 synchronization measurements under a 90-second TCP load.

#### Test A — Baseline (Without Dynamic QoS)

1. Exit Mininet by typing `exit` and stop POX using `Ctrl+C`.

2. Start POX without the Dynamic QoS component:

```bash
cd ~/pox
python3 ./pox.py forwarding.l2_learning
```

3. Open another terminal and restart Mininet:

```bash
cd ~/time-sync-sdn
sudo mn -c
sudo python3 topology.py
```

4. At the `mininet>` prompt, start both servers:

```bash
server python3 -u ./server.py &
server iperf3 -s -p 5201 &
```

5. Start competing TCP traffic:

```bash
client1 iperf3 -c 10.0.0.1 -p 5201 -t 90 > /tmp/baseline-iperf.log 2>&1 &
```

6. Immediately run the synchronization benchmark:

```bash
client1 python3 ./benchmark_client.py 10.0.0.1 50 0.1 ./results/qos/performance/baseline_freshvm.csv
```

7. Check the TCP test results:

```bash
client1 cat /tmp/baseline-iperf.log
```

#### Test B — Dynamic QoS

1. Exit Mininet and stop the baseline POX controller.

2. Restart POX with Dynamic QoS enabled:

```bash
cd ~/pox
python3 ./pox.py forwarding.l2_learning dynamic_qos
```

3. Restart Mininet using the same commands as Test A.

4. At the `mininet>` prompt, start both servers again:

```bash
server python3 -u ./server.py &
server iperf3 -s -p 5201 &
```

5. Start the same 90-second competing TCP traffic:

```bash
client1 iperf3 -c 10.0.0.1 -p 5201 -t 90 > /tmp/dynamic-iperf.log 2>&1 &
```

6. Immediately run the same synchronization benchmark:

```bash
client1 python3 ./benchmark_client.py 10.0.0.1 50 0.1 ./results/qos/performance/dynamic_freshvm.csv
```

7. Verify the TCP test results:

```bash
client1 cat /tmp/dynamic-iperf.log
```

Check the POX terminal to confirm that congestion detection and automatic QoS activation occurred during the benchmark.

#### Metrics Collected

The benchmark evaluates:

- Average RTT
- Median RTT
- Minimum RTT
- Maximum RTT
- 95th-percentile RTT
- Successful and failed synchronization requests
- TCP receiver throughput
- TCP retransmissions

Compare the baseline and Dynamic QoS results to evaluate the effect of automatic synchronization-traffic prioritization.

**Note:** The existing experimental results are stored in `results/qos/performance/`. The fresh-VM benchmark runs use separate CSV filenames so the original experimental data is not overwritten.

The initial experiments showed an average RTT reduction of approximately **97.74%** with Dynamic QoS enabled. This is a preliminary result based on one run per configuration. Additional repeated trials are recommended for stronger performance conclusions.

### Initial measured results

These are the observed results from the current VM runs. They are single-run results and may vary on another machine.

| Metric | Baseline | Dynamic QoS |
|---|---:|---:|
| Successful synchronization measurements | 45 / 50 | 50 / 50 |
| Failed measurements | 5 | 0 |
| Average RTT | 1443.379 ms | 32.595 ms |
| Median RTT | 1586.244 ms | 32.295 ms |
| Minimum RTT | 430.050 ms | 31.307 ms |
| Maximum RTT | 2295.442 ms | 38.924 ms |
| 95th percentile RTT | 2171.636 ms | 34.329 ms |
| TCP receiver throughput | 9.38 Mbps | 9.41 Mbps |
| TCP retransmissions | 1775 | 1833 |

The observed average RTT reduction between these two runs was approximately 97.74%. The TCP receiver throughput was similar in both runs, which supports the comparison, but repeat trials are recommended before presenting this percentage as a final general result.

## Short explanation for the evaluator

> “Our application performs UDP-based time synchronization using a reference server and multiple clients. Mininet emulates the network, while POX provides Layer-2 forwarding and monitors OpenFlow port statistics. OVS queues are created automatically when the topology starts. When traffic exceeds 6 Mbps for two consecutive samples, the POX Dynamic QoS component installs high-priority OpenFlow rules that direct UDP synchronization traffic on port 9999 to Queue 1. When traffic falls to 3.5 Mbps or below for three consecutive samples, the controller removes those rules. We verified activation, Queue 1 packet counters and automatic recovery, then compared synchronization RTT under competing TCP traffic.”

## Stop the demonstration

1. Stop any foreground iperf3 or benchmark process if it is still running.
2. Type `exit` at the Mininet `mininet>` prompt.
3. Press `Ctrl+C` in the POX terminal.
4. Clean up Mininet if needed:

   ```bash
   sudo mn -c
   ```
