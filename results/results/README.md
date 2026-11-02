# Experimental Results and Validation Evidence

This directory contains the recorded experiments and screenshots for the Network Time Synchronization System.

## Folder structure

```text
results/
├── README.md
├── synchronization/
│   ├── synchronization_delay_experiment.csv
│   └── clock_offset_accuracy.csv
├── qos/
│   ├── static_qos_comparison.csv
│   ├── dynamic_qos_verification.csv
│   └── performance/
│       ├── baseline_repeat.csv
│       ├── dynamic.csv
│       └── performance_summary.csv
└── validation/
    ├── README.md
    ├── connectivity/
    │   └── mininet_connectivity.png
    ├── synchronization/
    │   └── udp_synchronization.png
    └── dynamic_qos/
        ├── activation_recovery.png
        ├── flow_rules.png
        └── queue1_forwarding.png
```

## Synchronization experiments

- `synchronization/synchronization_delay_experiment.csv`: observed RTT measurements under the configured Mininet link delays, including the Client 1 link-delay change from 20 ms to 100 ms and restoration to 20 ms. Blank/unrecorded values are marked as not recorded rather than treated as zero.
- `synchronization/clock_offset_accuracy.csv`: five measurements from the simulated client-clock offset experiment, with the calculated average absolute offset error.

## QoS experiments

- `qos/static_qos_comparison.csv`: earlier comparison of baseline forwarding and manually installed static UDP QoS rules.
- `qos/dynamic_qos_verification.csv`: recorded observations for Dynamic QoS activation/deactivation and Queue 1 packet counters.

## QoS performance comparison

The `qos/performance/` folder contains the raw RTT samples and summary from the initial baseline and Dynamic QoS comparison:

- `baseline_repeat.csv`: 50 baseline samples, including timeout statuses.
- `dynamic.csv`: 50 Dynamic QoS samples.
- `performance_summary.csv`: summary statistics and the corresponding TCP load measurements.

The initial comparison showed a substantial RTT difference, but it consists of one baseline run and one Dynamic QoS run. Treat the percentage improvement as a preliminary observation, not a statistically conclusive result. Repeat trials are recommended for a stronger evaluation.

## Experimental graphs

See `GRAPHS_README.md` for descriptions and interpretation notes. Four graphs are included:

- `synchronization/graphs/link_delay_vs_rtt.png`
- `synchronization/graphs/clock_offset_error.png`
- `qos/performance/graphs/rtt_samples_comparison.png`
- `qos/performance/graphs/average_rtt_comparison.png`

## Validation screenshots

See `validation/README.md` for descriptions of the connectivity, synchronization, OpenFlow-rule and Queue 1 forwarding screenshots.

All CSV files contain recorded values supplied from the project's experiments. Missing measurements are identified as not recorded; they are not inferred or replaced with zero.
