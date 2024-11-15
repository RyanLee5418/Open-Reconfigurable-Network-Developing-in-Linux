from pox.core import core
import pox.lib.packet as pkt
import pox.lib.packet.ethernet as eth
import pox.lib.packet.arp as arp
import pox.lib.packet.icmp as icmp
import pox.lib.packet.ipv4 as ip
import pox.lib.packet.tcp as tcp
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr


log = core.getLogger()

table={}


rules=[['00:00:00:00:00:01', '00:00:00:00:00:03'],['00:00:00:00:00:03', '00:00:00:00:00:04'],['00:00:00:00:00:02', '00:00:00:00:00:03'],
       ['00:00:00:00:00:01', '00:00:00:00:00:02','30','0'], ['00:00:00:00:00:01', '00:00:00:00:00:02','50','1']]#,['00:00:00:00:00:02', '00:00:00:00:00:03','1'],['00:00:00:00:00:02', '00:00:00:00:00:04','0']]

##################################################################################################


def launch ():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("PacketIn",  _handle_PacketIn)
    log.info("Switch running.")

def _handle_ConnectionUp ( event):
    log.info("Starting Switch %s", dpidToStr(event.dpid))
    msg = of.ofp_flow_mod(command = of.OFPFC_DELETE)
    event.connection.send(msg)
      

def _handle_PacketIn ( event):

    dpid = event.connection.dpid
    sw=dpidToStr(event.dpid)
    inport = event.port
    eth_packet = event.parsed
    log.debug("Event: switch %s port %s packet %s" % (sw, inport, eth_packet))


    table[(event.connection,eth_packet.src)] = event.port
    dst_port = table.get((event.connection,eth_packet.dst))
    
    

    if dst_port is None and eth_packet.type == eth.ARP_TYPE and eth_packet.dst == EthAddr(b"\xff\xff\xff\xff\xff\xff"):
        

        msg = of.ofp_packet_out(data = event.ofp)
        msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))
        event.connection.send(msg)
        #########################################################
       
    else:
        for rule in rules:
           if len(rule) < 3:

               block = of.ofp_match()
               block.dl_src = EthAddr(rule[0])
               block.dl_dst = EthAddr(rule[1])
               flow_mod = of.ofp_flow_mod()
               flow_mod.match = block
               flow_mod.priority = 32000
               event.connection.send(flow_mod)
 
           elif len(rule) < 4:
               msg = of.ofp_flow_mod()
               msg.priority=100
               msg.match.dl_src = EthAddr(rule[0])
               msg.match.dl_dst = EthAddr(rule[1])
               msg.match.tp_dst = tcp.dstport(rule[2])
               msg.hard_timeout = 60
               msg.actions.append(of.ofp_action_output(port = event.port))
               event.connection.send(msg)

               msg = of.ofp_packet_out()
               msg.data = event.ofp
               msg.actions.append(of.ofp_action_output(port = dst_port))
               event.connection.send(msg)
              
               #log.debug("Installing %s <-> %s" % (eth_packet.src, eth_packet.dst))



           else:
               msg = of.ofp_flow_mod()
               msg.priority=100
               msg.match.dl_dst = eth_packet.src
               msg.match.dl_src = eth_packet.dst
               msg.hard_timeout = 60
               msg.actions.append(of.ofp_action_output(port = event.port))
               event.connection.send(msg)


               msg = of.ofp_packet_out()
               msg.data = event.ofp
               msg.actions.append(of.ofp_action_output(port = dst_port))
               event.connection.send(msg)
              
               log.debug("Installing %s <-> %s" % (eth_packet.src, eth_packet.dst))
