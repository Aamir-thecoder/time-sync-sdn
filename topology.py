from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

def time_sync_network():
    # Initialize Mininet with RemoteController (for SDN) and TCLink (for network delay)
    net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink)

    print("[*] Adding SDN Controller...")
    # This prepares the network to connect to your Ryu controller later
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    print("[*] Adding Switch...")
    s1 = net.addSwitch('s1')

    print("[*] Adding Hosts...")
    server = net.addHost('server', ip='10.0.0.1')
    client1 = net.addHost('client1', ip='10.0.0.2')
    client2 = net.addHost('client2', ip='10.0.0.3')

    print("[*] Creating Links with Controlled Delay...")
    # Generating controlled network delay required by the project specifications
    net.addLink(server, s1, delay='10ms')
    net.addLink(client1, s1, delay='20ms')
    net.addLink(client2, s1, delay='50ms')

    print("[*] Starting Network...")
    net.start()
    
    print("[*] Network is running. Opening CLI.")
    CLI(net)

    print("[*] Stopping Network...")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    time_sync_network()
