import socket
import time
import struct
import sys

# Default to localhost if no IP is provided
SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
SERVER_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2.0)  # Timeout if a packet is dropped

try:
    # T1: Client departure timestamp
    t1 = time.time()
    
    # Send T1 to the server
    sock.sendto(struct.pack("!d", t1), (SERVER_IP, SERVER_PORT))
    
    # Receive response from server
    data, _ = sock.recvfrom(1024)
    
    # T4: Client arrival timestamp
    t4 = time.time()
    
    # Unpack T1, T2, T3
    t1_ret, t2, t3 = struct.unpack("!ddd", data)
    
    # Calculate round-trip delay and clock offset
    rtt_delay = (t4 - t1) - (t3 - t2)
    clock_offset = ((t2 - t1) + (t3 - t4)) / 2.0
    
    print(f"--- Synchronization Results with {SERVER_IP} ---")
    print(f"T1 (Client Send)   : {t1:.6f}")
    print(f"T2 (Server Receive): {t2:.6f}")
    print(f"T3 (Server Send)   : {t3:.6f}")
    print(f"T4 (Client Receive): {t4:.6f}")
    print(f"Round-Trip Delay   : {rtt_delay * 1000:.3f} ms")
    print(f"Estimated Offset   : {clock_offset * 1000:.3f} ms")
    
except socket.timeout:
    print("[!] Request timed out. Packet may have been dropped.")
finally:
    sock.close()
