import logging, json
import datetime, time, os, sys, shutil
import subprocess, argparse, yaml, re

import cherrypy as NetPlanner
from netplanbuffers import cmdbuffers
import netifaces

logging.basicConfig(filename='netconfig-gen.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
handler = logging.StreamHandler(sys.stdout)
logging.getLogger().addHandler(handler)


class InterfaceGenerator(object):
    '''
    classdocs
    '''

    def __init__(self, staticdir=None):
        '''
        Constructor
        '''
        logging.info("Staring Interface Generator")
        self.staticdir = os.path.join(os.getcwd(), 'ui_www')
        if staticdir:
            self.staticdir = staticdir

        logging.info('Setting static directory as, %s' % (self.staticdir))

    def networkports(self, prefix=None):
        '''
        Grabs Network ports and details
        '''
        intfs = netifaces.interfaces()
        props = {'mac': netifaces.AF_LINK, 'ipv4': netifaces.AF_INET, 'ipv6': netifaces.AF_INET6}
        netobjs = {}
        intfprfx = ''
        if prefix:
            intfprfx = prefix

        for eth in intfs:
            #print("=== ", eth)
            ethobj = netifaces.ifaddresses(eth)
            ethprops = {}
            for key, prop in props.items():
                if prop in ethobj:
                    #print("\t=>%s, %s" % (prop, ethobj[prop][0]))
                        ethprops[key] = ethobj[prop][0]
            if intfprfx in eth:
                netobjs[eth] = ethprops
        #print(netobjs)
        return netobjs

    def ethInterfaceGen(self, intflist):
        """
        Generates a Network Interface file

        :param intflist:
        :return:
        """
        for key, value in intflist.items():
            print("Intf: {}".format(key))



# main code section
if __name__ == '__main__':
    intf = InterfaceGenerator(staticdir=None)
    intfs  = intf.networkports(prefix='en')
    for intf, intobj in intfs.items():
        print("{} / {}".format(intf, intobj))

    #NetPlanner.quickstart(InterfaceGenerator(staticdir=static_dir),
    #                      '/', conf)
    #
    # nplnr = NetPlan(staticdir=None)


