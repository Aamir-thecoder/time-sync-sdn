"""
Dynamic QoS controller component for the time-sync-sdn Mininet topology.

Run together with POX's learning switch:
    python3 ./pox.py forwarding.l2_learning dynamic_qos

Prerequisite:
    HTB queues 0 and 1 must already exist on s1-eth1, s1-eth2, s1-eth3.
    This component dynamically installs/removes the UDP classification flows.
"""

import time

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr
from pox.lib.recoco import Timer

log = core.getLogger()

# The experiment configures each switch port with a 10 Mbps HTB parent.
POLL_INTERVAL = 1.0
HIGH_THRESHOLD_BPS = 6_000_000       # Activate above 6 Mbps
LOW_THRESHOLD_BPS = 3_500_000        # Deactivate below 3.5 Mbps
HIGH_SAMPLES_REQUIRED = 2            # Two consecutive high samples
LOW_SAMPLES_REQUIRED = 3              # Three consecutive low samples

MONITORED_PORTS = (1, 2, 3)
FLOW_PRIORITY = 60000
SYNC_UDP_PORT = 9999
HIGH_PRIORITY_QUEUE = 1

# (input port, UDP field, UDP value, optional destination IP, output port)
RULES = (
    (2, "tp_dst", SYNC_UDP_PORT, None, 1),             # Client 1 -> Server
    (3, "tp_dst", SYNC_UDP_PORT, None, 1),             # Client 2 -> Server
    (1, "tp_src", SYNC_UDP_PORT, "10.0.0.2", 2),       # Server -> Client 1
    (1, "tp_src", SYNC_UDP_PORT, "10.0.0.3", 3),       # Server -> Client 2
)


class DynamicQoS(object):
    """
    Monitors OpenFlow port TX rates and enables synchronization QoS
    when sustained congestion is detected.
    """

    def __init__(self):
        self._last_port_stats = {}   # (dpid, port_no) -> (tx_bytes, timestamp)
        self._switch_state = {}      # dpid -> state dictionary

        core.openflow.addListenerByName(
            "ConnectionUp", self._handle_connection_up
        )
        core.openflow.addListenerByName(
            "ConnectionDown", self._handle_connection_down
        )
        core.openflow.addListenerByName(
            "PortStatsReceived", self._handle_port_stats
        )

        self._timer = Timer(
            POLL_INTERVAL, self._request_port_stats, recurring=True
        )

        log.info(
            "Dynamic QoS monitor started: poll=%.1fs, enable>=%.1f Mbps "
            "for %d samples, disable<=%.1f Mbps for %d samples",
            POLL_INTERVAL,
            HIGH_THRESHOLD_BPS / 1_000_000.0,
            HIGH_SAMPLES_REQUIRED,
            LOW_THRESHOLD_BPS / 1_000_000.0,
            LOW_SAMPLES_REQUIRED
        )

    def _handle_connection_up(self, event):
        dpid = event.connection.dpid

        self._switch_state[dpid] = {
            "active": False,
            "high_count": 0,
            "low_count": 0,
        }

        # Remove stale copies of our managed rules if POX was restarted.
        self._send_priority_rules(event.connection, enable=False)

        # Force a fresh counter baseline for this switch.
        for key in list(self._last_port_stats):
            if key[0] == dpid:
                del self._last_port_stats[key]

        log.info(
            "Switch %s connected. Dynamic QoS starts in NORMAL mode; "
            "waiting for congestion measurements.",
            dpid
        )

    def _handle_connection_down(self, event):
        dpid = event.connection.dpid
        self._switch_state.pop(dpid, None)

        for key in list(self._last_port_stats):
            if key[0] == dpid:
                del self._last_port_stats[key]

        log.info("Switch %s disconnected; monitor state cleared.", dpid)

    def _request_port_stats(self):
        # Ask each connected switch for counters on all physical ports.
        for connection in core.openflow.connections:
            try:
                request = of.ofp_stats_request(
                    body=of.ofp_port_stats_request(port_no=of.OFPP_NONE)
                )
                connection.send(request)
            except Exception as exc:
                log.warning(
                    "Could not request port statistics from switch %s: %s",
                    connection.dpid, exc
                )

    def _handle_port_stats(self, event):
        dpid = event.connection.dpid

        if dpid not in self._switch_state:
            self._switch_state[dpid] = {
                "active": False,
                "high_count": 0,
                "low_count": 0,
            }

        now = time.time()
        rates = {}

        for stat in event.stats:
            port_no = stat.port_no

            if port_no not in MONITORED_PORTS:
                continue

            key = (dpid, port_no)
            previous = self._last_port_stats.get(key)
            self._last_port_stats[key] = (stat.tx_bytes, now)

            # The first reply only establishes a byte-counter baseline.
            if previous is None:
                continue

            previous_bytes, previous_time = previous
            elapsed = now - previous_time
            byte_delta = stat.tx_bytes - previous_bytes

            # Ignore a reset/wrap sample; the new baseline is already saved.
            if elapsed <= 0 or byte_delta < 0:
                continue

            rates[port_no] = (byte_delta * 8.0) / elapsed

        if not rates:
            return

        # The busiest egress port is the best congestion indicator for
        # this small topology; congestion on different ports is independent.
        busiest_port = max(rates, key=rates.get)
        peak_rate = rates[busiest_port]
        state = self._switch_state[dpid]

        mode = "ACTIVE" if state["active"] else "NORMAL"
        log.info(
            "TRAFFIC MONITOR: switch %s port %d = %.2f Mbps; QoS state=%s",
            dpid, busiest_port, peak_rate / 1_000_000.0, mode
        )

        if not state["active"]:
            state["low_count"] = 0

            if peak_rate >= HIGH_THRESHOLD_BPS:
                state["high_count"] += 1
            else:
                state["high_count"] = 0

            if state["high_count"] >= HIGH_SAMPLES_REQUIRED:
                self._send_priority_rules(event.connection, enable=True)
                state["active"] = True
                state["high_count"] = 0
                log.info(
                    "CONGESTION DETECTED: switch %s port %d reached %.2f Mbps. "
                    "Activating high-priority UDP time-sync rules.",
                    dpid, busiest_port, peak_rate / 1_000_000.0
                )
        else:
            state["high_count"] = 0

            if peak_rate <= LOW_THRESHOLD_BPS:
                state["low_count"] += 1
            else:
                state["low_count"] = 0

            if state["low_count"] >= LOW_SAMPLES_REQUIRED:
                self._send_priority_rules(event.connection, enable=False)
                state["active"] = False
                state["low_count"] = 0
                log.info(
                    "CONGESTION CLEARED: switch %s busiest port is %.2f Mbps. "
                    "Returning synchronization traffic to normal queueing.",
                    dpid, peak_rate / 1_000_000.0
                )

    def _build_match(self, in_port, field, value, destination_ip):
        match = of.ofp_match()
        match.in_port = in_port
        match.dl_type = 0x0800       # IPv4
        match.nw_proto = 17          # UDP

        if field == "tp_dst":
            match.tp_dst = value
        else:
            match.tp_src = value

        if destination_ip is not None:
            match.nw_dst = IPAddr(destination_ip)

        return match

    def _send_priority_rules(self, connection, enable):
        for in_port, field, value, destination_ip, out_port in RULES:
            match = self._build_match(
                in_port, field, value, destination_ip
            )

            if enable:
                flow = of.ofp_flow_mod()
                flow.command = of.OFPFC_ADD
                flow.priority = FLOW_PRIORITY
                flow.match = match
                flow.actions.append(
                    of.ofp_action_enqueue(
                        port=out_port,
                        queue_id=HIGH_PRIORITY_QUEUE
                    )
                )
            else:
                flow = of.ofp_flow_mod()
                flow.command = of.OFPFC_DELETE_STRICT
                flow.priority = FLOW_PRIORITY
                flow.match = match
                flow.out_port = of.OFPP_NONE

            connection.send(flow)


def launch():
    """
    POX component entry point.
    Load alongside forwarding.l2_learning.
    """
    core.registerNew(DynamicQoS)
