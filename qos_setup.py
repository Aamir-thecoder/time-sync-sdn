import subprocess

def configure_qos():
    print("[*] Configuring QoS queues...")

    ports = ["s1-eth1", "s1-eth2", "s1-eth3"]

    for port in ports:
        command = [
            "ovs-vsctl", "--",
            "--id=@q0", "create", "Queue",
            "other-config:priority=10",
            "other-config:min-rate=1000000",
            "other-config:max-rate=10000000",
            "--",
            "--id=@q1", "create", "Queue",
            "other-config:priority=0",
            "other-config:min-rate=1000000",
            "other-config:max-rate=10000000",
            "--",
            "--id=@qos", "create", "QoS",
            "type=linux-htb",
            "other-config:max-rate=10000000",
            "queues:0=@q0",
            "queues:1=@q1",
            "--",
            "set", "Port", port, "qos=@qos"
        ]

        subprocess.run(command, check=True)
        print(f"[+] QoS configured on {port}")

    print("[+] QoS queue configuration completed.")

