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


### The list where the rules that need to be installed. ###################
rules=[['00:00:00:00:00:01', '00:00:00:00:00:03'],['00:00:00:00:00:03', '00:00:00:00:00:04'],['00:00:00:00:00:02', '00:00:00:00:00:03']]
       ##['00:00:00:00:00:01', '00:00:00:00:00:02','30','0'], ['00:00:00:00:00:01', '00:00:00:00:00:02','50','1']]#,['00:00:00:00:00:02', '00:00:00:00:00:03','1'],['00:00:00:00:00:02', '00:00:00:00:00:04','0']]

##################################################################################################


def launch ():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("PacketIn",  _handle_PacketIn)
    log.info("Switch running.")

def _handle_ConnectionUp ( event):
    log.info("Starting Switch %s", dpidToStr(event.dpid))
    msg = of.ofp_flow_mod(command = of.OFPFC_DELETE)
    event.connection.send(msg)
      
    for rule in rules:
               block = of.ofp_match()
               block.dl_src = EthAddr(rule[0])
               block.dl_dst = EthAddr(rule[1])
               flow_mod = of.ofp_flow_mod()
               flow_mod.match = block
               flow_mod.priority = 32000
               event.connection.send(flow_mod)  

def _handle_PacketIn ( event):

    dpid = event.connection.dpid
    sw=dpidToStr(event.dpid)
    inport = event.port
    eth_packet = event.parsed
    log.debug("Event: switch %s port %s packet %s" % (sw, inport, eth_packet))


    table[(event.connection,eth_packet.src)] = event.port
    dst_port = table.get((event.connection,eth_packet.dst))
    
    if dst_port is None:
        
        msg = of.ofp_packet_out(data = event.ofp)
        msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))
        event.connection.send(msg)
        #########################################################
       
    else:
         msg = of.ofp_flow_mod()
         if isinstance(eth_packet.next, ip):
            if eth_packet.find('tcp') != None:
                ipp = eth_packet.find('tcp')
                #ipp.tpye = 0x800
                #ipp.protocol = 6
                msg.match.tp_src = ipp.srcport
                msg.match.tp_dst = ipp.dstport
                msg.match.nw_src = eth_packet.next.srcip
                msg.match.nw_dst = eth_packet.next.dstip
                if eth_packet.next.srcip == "10.0.0.1" and eth_packet.next.dstip == "10.0.0.2":
                           if str(ipp.dstport) == "30":
                               msg.actions.append(of.ofp_action_enqueue(port = dst_port, queue_id = 0))
                               event.connection.send(msg)
                           elif str(ipp.dstport) == "50":
                               msg.actions.append(of.ofp_action_enqueue(port = dst_port, queue_id = 1))
                               event.connection.send(msg)
                           else: 
                               msg.actions.append(of.ofp_action_output(port = dst_port))
                               event.connection.send(msg)

                elif (eth_packet.next.srcip == "10.0.0.1" or eth_packet.next.srcip == "10.0.0.2") and eth_packet.next.dstip == "10.0.0.4":        
                           if str(ipp.dstport) == "40": 
                               msg.actions.append(of.ofp_action_output(port = event.port))
                               event.connection.send(msg)   
            else:
                            
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

        
 
        #    elif len(rule) < 4:
        #        msg = of.ofp_flow_mod()
        #        msg.priority=100
        #        msg.match.dl_src = EthAddr(rule[0])
        #        msg.match.dl_dst = EthAddr(rule[1])
        #        msg.match.tp_dst = tcp.dstport(rule[2])
        #        msg.hard_timeout = 60
        #        msg.actions.append(of.ofp_action_output(port = event.port))
        #        event.connection.send(msg)


        #        msg = of.ofp_packet_out()
        #        msg.data = event.ofp
        #        msg.actions.append(of.ofp_action_output(port = dst_port))
        #        event.connection.send(msg)
              
               #log.debug("Installing %s <-> %s" % (eth_packet.src, eth_packet.dst))



        #    else:
        #        msg = of.ofp_flow_mod()
        #        if isinstance(eth_packet.next, ip):
        #            if eth_packet.find('tcp') != None:
        #                ipp = eth_packet.find('tcp')
            
        #                msg.match.tp_src = ipp.srcport
        #                msg.match.tp_dst = ipp.dstport
        #                msg.match.nw_src = eth_packet.next.srcip
        #                msg.match.nw_dst = eth_packet.next.dstip
        #                if eth_packet.next.srcip == "10.0.0.1" and eth_packet.next.dstip == "10.0.0.2":
        #                    if str(ipp.dstport) == "30":
        #                        msg.actions.append(of.ofp_action_enqueue(port = dst_port, queue_id = 0))
        #                        event.connection.send(msg)
        #                    elif str(ipp.dstport) == "50":
        #                        msg.actions.append(of.ofp_action_enqueue(port = dst_port, queue_id = 1))
        #                        event.connection.send(msg)
        #                    else:
        #                        msg.priority=100
        #                        msg.match.dl_dst = eth_packet.src
        #                        msg.match.dl_src = eth_packet.dst
        #                        msg.hard_timeout = 60
        #                        msg.actions.append(of.ofp_action_output(port = event.port))
        #                        event.connection.send(msg)

        #                 
        #                        msg = of.ofp_packet_out()
        #                        msg.data = event.ofp
        #                        msg.actions.append(of.ofp_action_output(port = dst_port))
        #                        event.connection.send(msg)

        #                        log.debug("Installing %s <-> %s" % (eth_packet.src, eth_packet.dst))
        #        msg.priority=100
        #        msg.match.dl_dst = eth_packet.src
        #        msg.match.dl_src = eth_packet.dst
        #        msg.hard_timeout = 60
        #        msg.actions.append(of.ofp_action_output(port = event.port))
        #        event.connection.send(msg)

        #        msg = of.ofp_packet_out()
        #        msg.data = event.ofp
        #        msg.actions.append(of.ofp_action_output(port = dst_port))
        #        event.connection.send(msg)
              
               #log.debug("Installing %s <-> %s" % (eth_packet.src, eth_packet.dst))
