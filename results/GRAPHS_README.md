# Experimental Graphs

The plots in this folder are generated from the recorded CSV datasets.

## Synchronization graphs

- `synchronization/graphs/link_delay_vs_rtt.png`: a three-test timeline showing Client 1's configured delay change (20 ms -> 100 ms -> 20 ms restored) and the corresponding recorded RTTs. Client 2 remained configured at 50 ms; its RTT is shown only for the first two tests because no third value was recorded.
- `synchronization/graphs/clock_offset_error.png`: comparison of five recorded absolute clock-offset errors from the earlier VM run and five from fresh-VM validation; each series is labeled with its mean.

## QoS performance graphs

- `qos/performance/graphs/rtt_samples_comparison.png`: individual RTT samples for the baseline and Dynamic QoS runs. Baseline timeouts appear as gaps, not zero RTT.
- `qos/performance/graphs/average_rtt_comparison.png`: horizontal log-scale comparison of average RTT. Labels and the preliminary-result note are placed outside the bars to avoid overlap.

## Interpretation cautions

The performance comparison contains one baseline run and one Dynamic QoS run. The calculated reduction is a preliminary observation, not a statistically conclusive result. The baseline average excludes five timed-out samples; the Dynamic QoS average uses all 50 successful samples.

Graphs use only recorded values in the accompanying CSV files. Missing measurements are not interpolated or treated as zero.
