# Classroom Demo Guide — Network Time Synchronization System

This guide is for a presenter who needs to demonstrate the project in a fixed order. It lists the terminal setup, commands to run, evidence to show, and short explanations for the evaluator.

## Before the demonstration — check and install prerequisites

Use the Ubuntu VM for the demonstration. The commands below check the required software first and install only missing Ubuntu packages.

### 1. Check the operating system

```bash
cat /etc/os-release
```

The commands in this guide are written for Ubuntu.

### 2. Check Python, Git, Mininet, Open vSwitch and iperf3

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
ovs-vsctl --version | head -n 1
ovs-ofctl --version | head -n 1
iperf3 --version | head -n 1
```

The Ubuntu packages used above are `mininet`, `openvswitch-switch` and `iperf3`; Mininet's installation guide also documents installing Mininet and starting Open vSwitch on Ubuntu/Debian. See the [Mininet installation guide](https://mininet.org/download/).

### 3. Make sure the Open vSwitch service is running

```bash
if systemctl is-active --quiet openvswitch-switch; then
    echo "Open vSwitch service is running."
else
    echo "Starting Open vSwitch service..."
    sudo systemctl enable --now openvswitch-switch
fi

systemctl is-active openvswitch-switch
```

The final command should print `active`.

### 4. Check POX and install it if it is missing

POX is obtained from its official GitHub repository. Check whether `pox.py` exists:

```bash
if [ -f "$HOME/pox/pox.py" ]; then
    echo "POX is present at $HOME/pox"
else
    echo "POX is not present at $HOME/pox"
fi
```

If POX is missing and `~/pox` does not already exist, clone it:

```bash
git clone https://github.com/noxrepo/pox.git ~/pox
```

Then verify it:

```bash
ls -l ~/pox/pox.py
```

If a `~/pox` directory already exists but does not contain `pox.py`, inspect that directory before cloning; do not overwrite or delete an existing POX folder blindly. POX's official repository documents running the controller through `pox.py`: [POX on GitHub](https://github.com/noxrepo/pox).

### 5. Check out the project and verify its files

Keep the project in `~/time-sync-sdn`. If the folder does not exist yet, clone the repository:

```bash
if [ ! -d "$HOME/time-sync-sdn" ]; then
    git clone https://github.com/Aamir-thecoder/time-sync-sdn.git "$HOME/time-sync-sdn"
else
    echo "Project folder already exists at $HOME/time-sync-sdn"
fi
```

Then check that the required files are present:

```bash
cd ~/time-sync-sdn

for file in topology.py server.py client.py qos_setup.py dynamic_qos.py benchmark_client.py; do
    if [ -f "$file" ]; then
        echo "[OK] $file"
    else
        echo "[MISSING] $file"
    fi
done
```

`benchmark_client.py` is needed only if you plan to run the performance comparison. The other files are needed for the complete Dynamic QoS demonstration.

### 6. Make the Dynamic QoS component visible to POX

Create/update the symbolic link once:

```bash
ln -sf ~/time-sync-sdn/dynamic_qos.py ~/pox/pox/dynamic_qos.py
```

Verify that the link resolves to the project file:

```bash
readlink -f ~/pox/pox/dynamic_qos.py
```

The output should point to `~/time-sync-sdn/dynamic_qos.py` (expanded to your home directory).

### 7. Check the automatic queue setup and benchmark syntax

Confirm that `topology.py` imports `configure_qos` from `qos_setup.py` and calls `configure_qos()` immediately after `net.start()`.

Run a syntax check:

```bash
cd ~/time-sync-sdn
python3 -m py_compile topology.py qos_setup.py dynamic_qos.py benchmark_client.py
```

If you are not running the performance comparison, you can omit `benchmark_client.py` from the syntax-check command.

### 8. Prepare the terminals and verify the project path

- Keep the project folder at `~/time-sync-sdn` and POX at `~/pox`. These paths use `~`, so they work regardless of the Ubuntu username.
- Open three terminal windows/tabs: one for POX, one for Mininet, and one spare for checks if needed.
- Keep the POX and Mininet terminals open while the system is running.
- Commands shown at the `mininet>` prompt must be entered in the Mininet terminal.
- Start Mininet from the project directory (`cd ~/time-sync-sdn` before running `sudo python3 topology.py`). The Mininet hosts inherit that working directory, allowing the demo commands to use relative paths such as `./server.py` so the commands do not contain any account-specific absolute paths.
- After Mininet starts, verify the working directory from the Mininet hosts:

  ```text
  server pwd
  client1 pwd
  ```

  Both should show the project directory ending in `/time-sync-sdn`. If they do not, start Mininet again from `~/time-sync-sdn`.

## Start the system — exact terminal order

### Terminal 1: POX controller with Dynamic QoS

```bash
cd ~/pox
python3 ./pox.py forwarding.l2_learning dynamic_qos
```

Wait for messages indicating that the Dynamic QoS monitor has started and that POX is listening for OpenFlow connections. The configured initial thresholds are:

- Activate: traffic above 6 Mbps for 2 consecutive samples.
- Deactivate: traffic at or below 3.5 Mbps for 3 consecutive samples.

Keep this terminal open. During the demo, use it to show congestion detection, QoS activation and recovery messages.

### Terminal 2: Mininet topology

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

### Verify automatic QoS queue creation

At `mininet>` run:

```text
sh ovs-vsctl --columns=name,qos list Port
```

Point out that QoS is attached to `s1-eth1`, `s1-eth2` and `s1-eth3`. The queues are created automatically by `qos_setup.py`; they do not need to be configured manually for each run.

To inspect queue definitions, use:

```text
sh ovs-vsctl list QoS
sh ovs-vsctl list Queue
```

## Demonstration 1 — UDP time synchronization

At `mininet>` start the reference time server:

```text
server python3 -u ./server.py &
```

Run Client 1:

```text
client1 python3 ./client.py 10.0.0.1
```

Run Client 2:

```text
client2 python3 ./client.py 10.0.0.1
```

Explain:

> “The clients send UDP timestamp requests to the reference server. The server records its receive and send timestamps and returns them to the client. The client uses the four timestamps to calculate round-trip delay and estimate the clock offset. The program estimates the offset; it does not change the host operating-system clock.”

## Demonstration 2 — Dynamic QoS activation under congestion

Start an iperf3 server on the reference-server host:

```text
server iperf3 -s -p 5201 &
```

Start competing TCP traffic from Client 1:

```text
client1 iperf3 -c 10.0.0.1 -p 5201 -t 30
```

Watch Terminal 1 (POX). When the monitored switch-port traffic exceeds the activation threshold for two consecutive samples, the controller should report congestion and activate the high-priority UDP synchronization rules.

Explain:

> “The controller polls OpenFlow port statistics and calculates traffic rates. When sustained traffic crosses the configured threshold, POX installs high-priority rules for UDP port 9999. These rules classify synchronization packets into Queue 1. The TCP traffic remains ordinary competing traffic.”

## Demonstration 3 — Verify the installed flow rules

While congestion is active, run this at `mininet>`:

```text
sh ovs-ofctl -O OpenFlow10 dump-flows s1
```

Point out the four high-priority rules (priority `60000`) that match UDP synchronization traffic and enqueue it on Queue 1:

| Direction | Match | Output queue |
|---|---|---|
| Client 1 to server | UDP destination port 9999, input port 2 | Port 1, Queue 1 |
| Client 2 to server | UDP destination port 9999, input port 3 | Port 1, Queue 1 |
| Server to Client 1 | UDP source port 9999, destination `10.0.0.2` | Port 2, Queue 1 |
| Server to Client 2 | UDP source port 9999, destination `10.0.0.3` | Port 3, Queue 1 |

The rules are installed by POX; they are not manually added with `ovs-ofctl` during the dynamic test.

## Demonstration 4 — Verify synchronization packets use Queue 1

While the TCP load is active, run the synchronization clients:

```text
client1 python3 ./client.py 10.0.0.1
client2 python3 ./client.py 10.0.0.1
```

Then inspect queue counters:

```text
sh ovs-ofctl -O OpenFlow10 queue-stats s1
```

Explain:

> “The Queue 1 packet counters increase when the synchronization requests and responses are classified into the high-priority queue. Queue counters provide evidence that the matching packets were enqueued. The counters may differ between runs depending on how many client requests were sent.”

## Demonstration 5 — Automatic recovery after congestion

Allow the iperf3 test to finish. Watch Terminal 1. Once the traffic remains at or below 3.5 Mbps for three consecutive samples, POX should report that congestion has cleared and remove the special prioritization rules.

Verify at `mininet>`:

```text
sh ovs-ofctl -O OpenFlow10 dump-flows s1
```

The four special UDP prioritization rules should no longer be present after the controller deactivates them. The QoS queues remain attached to the ports; only the dynamic classification rules are removed.

Explain:

> “The controller uses separate activation and deactivation thresholds, known as hysteresis. This prevents repeated switching when traffic fluctuates near one threshold. When congestion clears, the controller removes the temporary UDP prioritization rules automatically.”

## Demonstration 6 — Performance comparison

The benchmark program sends repeated synchronization requests and saves each RTT and offset measurement to a CSV file.

Use the same topology, server, TCP traffic duration and benchmark parameters for both runs. Restart both POX and Mininet between the baseline and Dynamic QoS tests.

### Test A: Baseline without Dynamic QoS

1. Exit Mininet and stop POX with `Ctrl+C`.
2. Start POX without the Dynamic QoS component:

   ```bash
   cd ~/pox
   python3 ./pox.py forwarding.l2_learning
   ```

3. Start Mininet in another terminal:

   ```bash
   cd ~/time-sync-sdn
   sudo mn -c
   sudo python3 topology.py
   ```

4. At `mininet>`, start the time server and iperf3 server:

   ```text
   server python3 -u ./server.py &
   server iperf3 -s -p 5201 &
   ```

5. Start a 90-second TCP load and immediately run the benchmark:

   ```text
   client1 iperf3 -c 10.0.0.1 -p 5201 -t 90 > /tmp/baseline-iperf.log 2>&1 &
   client1 python3 ./benchmark_client.py 10.0.0.1 50 0.1 ./baseline.csv
   ```

6. Save the benchmark summary and TCP log. Check the TCP test duration and receiver throughput:

   ```text
   client1 cat /tmp/baseline-iperf.log
   ```

With no Dynamic QoS component, the special UDP classification rules are not installed; synchronization packets use the normal/default queue.

### Test B: Dynamic QoS enabled

1. Exit Mininet and stop the baseline POX process with `Ctrl+C`.
2. Start POX with Dynamic QoS:

   ```bash
   cd ~/pox
   python3 ./pox.py forwarding.l2_learning dynamic_qos
   ```

3. Restart Mininet using the same commands as Test A. Start the same UDP time server and iperf3 server.
4. Start the same TCP load and benchmark:

   ```text
   client1 iperf3 -c 10.0.0.1 -p 5201 -t 90 > /tmp/dynamic-iperf.log 2>&1 &
   client1 python3 ./benchmark_client.py 10.0.0.1 50 0.1 ./dynamic.csv
   ```

5. Verify in the POX terminal that the controller activated prioritization during the benchmark. Inspect Queue 1 counters:

   ```text
   sh ovs-ofctl -O OpenFlow10 queue-stats s1
   ```

6. Save the benchmark summary and TCP log:

   ```text
   client1 cat /tmp/dynamic-iperf.log
   ```

Compare average, median and 95th-percentile RTT, successful and failed measurements, and TCP receiver throughput. Repeat both tests if time permits; a single run per configuration is preliminary evidence, not a statistically conclusive result.

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

