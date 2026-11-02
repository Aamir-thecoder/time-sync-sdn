import socket
import time
import struct
import sys
import csv
import statistics
import math

SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else "10.0.0.1"
COUNT = int(sys.argv[2]) if len(sys.argv) > 2 else 50
INTERVAL = float(sys.argv[3]) if len(sys.argv) > 3 else 0.1
OUTPUT = sys.argv[4] if len(sys.argv) > 4 else "benchmark_results.csv"

SERVER_PORT = 9999

rtt_values = []
offset_values = []
failed = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2.0)

with open(OUTPUT, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Sample", "RTT_ms", "Offset_ms"])

    print(f"Starting {COUNT} synchronization measurements...")

    for i in range(1, COUNT + 1):
        try:
            t1 = time.time()
            sock.sendto(struct.pack("!d", t1), (SERVER_IP, SERVER_PORT))

            data, _ = sock.recvfrom(1024)
            t4 = time.time()

            if len(data) != 24:
                raise ValueError("Invalid server response")

            t1_ret, t2, t3 = struct.unpack("!ddd", data)

            rtt = ((t4 - t1_ret) - (t3 - t2)) * 1000
            offset = ((t2 - t1_ret) + (t3 - t4)) * 500

            rtt_values.append(rtt)
            offset_values.append(offset)

            writer.writerow([
                i, round(rtt, 3), round(offset, 3)
            ])

            print(f"Sample {i:02d}: RTT = {rtt:.3f} ms")

        except (socket.timeout, ValueError) as error:
            failed += 1
            print(f"Sample {i:02d}: Failed - {error}")

        time.sleep(INTERVAL)

sock.close()

print("\n========== BENCHMARK RESULTS ==========")
print(f"Successful measurements: {len(rtt_values)}")
print(f"Failed measurements: {failed}")

if rtt_values:
    sorted_rtt = sorted(rtt_values)
    p95_index = math.ceil(0.95 * len(sorted_rtt)) - 1

    print(f"Average RTT: {statistics.mean(rtt_values):.3f} ms")
    print(f"Median RTT : {statistics.median(rtt_values):.3f} ms")
    print(f"Minimum RTT: {min(rtt_values):.3f} ms")
    print(f"Maximum RTT: {max(rtt_values):.3f} ms")
    print(f"95th percentile RTT: {sorted_rtt[p95_index]:.3f} ms")

print(f"\nResults saved to: {OUTPUT}")
