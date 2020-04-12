'''
Created on Oct 2, 2019

@author: navendusinha
'''

import logging, json
import datetime, time, os, sys, shutil
import subprocess, argparse, yaml, re
import base64

import cherrypy as NetPlanner
from netplanbuffers import cmdbuffers
import netifaces

logging.basicConfig(filename='netplanner-server.log',level=logging.DEBUG, format='%(asctime)s %(message)s')
handler = logging.StreamHandler(sys.stdout)
logging.getLogger().addHandler(handler)


class NetPlan(object):
    '''
    classdocs
    '''


    def __init__(self, staticdir=None):
        '''
        Constructor
        '''
        logging.info("Staring NetPlan Serverlet")
        self.staticdir = os.path.join(os.getcwd(), 'ui_www')
        if staticdir: 
            self.staticdir = staticdir 
        
        logging.info('Setting static directory as, %s' % (self.staticdir))
        
        #self.getNetPlanStats()
        #self.loadnetplan()
        #self.ethinterfaces()
        self.networkports()
    
    
    def getNetPlanStats(self):
        '''
        Run network status commands
        '''
        intfs = self.shellcommand(['ip', 'a'])
        ifconf = self.shellcommand(['ifconfig'])
        

    @NetPlanner.expose
    def loadnetplan(self):
        '''
        Load NetPlan Settings
        '''
        netyaml = '/etc/netplan/50-cloud-init.yaml'
        logging.info('Reading YAML file, %s' % (netyaml) )
        yamlf = None
        with open(netyaml, 'r') as stream:
                yamlf = yaml.safe_load(stream)
                logging.info('Reading YAML : %s' % (yamlf))

        return json.dumps(yamlf)
    
    @NetPlanner.expose
    def index(self):
        '''
        Serves the index Page
        '''
        
        return open(os.path.join(self.staticdir, "index.html"))
    
    
    def shellcommand(self, cmdarr=None):
        '''
        '''
        shprocess = subprocess.Popen(cmdarr, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT)
        
        stdout,stderr = shprocess.communicate()
        stdout = str(stdout)
        for ln in stdout.split('\n'): 
            print(ln)
        

    @NetPlanner.expose
    def registerhost(self, appldef=None):
        """
        Registers a SmartDomus Appliance and generates a Segmented Network Defintion

        :param appldef:
        :return:
        """
        logging.info("Recieved Appliance Def: {}".format(appldef))
        appldefs = appldef.strip()
        print(appldef)
        infostr = base64.b64decode(appldef+"==").decode('utf-8')
        print(infostr)
        infoarr = infostr.split(';')
        for ninfo in infoarr:
            print(ninfo)



    @NetPlanner.expose
    def getInstallScript(self):
        """
        Get Install Script
        :return:
        """
        scrf = os.path.join(self.staticdir, 'client', 'clientsetup.sh')

        return open(scrf)






    @NetPlanner.expose
    def ethinterfaces_cmd(self):
        '''
        Method that extracts details of all physical interfaces
        '''
        str = cmdbuffers['ip-a'] 
        #print('------- %s' % (str))
        ethdef = re.compile('^[1-9]*:(.*)')
        macaddr = re.compile('link.*(..:..:..:..:..:..).brd')
        ethname = re.compile(':(.*):')
        inetaddr = re.compile('inet.(.*)brd')
        inetbrd = re.compile('inet.*brd(.*)scope')
        inettype = re.compile('inet.*scope(.*)')
        
        ethobjarr = []
        
        ethobj = {'name' : None, 'mac' : None}
        intdef = False
        buff = ''
        for line in str.splitlines():
            ethmatch = ethdef.search(line)
            if ethmatch:
                #print("--> ", ethmatch.group(0))
                if intdef: 
                    print('=====\n %s' % (buff))
                    print("=> %s" % (ethobj))
                    buff = ''
                    ethobjarr.append(ethobj)
                    ethobj = {}
                    
                elif not intdef:
                    intdef = True
                
                ethx_name = ethname.search(line)
                if ethx_name:
                    # print("Name: %s" % (ethx_name.group(0)))
                    ethobj['name'] = ethx_name.group(1).strip()
            
            # MAC Addr
            macaddr_match = macaddr.search(line)
            if macaddr_match: 
                print("MAC:  %s" % (macaddr_match.group(1))) 
                ethobj['mac'] = macaddr_match.group(1).strip().upper()
            
            # INET Addr    
            inetgroup_match = inetaddr.search(line)
            if inetgroup_match: 
                #print('Inet : %s' % (inetgroup_match.group(1)))
                #print('>> Inet: %s' % (inetgroup_match.group(0)))
                inetstr = inetgroup_match.group(1)
                inetbrd_match = inetbrd.search(line)
                if inetbrd_match: 
                    print('Broadcast: %s' % (inetbrd_match.group(1)))
            
                ethobj['ip4'] = {'addr' : inetstr.split('/')[0], 
                                 'subnet' : inetstr.split('/')[1], 
                                 'broadcast' : inetbrd_match.group(1).strip()}
            
                    
            if intdef:
                buff += line.strip() + '\n\t'
    
        print("Ethernet Interfaces")
        for ethobj in ethobjarr:
            print(ethobj)
    

    @NetPlanner.expose
    def networkports(self):
        '''
        Grabs Network ports and details
        '''
        intfs = netifaces.interfaces()
        props = { 'mac' : netifaces.AF_LINK, 'ipv4' : netifaces.AF_INET, 'ipv6' : netifaces.AF_INET6 }
        netobjs = {}
        for eth in intfs: 
            print("=== ", eth)
            ethobj = netifaces.ifaddresses(eth)
            ethprops = {}
            for key, prop in props.items():
                if prop in ethobj: 
                    print("\t=>%s, %s" % (prop, ethobj[prop][0]))
                    ethprops[key] = ethobj[prop][0]
            netobjs[eth] = ethprops
            logging.info('NetObj: %s, %s' % (eth, ethprops) )
        
        return json.dumps(netobjs)
    
    @NetPlanner.expose
    def getsysteminfo(self):
        '''
        '''
        sysinfo = {}
        sysinfo['system'] = None
        sysinfo['network'] = json.loads(self.networkports())
        
        return json.dumps(sysinfo)

# main code section   
if __name__ == '__main__':
    
    port = 9005
    www = os.path.join(os.getcwd(), 'ui_www')
    ipaddr = '0.0.0.0'
    dbip = '127.0.0.1'
    
    ap = argparse.ArgumentParser()  
    ap.add_argument("-p", "--port", required=False, default=6001,
                help="Port number to start HTTPServer." )

    ap.add_argument("-i", "--ipaddress", required=False, default=ipaddr,
                help="IP Address to start HTTPServer")

    
    ap.add_argument("-s", "--static", required=False, default=www, 
                help="Static directory where WWW files are present")

    args = vars(ap.parse_args())
    
    portnum = int(args["port"])
    ipadd = args["ipaddress"]
    staticwww = os.path.abspath(args['static'])
    
    

    NetPlanner.config.update({ 'server.socket_host' : ipadd,
                          'server.socket_port': portnum, 
                          'server.socket_timeout': 60,
                          'server.thread_pool' : 8, 
                          'server.max_request_body_size': 0 
                          })
    
    
    # static_dir = os.path.join(os.getcwd(), '..' ,'www')
    static_dir = staticwww
    
    logging.info("Static dir: %s " % (static_dir))
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': static_dir
        }
    }
    
    NetPlanner.quickstart(NetPlan(staticdir=static_dir),
                               '/', conf)
    #
    #nplnr = NetPlan(staticdir=None)
    
    