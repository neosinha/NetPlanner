#!/usr/bin/env python3
import base64
import datetime
import yaml
import logging
import cherrypy as HttpServer
from pymongo import MongoClient
import os, sys, ipaddress
import argparse

class RouterConfigGenerator:
    """
    Generates:
      - Netplan YAML for Ubuntu
      - dnsmasq.conf
      - iptables rules
      - install script
    from a simple YAML input describing the network segments.
    """

    staticdir = None
    starttime = None

    def __init__(self, staticdir=None, dbhost=None):
        '''
        Constructor
        '''
        self.staticdir = os.path.join(os.getcwd(), 'ui_www')
        if staticdir:
            self.staticdir = staticdir

        logging.info("Static directory for web-content: %s" % self.staticdir)

        # Intializing the upload directory
        uploaddir = os.path.join(self.staticdir, '..', 'uploads')
        if uploaddir:
            self.uploaddir = uploaddir
        os.makedirs(self.uploaddir, exist_ok=True)

        # DB Port Addresses
        self.dbhost = '127.0.0.1'
        self.dbport = 27017
        if dbhost:
            dbhostarr = dbhost.split(":")
            self.dbhost = dbhostarr[0]
            if dbhostarr[1]:
                self.dbport = int(dbhostarr[1])
        logging.info("MongoDB Client: {} : {}".format(self.dbhost, self.dbport))
        client = MongoClient(self.dbhost, self.dbport)

        self.dbase = client['routerconfig']
        self.configdb = self.dbase['configuration']


    @HttpServer.expose
    def index(self):
        """
        Sources the index file
        :return: raw index file
        """
        return open(os.path.join(self.staticdir, "index.html"))

    @HttpServer.expose
    def getinstallscript(self):
        """
        Get in the installscript file
        """
        return open(os.path.join(self.staticdir, "installrouterconfig"))

    @HttpServer.expose
    def getdnsmasq(self, data):
        """
        data: Get the configuration data from the Routers. data is base64 encoded
        """
        print(f"Configuring Router: {data}")
        datax = base64.b64decode(data).decode("utf-8").split("#")
        interfaces = datax[0].strip().split(";")
        macs = datax[1].strip().split(";")
        print(interfaces)
        print(macs)
        intfs = interfaces[1:]
        print(intfs)
        dnsmasq_str = self.generate_dnsmasqconf(interfaces=intfs,
                                                ip_bases=['10.20.0.0', '10.30.0.0', '10.40.0.0'])
        print(dnsmasq_str)
        return dnsmasq_str

    @HttpServer.expose
    def getnetplan(self, data):
        """
        data: Get the configuration data from the Routers. data is base64 encoded
        """
        print(f"Configuring NetPlanner: {data}")
        datax = base64.b64decode(data).decode("utf-8").split("#")
        interfaces = datax[0].strip().split(";")
        macs = datax[1].strip().split(";")
        print(interfaces)
        print(macs)
        intfs = interfaces[1:]
        netplan_str = self.generate_netplan(interfaces=interfaces,
                                            ip_bases=['10.21.0.0', '10.20.0.0', '10.30.0.0', '10.40.0.0'])
        return netplan_str

    @HttpServer.expose
    def getiptables(self, data):
        """
        Generates IP Tables rules
        """
        print(f"Configuring IPTables: {data}")
        datax = base64.b64decode(data).decode("utf-8").split("#")
        interfaces = datax[0].strip().split(";")
        macs = datax[1].strip().split(";")
        print(interfaces)
        print(macs)
        intfs = interfaces[1:]
        iptables_str = self.generate_iptables(interfaces=interfaces,
                                            ip_bases=['10.21.0.0', '10.20.0.0', '10.30.0.0', '10.40.0.0'])
        return iptables_str

    @HttpServer.expose
    def setbackup(self, data, bkup):
        """
        Upload backup files
        """


    def generate_netplan(self, interfaces, ip_bases):
        """
        Generate a Netplan YAML
        """
        dtstr = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        hdr = f"# Auto-generated netplan.yaml for segmented LAN DHCP on {dtstr}\n"
        hdr += f"# Copyright(c) SDOMUS LLC 2025, All Rights Reserved\n"
        hdr += f"# Do not tamper with the lines below, unless you are sure. \n"
        hdr += "# =========================================== \n"

        ntpln =hdr + "\n"
        ntpln +="network:\n"
        ntpln +=" version: 2\n"
        ntpln +=" renderer: networkd\n"
        ntpln +="\n"
        ntpln +=" ethernets:\n"
        idx = 0
        for intf, baseip in zip(interfaces, ip_bases):
            net = ipaddress.IPv4Interface(baseip + "/24")
            ip_network = ipaddress.IPv4Network(net.network, strict=False)
            start_ip = str(ip_network.network_address + 1)
            ntpln += f"  {intf}:\n"
            if idx == 0:
                ntpln += "   dhcp4: true\n"
            else:
                ntpln += "   addresses:\n"
                ntpln += f"    -{start_ip}/24\n"

            ntpln + "\n"
            idx = idx + 1


        return ntpln



    def generate_dnsmasqconf(self, interfaces, ip_bases, lease_time="12h"):
        """
        Generate a dnsmasq.conf file
        :param interfaces:
        :param ip_bases:
        :param lease_time:
        """
        dtstr = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        hdr = f"# Auto-generated dnsmasq.conf for segmented LAN DHCP on {dtstr}\n"
        hdr += f"# Copyright(c) SDOMUS LLC 2025, All Rights Reserved\n"
        hdr += f"# Do not tamper with the lines below, unless you are sure. \n"
        hdr += "# =========================================== \n"
        hdr +="no-resolv\n"
        hdr +="domain-needed\n"
        hdr +="bogus-priv\n"
        hdr +="\n"
        hdr +="# DNS Servers\n"
        hdr +="server=8.8.8.8\n"
        hdr +="server=1.1.1.1\n"
        hdr +="\n"
        hdr +="expand-hosts\n\n"
        hdr += "# Local Domain Name\n"
        hdr +="domain=sdomus.io\n\n"
        hdr +="# Bind to local interface\n"
        hdr +="bind-interfaces\n"

        bdy = "\n\n"
        for iface, base_ip in zip(interfaces, ip_bases):
            # Interface-specific settings
            #interface=eth1
            #dhcp-range=eth1,10.10.1.100,10.10.1.200,255.255.255.0,12h
            bdy += f"# Interface ${iface} specific settings\n"
            bdy += f"interfae={iface}\n"
            net = ipaddress.IPv4Interface(base_ip + "/24")
            ip_network = ipaddress.IPv4Network(net.network, strict=False)
            start_ip = str(ip_network.network_address + 50)
            end_ip = str(ip_network.network_address + 225)
            bdy += f"dhcp-range={iface},{start_ip},{end_ip},255.255.255.0,{lease_time}"
            bdy += "\n"

        return hdr + bdy


    def generate_iptables(self, interfaces, ip_bases):
        """
        Generates the iptables shell scripts
        """
        dtstr = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        scr = f"# Auto-generated dnsmasq.conf for segmented LAN DHCP on {dtstr}\n"
        scr += f"# Copyright(c) SDOMUS LLC 2025, All Rights Reserved\n"
        scr += f"# Do not tamper with the lines below, unless you are sure. \n"
        scr += "# =========================================== \n\n"
        wanport = interfaces[0]
        scr += f"# Enable NAT on WAN Interface{wanport}\n"
        scr += f'sudo iptables -t nat -A POSTROUTING -o {wanport} -j MASQUERADE\n'
        scr += "\n\n"
        lanports = interfaces[1:]
        ## Generate rules to transfer traffic between WAN <> LAN
        for idx, lanport in enumerate(lanports):
            scr += f"# Enable Traffic between LAN por{lanport} and WAN{wanport}\n"
            scr += f"sudo iptables -A FORWARD -i {lanport} -o {wanport} -j ACCEPT\n"
            scr += f"sudo iptables -A FORWARD -i {wanport} -o {lanport} -m state --state ESTABLISHED,RELATED -j ACCEPT\n"
            ## Firewall rules
            firewallports = lanports[idx:]
            scr += f"# Block Traffic between LAN por{lanport} and LAN ports {firewallports}\n"
            for lidx, flanport in enumerate(firewallports):
                scr += f"sudo iptables -A FORWARD -i {lanport} -o {flanport} -j DROP\n"

        scr += "\n\n"
        scr += "sudo netfilter-persistent save\n"
        scr += "sudo systemctl enable netfilter-persistent\n"
        scr += "\n\n"

        return scr

# main code section
if __name__ == '__main__':
        portmum = 9005
        www = os.path.join(os.getcwd(), 'ui_www')
        ipaddr = '127.0.0.1'

        dbip = '127.0.0.1:27017'

        logpath = os.path.join(os.getcwd(), 'log', 'raedam-server.log')
        logdir = os.path.dirname(logpath)
        os.makedirs(logdir, exist_ok=True)

        cascPath = os.path.abspath(os.getcwd())

        ap = argparse.ArgumentParser()
        ap.add_argument("-p", "--port", required=False, default=portmum,
                        help="Port number to start HTTPServer, defaults to {}".format(portmum))

        ap.add_argument("-i", "--ipaddress", required=False, default='127.0.0.1',
                        help="IP Address to start HTTPServer")

        ap.add_argument("-d", "--dbaddress", required=False, default='127.0.0.1:27017',
                        help="Database IP Address")

        ap.add_argument("-s", "--static", required=False, default=www,
                        help="Static directory where WWW files are present")


        ap.add_argument("-f", "--logfile", required=False, default=logpath,
                        help="Directory where application logs shall be stored, defaults to %s" % (logpath))

        # Parse Arguments
        args = vars(ap.parse_args())
        if args['port']:
            portnum = int(args["port"])

        if args['ipaddress']:
            ipadd = args["ipaddress"]

        if args['dbaddress']:
            dbip = args["dbaddress"]

        if args['static']:
            staticwww = os.path.abspath(args['static'])

        if args['logfile']:
            logpath = os.path.abspath(args['logfile'])
        else:
            if not os.path.exists(logdir):
                print("Log directory does not exist, creating %s" % (logdir))
                os.makedirs(logdir)

        logging.basicConfig(filename=logpath, format='%(asctime)s %(message)s')
        handler = logging.StreamHandler(sys.stdout)
        logging.getLogger().addHandler(handler)

        HttpServer.config.update({'server.socket_host': ipadd,
                                  'server.socket_port': portnum,
                                  'server.socket_timeout': 60,
                                  'server.thread_pool': 8,
                                  'server.max_request_body_size': 0
                                  })

        logging.info("Static dir: %s " % (staticwww))
        conf = {'/': {
            'tools.sessions.on': True,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': staticwww}
        }

        HttpServer.quickstart(RouterConfigGenerator (staticdir=staticwww, dbhost=dbip), '/', conf)
        #wbsx = Webserver(staticdir=staticwww)
        #wbsx.getjs()
