from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import time
import os


def assignmentTopo():
    net = Mininet( controller=RemoteController)
    
    info( '*** Adding controller\n' )
    net.addController('c0')
    

    ### Code here to add hosts switches and links ###############
    info( '*** Adding hosts\n' )
    h1 = net.addHost( 'h1', ip='10.0.0.1', mac='00:00:00:00:00:01' )
    h2 = net.addHost( 'h2', ip='10.0.0.2', mac='00:00:00:00:00:02' )
    h3 = net.addHost( 'h3', ip='10.0.0.3', mac='00:00:00:00:00:03' )
    h4 = net.addHost( 'h4', ip='10.0.0.4', mac='00:00:00:00:00:04' )
    
    info( '*** Adding switches\n' )
    s1 = net.addSwitch( 's1' )

    info( '*** Creating links\n' )
    net.addLink( s1, h1 )     
    net.addLink( s1, h2 )
    net.addLink( s1, h3 )
    net.addLink( s1, h4 )
    
    #root = s1
    #############################################################


    info( '*** Starting network\n')
    net.start()
    h1, h2, h3, h4 = net.hosts[0],net.hosts[1],net.hosts[2],net.hosts[3]
    

    ### Add code here to add QoS commands using hte ovs-vsctl primitive #################
    ### Yuo shuld use the command os.system("....")   to run the ovsctl commands ########
    ########################################################################################
    os.system('sudo ovs-vsctl set port s1-eth2 qos=@newqos -- --id=@newqos create qos type=linux-htb queues=0=@q0,1=@q1 -- --id=@q0 create queue other-config:min-rate=0 other-config:max-rate=50000000 --  --id=@q1 create queue other-config:min-rate=50000000 other-config:max-rate=100000000')    
    #os.system('sudo ovs-vsctl set port s1-eth4 qos=@newqos -- --id=@newqos create qos type=linux-htb queues=0=@q0 -- --id=@q0 create queue other-config:min-rate=100000000 other-config:max-rate=200000000')
    
    # os.system('sudo ovs-ofctl add-flow s1 dl_dst=00:00:00:00:00:03,dl_src=00:00:00:00:00:01,actions=enqueue:3:0')
    # os.system('sudo ovs-ofctl add-flow s1 dl_dst=00:00:00:00:00:02,dl_src=00:00:00:00:00:01,actions=enqueue:3:0')
    # os.system('sudo ovs-ofctl add-flow s1 dl_dst=00:00:00:00:00:01,dl_src=00:00:00:00:00:02,actions=enqueue:3:0')
    
    # os.system('sudo ovs-ofctl add-flow s1 dl_dst=00:00:00:00:00:03,dl_src=00:00:00:00:00:02,actions=enqueue:3:1')
    # os.system('sudo ovs-ofctl add-flow s1 dl_dst=00:00:00:00:00:04,dl_src=00:00:00:00:00:02,actions=enqueue:4:0')
    # os.system('sudo ovs-ofctl add-flow s1 dl_dst=00:00:00:00:00:04,dl_src=00:00:00:00:00:03,actions=enqueue:3:0')
    # os.system('sudo ovs-ofctl add-flow s1 dl_dst=00:00:00:00:00:03,dl_src=00:00:00:00:00:04,actions=enqueue:3:0')

    
    ### Add code here to run iperf tests to verify that your solutions respects the given performance   ##############
    ### You should use iperf commands to check data rate and connectivity among all nodes               ##############
    
    ###The example is shown here for one iperf conection####
    info( '\n\n\n\n*** Testing PIR from H1 to H3\n')
    h3.cmd('iperf -s &') # this creates a listener for iperf in H3 - the & let's it run in the backgorund, so that the function returns and the code execution can proceed to the next line.
    print(h1.cmd('iperf -c %s' % h3.IP()))  #this starts the transmission from H1 to H3
    
    #### Here you can add the other iperf tests ######
    info( '\n\n\n\n*** Testing PIR from H1 to H2\n')
    h2.cmd('iperf -s &')
    print(h1.cmd('iperf -c %s' % h2.IP()))  
    #######
    info( '\n\n\n\n*** Testing PIR from H2 to H1\n')
    h1.cmd('iperf -s &')
    print(h2.cmd('iperf -c %s' % h1.IP()))  
    ###..........######
    info( '\n\n\n\n*** Testing PIR from H2 to H3\n')
    h3.cmd('iperf -s &')
    print(h2.cmd('iperf -c %s' % h3.IP()))  
    ### ....................
    info( '\n\n\n\n*** Testing PIR from H2 to H4\n')
    h4.cmd('iperf -s &')
    print(h2.cmd('iperf -c %s' % h4.IP()))  
    #####
    info( '\n\n\n\n*** Testing PIR from H3 to H4\n')
    h4.cmd('iperf -s &')
    print(h3.cmd('iperf -c %s' % h4.IP()))  
    #######
    info( '\n\n\n\n*** Testing PIR from H4 to H3\n')
    h3.cmd('iperf -s &')
    print(h4.cmd('iperf -c %s' % h3.IP()))  
    ##############################################################################################################
    print(h1.cmd('ping -c 1 %s ' % h2.IP())) 
    print(h2.cmd('ping -c 1 %s ' % h1.IP())) 
    print(h3.cmd('ping -c 1 %s ' % h4.IP())) 
    print(h4.cmd('ping -c 1 %s ' % h3.IP())) 
    CLI( net )
    #### the following commands delete all Qos entries before quitting mininet #################
    os.system('sudo ovs-vsctl clear Port s1-eth3 qos')
    os.system('sudo ovs-vsctl clear Port s1-eth4 qos')
    os.system('sudo ovs-vsctl --all destroy qos')
    os.system('sudo ovs-vsctl --all destroy queue')
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    assignmentTopo()


