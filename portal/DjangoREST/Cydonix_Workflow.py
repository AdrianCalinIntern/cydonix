__author__ = 'Adi'

from sleekxmpp import ClientXMPP
from sleekxmpp.xmlstream import ET, tostring

import ConfigParser
from optparse import OptionParser
import sys
import os
import logging



class PortalXMPP(ClientXMPP):
    def __init__(self, jid, password, sensor_bot_jid, pubsub_server_jid, trigger, action, node):
        ClientXMPP.__init__(self, jid, password)

        # Set reciver jid and sender jid 
        self.sender_jid = jid
        self.sensor_bot_jid = sensor_bot_jid

        # Start sesion and print a succes mesage
        self.add_event_handler("session_start", self.session_start)
        
        # Connecting bot
        self.connect()
        
        # Sending bot presence
        self.send_presence()
        
        self.register_plugin('xep_0060')
        self.node = node
        self.pubsub_server = pubsub_server_jid
        self.add_event_handler('pubsub_publish', self._publish)
        self.trigger = trigger
        self.action = action

        try:
            self.subscribe()
            #self.unsubscribe()

            # Starting to process incoming messages
            self.process(block=True)
        except KeyboardInterrupt:
            self.send_thread.cancel()

    def session_start(self, event):
        print("Started")

    def subscribe(self):
        try:
            result = self['xep_0060'].subscribe(self.pubsub_server, self.node)
            print(result)
            print('Subscribed %s to node %s' % (self.boundjid.bare, self.node))
        except:
            logging.error('Could not subscribe %s to node %s' % (self.boundjid.bare, self.node))

    def _publish(self, msg):
        """Handle receiving a publish item event."""
        print msg
        data = msg['pubsub_event']['items']['item']['payload']
        str_data = tostring(data)
        begin = str_data.find('>') +1
        end = str_data.find('</test>')
        x = str_data[begin:end]
        if x == self.trigger:
            self.send_message(mto=self.sensor_bot_jid,
                          mbody='SET '+ self.action, mtype='normal', mfrom=self.sender_jid)

if  __name__ =='__main__':
    optp = OptionParser()

    optp.add_option('-c', '--config=FILE', dest="conf_file", help='configuration FILE')
    optp.add_option('-d', '--debug', help='set logging to DEBUG', action='store_const',
                    dest='loglevel', const=logging.DEBUG, default=logging.disable('INFO'))
    optp.add_option('-l', '--log=FILE', dest="log_file", help='log messages to FILE')

    opts, args = optp.parse_args()
    #print(opts.log_file)
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s', filename=opts.log_file, filemode='a')

    # If configuration file does not exist the script will terminate
    if not (os.path.isfile(str(opts.conf_file))):
        print "The configuration file does not exist"
        sys.exit()

    # Reading data from the configuration file
    conf = ConfigParser.ConfigParser()
    conf.read(opts.conf_file)
    
    # Reading data from config file and put into variabiles
    sender_jid = conf.get("XMPP", "sender_jid")
    sender_pass = conf.get("XMPP", "sender_pass")
    receiver_jid = conf.get("XMPP", "receiver_jid")
    pubsub_jid = conf.get("XMPP", "pubsub_jid")
    trigger = conf.get("XMPP", "trigger")
    action = conf.get("XMPP", "action")
    pubsub_node = conf.get("XMPP", "pubsub_node")
 
    
    xmpp = PortalXMPP(sender_jid, sender_pass, receiver_jid, pubsub_jid, trigger, action, pubsub_node)
