from __future__ import print_function  # This import is for python2.*
import atexit
import requests
import ssl
import getpass
from pyvim import connect
from pyVmomi import vim
from pyVmomi import vmodl
import argparse
import yaml
import re

portgroupList = ['1-10',
'1-2',
'1-5',
'1-6',
'1-7',
'1-8',
'1-9',
'2-10',
'2-2',
'2-3',
'2-4',
'2-5',
'2-6',
'2-7',
'2-8',
'2-9',
'3-10',
'3-5',
'3-6',
'3-7',
'3-8',
'3-9',
'4-10',
'4-5',
'4-6',
'4-7',
'4-8',
'4-9',
'5-6',
'7-8',
'9-10']

def get_obj(content, vimtype, name):
    """
    Return an object by name, if name is None the
    first found object is returned
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                return obj
        else:
            obj = c
            return obj

def AddHostSwitch(host, vswitchName):
    vswitch_spec = vim.host.VirtualSwitch.Specification()
    vswitch_spec.numPorts = 32
    vswitch_spec.mtu = 9000

    #Set security policies. We need to be pretty open here for vEOS
    #Note remark out network_policy below because this is not working.
    #For the time being, we'll set it under the port group
    #https://github.com/vmware/pyvmomi-community-samples/issues/403
    #network_policy = vim.host.NetworkPolicy()
    #network_policy.security = vim.host.NetworkPolicy.SecurityPolicy()
    #network_policy.security.allowPromiscuous = True
    #network_policy.security.macChanges = True
    #network_policy.security.forgedTransmits = True

    #vswitch_spec.policy = network_policy

    host.configManager.networkSystem.AddVirtualSwitch(vswitchName,vswitch_spec)

    #Now create port group and add that to the vswitch we just created.

    portgroup_spec = vim.host.PortGroup.Specification()
    portgroup_spec.vswitchName = vswitchName
    portgroup_spec.name = vswitchName
    portgroup_spec.vlanId = int(4095)
    network_policy = vim.host.NetworkPolicy()
    network_policy.security = vim.host.NetworkPolicy.SecurityPolicy()
    network_policy.security.allowPromiscuous = True
    network_policy.security.macChanges = True
    network_policy.security.forgedTransmits = True
    portgroup_spec.policy = network_policy

    host.configManager.networkSystem.AddPortGroup(portgroup_spec)

service_instance = None
sslContext = None
verify_cert = None

sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
sslContext.verify_mode = ssl.CERT_NONE
verify_cert = False

service_instance = connect.SmartConnect(host='192.168.133.131',
                   user='root',
                   pwd='totallyarealpasswordEric',
                   port=443,
                   sslContext=sslContext)
content=service_instance.RetrieveContent()
host=get_obj(content,[vim.HostSystem], None)

for portgroup in portgroupList:
   AddHostSwitch(host,portgroup)
