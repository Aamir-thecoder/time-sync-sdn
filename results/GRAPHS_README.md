# Experimental Graphs

These graphs are generated from the CSV datasets in this `results/` directory.

## Synchronization graphs

- `synchronization/graphs/link_delay_vs_rtt.png`: recorded host-link delays versus measured RTT. Client 1 was measured at 20 ms, 100 ms, then restored to 20 ms. Client 2 RTT was recorded in the first two experiments only.
- `synchronization/graphs/clock_offset_error.png`: five recorded absolute clock-offset errors and their mean.

## QoS performance graphs

- `qos/performance/graphs/rtt_samples_comparison.png`: individual RTT samples for the baseline and Dynamic QoS runs. Baseline timeouts appear as gaps, not zero RTT.
- `qos/performance/graphs/average_rtt_comparison.png`: average RTT over successful samples. The vertical axis is logarithmic because the averages differ greatly.

## Interpretation cautions

The performance comparison contains one baseline run and one Dynamic QoS run. The calculated reduction is a preliminary observation, not a statistically conclusive result. The baseline average excludes five timed-out samples; the Dynamic QoS average uses all 50 successful samples.

Graphs use only recorded values in the accompanying CSV files. Missing measurements are not interpolated or treated as zero.
