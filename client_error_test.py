import socket
import time
import struct
import sys

SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
SERVER_PORT = 9999

# Simulate the client clock being 50 ms ahead of the server.
SIMULATED_OFFSET_MS = 50.0
SIMULATED_OFFSET_SEC = SIMULATED_OFFSET_MS / 1000.0

# Reference offset is server time minus client time.
REFERENCE_OFFSET_MS = -SIMULATED_OFFSET_MS


def client_time():
    """Return simulated client time, 50 ms ahead of system time."""
    return time.time() + SIMULATED_OFFSET_SEC


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2.0)

try:
    # T1: Client sends request.
    t1 = client_time()
    sock.sendto(struct.pack("!d", t1), (SERVER_IP, SERVER_PORT))

    # Receive server response, then record T4.
    data, _ = sock.recvfrom(1024)
    t4 = client_time()

    # Unpack the echoed T1 and server timestamps T2 and T3.
    t1_ret, t2, t3 = struct.unpack("!ddd", data)

    # Calculate round-trip delay and estimated clock offset.
    rtt_delay = (t4 - t1) - (t3 - t2)
    estimated_offset_ms = (
        ((t2 - t1_ret) + (t3 - t4)) / 2.0
    ) * 1000.0

    # Compare estimated offset with the known reference offset.
    synchronization_error = abs(
        estimated_offset_ms - REFERENCE_OFFSET_MS
    )

    print("\n--- Synchronization Error Measurement ---")
    print(f"Simulated Client Offset : {SIMULATED_OFFSET_MS:.3f} ms")
    print(f"Reference Offset        : {REFERENCE_OFFSET_MS:.3f} ms")
    print(f"Estimated Offset        : {estimated_offset_ms:.3f} ms")
    print(f"Round-Trip Delay        : {rtt_delay * 1000:.3f} ms")
    print(f"Synchronization Error   : {synchronization_error:.3f} ms")

except socket.timeout:
    print("Request timed out. Check whether the server is running.")
except struct.error as exc:
    print(f"Invalid response received from server: {exc}")
finally:
    sock.close()
