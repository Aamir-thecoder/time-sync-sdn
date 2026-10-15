import socket
import time
import struct

HOST = "0.0.0.0"
PORT = 9999

# Create a low-level UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"[*] Time Server listening on UDP port {PORT}...")

while True:
    try:
        # Buffer size of 1024 bytes
        data, addr = sock.recvfrom(1024)
        
        # T2: Server reception timestamp
        t2 = time.time()
        
        # Unpack the client send timestamp (T1) formatted as a double float
        t1 = struct.unpack("!d", data)[0]
        
        # T3: Server departure timestamp
        t3 = time.time()
        
        # Pack T1, T2, and T3 into binary data (three 8-byte doubles)
        response = struct.pack("!ddd", t1, t2, t3)
        sock.sendto(response, addr)
        
    except KeyboardInterrupt:
        print("\nShutting down server.")
        break

sock.close()
