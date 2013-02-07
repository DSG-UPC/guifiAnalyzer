#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# libcnml.py - CNML library
# Copyright (C) 2012 Pablo Castellano <pablo@anche.no>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


try:
    from lxml import etree
    from lxml.etree import XMLSyntaxError
    LXML = True
    print 'Using lxml which is more efficient'
except ImportError:
    import xml.dom.minidom as MD
    LXML = False
    print 'lxml module not found. Falling back to minidom'


class CNMLZone(object):
    def __init__(self, zid, parentid, aps=0, box=[], nclients=0, ndevices=0, nlinks=0, nservices=0, title=''):
        self.id = zid
        self.parentzone = parentid
        self.totalAPs = aps
        self.box = box
        self.totalClients = nclients
        self.totalDevices = ndevices
        self.totalLinks = nlinks
        self.totalServices = nservices
        self.title = title
        self.subzones = dict()
        self.nodes = dict()

    # @param z: CNMLZone
    def addSubzone(self, z):
        self.subzones[z.id] = z

    # @param z: CNMLNode
    def addNode(self, n):
        self.nodes[n.id] = n

    def getNodes(self):
        return self.nodes.values()

    def getSubzones(self):
        return self.subzones.values()

    @staticmethod
    def parseLxml(z):
        zid = int(z.get('id'))
        try:
            zparentid = int(z.get('parent_id'))
        except:
            # guifi.net World doesn't have parent_id
            zparentid = None

        nAPs = z.get('access_points') or 0
        nAPs = int(nAPs)
        box = z.get('box').split(',')
        box = [box[:2], box[2:]]
        nclients = z.get('clients') or 0
        nclients = int(nclients)
        ndevices = z.get('devices') or 0
        ndevices = int(ndevices)
        nlinks = z.get('links') or 0
        nlinks = int(nlinks)
        nservices = z.get('services') or 0
        nservices = int(nservices)
        title = z.get('title')
#       nnodes = int(z.getAttribute('zone_nodes'))
#       nnodes is not useful --> len(nodes)

        newzone = CNMLZone(zid, zparentid, nAPs, box, nclients, ndevices, nlinks, nservices, title)
        return newzone

    @staticmethod
    # @param z: xml.dom.minidom.Element
    def parseMinidom(z):
        zid = int(z.getAttribute("id"))
        try:
            zparentid = int(z.getAttribute("parent_id"))
        except:
            # guifi.net World doesn't have parent_id
            zparentid = None

        nAPs = z.getAttribute("access_points") or 0
        nAPs = int(nAPs)
        box = z.getAttribute("box").split(',')
        box = [box[:2], box[2:]]
        nclients = z.getAttribute("clients") or 0
        nclients = int(nclients)
        ndevices = z.getAttribute('devices') or 0
        ndevices = int(ndevices)
        nlinks = z.getAttribute('links') or 0
        nlinks = int(nlinks)
        nservices = z.getAttribute('services') or 0
        nservices = int(nservices)
        title = z.getAttribute('title')
#       nnodes = int(z.getAttribute('zone_nodes'))
#       nnodes is not useful --> len(nodes)

        newzone = CNMLZone(zid, zparentid, nAPs, box, nclients, ndevices, nlinks, nservices, title)
        return newzone

    @staticmethod
    def parse(z):
        if LXML:
            return CNMLZone.parseLxml(z)
        else:
            return CNMLZone.parseMinidom(z)


class CNMLNode(object):
    def __init__(self, nid, title, lat, lon, nlinks, status):
        self.id = nid
        self.title = title
        self.latitude = lat
        self.longitude = lon
        self.totalLinks = nlinks
        self.status = status
        self.devices = dict()
        self.services = dict()

    def getDevices(self):
        return self.devices.values()

    def getServices(self):
        return self.services.values()

    def addDevice(self, dev):
        self.devices[dev.id] = dev

    def addService(self, service):
        self.services[service.id] = service

    @staticmethod
    def parseMinidom(n):
        nid = int(n.getAttribute("id"))
        lat = float(n.getAttribute("lat"))
        lon = float(n.getAttribute("lon"))
        title = n.getAttribute('title')
        #ndevices = n.getAttribute('devices') or 0
        #ndevices = int(ndevices)
        nlinks = n.getAttribute('links') or 0
        nlinks = int(nlinks)
        status = n.getAttribute('status')
        status = Status.strToStatus(status)

        newnode = CNMLNode(nid, title, lat, lon, nlinks, status)
        return newnode

    @staticmethod
    def parseLxml(n):
        nid = int(n.get('id'))
        lat = float(n.get('lat'))
        lon = float(n.get('lon'))
        title = n.get('title')
        #ndevices = n.getAttribute('devices') or 0
        #ndevices = int(ndevices)
        nlinks = n.get('links') or 0
        nlinks = int(nlinks)
        status = n.get('status')
        status = Status.strToStatus(status)

        newnode = CNMLNode(nid, title, lat, lon, nlinks, status)
        return newnode

    @staticmethod
    def parse(n):
        if LXML:
            return CNMLNode.parseLxml(n)
        else:
            return CNMLNode.parseMinidom(n)


class CNMLService(object):
    def __init__(self, sid, title, stype, status, created, parent):
        self.id = sid
        self.title = title
        self.type = stype
        self.status = status
        self.created = created
        self.parentNode = parent

    @staticmethod
    def parseLxml(s, parent):
        sid = int(s.get('id'))
        title = s.get('title')
        stype = s.get('type')
        status = s.get('status')
        status = Status.strToStatus(status)
        created = s.get('created')

        newservice = CNMLService(sid, title, stype, status, created, parent)
        return newservice

    @staticmethod
    def parseMinidom(s, parent):
        sid = int(s.getAttribute('id'))
        title = s.getAttribute('title')
        stype = s.getAttribute('type')
        status = s.getAttribute('status')
        status = Status.strToStatus(status)
        created = s.getAttribute('created')

        newservice = CNMLService(sid, title, stype, status, created, parent)
        return newservice

    @staticmethod
    def parse(s, parent):
        if LXML:
            return CNMLService.parseLxml(s, parent)
        else:
            return CNMLService.parseMinidom(s, parent)


class CNMLDevice(object):
    def __init__(self, did, name, firmware, status, title, dtype, parent):
        self.id = did
        self.name = name
        self.firmware = firmware
        self.status = status
        self.title = title
        self.type = dtype
        self.radios = dict()
        self.interfaces = dict()
        self.parentNode = parent

    def getRadios(self):
        return self.radios.values()

    def getInterfaces(self):
        return self.interfaces.values()

    def addRadio(self, radio):
        self.radios[radio.id] = radio

    def addInterface(self, interface):
        self.interfaces[interface.id] = interface

    @staticmethod
    def parseLxml(d, parent):
        did = int(d.get('id'))
        name = d.get('name')
        firmware = d.get('firmware')
        status = d.get('status')
        status = Status.strToStatus(status)
        title = d.get('title')
        dtype = d.get('type')
        #nlinks = d.getAttribute('links') or 0
        #nlinks = int(nlinks)
        #por qué no tiene un atributo radios="2" en lugar de links="2"??

        newdevice = CNMLDevice(did, name, firmware, status, title, dtype, parent)
        return newdevice

    @staticmethod
    def parseMinidom(d, parent):
        did = int(d.getAttribute("id"))
        name = d.getAttribute("name")
        firmware = d.getAttribute("firmware")
        status = d.getAttribute("status")
        status = Status.strToStatus(status)
        title = d.getAttribute("title")
        dtype = d.getAttribute("type")
        #nlinks = d.getAttribute('links') or 0
        #nlinks = int(nlinks)
        #por qué no tiene un atributo radios="2" en lugar de links="2"??

        newdevice = CNMLDevice(did, name, firmware, status, title, dtype, parent)
        return newdevice

    @staticmethod
    def parse(d, parent):
        if LXML:
            return CNMLDevice.parseLxml(d, parent)
        else:
            return CNMLDevice.parseMinidom(d, parent)


class CNMLRadio(object):
    def __init__(self, rid, protocol, snmp_name, ssid, mode, gain, angle, channel, clients, parent):
        self.id = rid
        self.protocol = protocol
        self.snmp_name = snmp_name
        self.ssid = ssid
        self.mode = mode
        self.antenna_gain = gain
        self.antenna_angle = angle
        self.channel = channel
        self.clients_accepted = clients
        self.interfaces = dict()
        self.parentDevice = parent

    def getInterfaces(self):
        return self.interfaces.values()

    def addInterface(self, iface):
        self.interfaces[iface.id] = iface

    @staticmethod
    def parseLxml(r, parent):
        #radio ids are 0, 1, 2...
        rid = int(r.get('id'))
        protocol = r.get('protocol')
        snmp_name = r.get('snmp_name')
        ssid = r.get('ssid')
        mode = r.get('mode')
        antenna_gain = r.get('antenna_gain')
        antenna_angle = r.get('antenna_angle')
        channel = r.get('channel') or 0  # ugly
        channel = int(channel)
        clients = r.get('clients_accepted') == 'Yes'

        #falta atributo interfaces="2"
        #sobra atributo device_id

        newradio = CNMLRadio(rid, protocol, snmp_name, ssid, mode, antenna_gain, antenna_angle, channel, clients, parent)
        return newradio

    @staticmethod
    def parseMinidom(r, parent):
        #radio ids are 0, 1, 2...
        rid = int(r.getAttribute('id'))
        protocol = r.getAttribute('protocol')
        snmp_name = r.getAttribute('snmp_name')
        ssid = r.getAttribute('ssid')
        mode = r.getAttribute('mode')
        antenna_gain = r.getAttribute('antenna_gain')
        antenna_angle = r.getAttribute('antenna_angle')
        channel = r.getAttribute('channel') or 0  # ugly
        channel = int(channel)
        clients = r.getAttribute('clients_accepted') == 'Yes'

        #falta atributo interfaces="2"
        #sobra atributo device_id

        newradio = CNMLRadio(rid, protocol, snmp_name, ssid, mode, antenna_gain, antenna_angle, channel, clients, parent)
        return newradio

    @staticmethod
    def parse(r, parent):
        if LXML:
            return CNMLRadio.parseLxml(r, parent)
        else:
            return CNMLRadio.parseMinidom(r, parent)


class CNMLInterface(object):
    def __init__(self, iid, ipv4, mask, mac, itype, parent):
        self.id = iid
        self.ipv4 = ipv4
        self.mask = mask
        self.mac = mac
        self.type = itype
        self.links = dict()
        self.parentRadio = parent

    def getLinks(self):
        return self.links.values()

    def addLink(self, link):
        self.links[link.id] = link

    @staticmethod
    def parseLxml(i, parent):
        iid = int(i.get('id'))
        ipv4 = i.get('ipv4')
        mac = i.get('mac')
        #checkMac
        mask = i.get('mask')
        itype = i.get('type')  # wLan/Lan

        newiface = CNMLInterface(iid, ipv4, mask, mac, itype, parent)

        return newiface

    @staticmethod
    def parseMinidom(i, parent):
        iid = int(i.getAttribute('id'))
        ipv4 = i.getAttribute('ipv4')
        mac = i.getAttribute('mac')
        #checkMac
        mask = i.getAttribute('mask')
        itype = i.getAttribute('type')  # wLan/Lan

        newiface = CNMLInterface(iid, ipv4, mask, mac, itype, parent)

        return newiface

    @staticmethod
    def parse(i, parent):
        if LXML:
            return CNMLInterface.parseLxml(i, parent)
        else:
            return CNMLInterface.parseMinidom(i, parent)


# Note that for two connected nodes there's just one link, that is,
# two different links (different linked dev/if/node) but same id
# Given a device link, how to difference which is the linked device, A or B?
class CNMLLink(object):
    def __init__(self, lid, status, ltype, ldid, liid, lnid, parent):
        self.id = lid
        self.status = status
        self.type = ltype
        #self.linked_device = {ldid:None}
        #self.linked_interface = {liid:None}
        #self.linked_node = {lnid:None}
        self.parentInterface = parent
        self.nodeA = lnid
        self.deviceA = ldid
        self.interfaceA = liid
        self.nodeB = None
        self.deviceB = None
        self.interfaceB = None

    def getLinkedNodes(self):
        return [self.nodeA, self.nodeB]

    def getLinkedDevices(self):
        return [self.deviceA, self.deviceB]

    def getLinkedInterfaces(self):
        return [self.interfaceA, self.interfaceB]

    def parseLinkBLxml(self, l):
        self.nodeB = int(l.get('linked_node_id'))
        self.deviceB = int(l.get('linked_device_id'))
        self.interfaceB = int(l.get('linked_interface_id'))

    def parseLinkBLMinidom(self, l):
        self.nodeB = int(l.getAttribute('linked_node_id'))
        self.deviceB = int(l.getAttribute('linked_device_id'))
        self.interfaceB = int(l.getAttribute('linked_interface_id'))

    def parseLinkB(self, l):
        if LXML:
            self.parseLinkBLxml(l)
        else:
            self.parseLinkBLMinidom(l)

    def setLinkedParameters(self, devs, ifaces, nodes):
        didA = self.deviceA
        iidA = self.interfaceA
        nidA = self.nodeA
        didB = self.deviceB
        iidB = self.interfaceB
        nidB = self.nodeB

        if self.nodeB is None:
            #print "Couldn't find linked node (%d) in link %d. It may be defined in a different CNML zone." %(self.nodeA, self.id)
            return

        if didA in devs:
            self.deviceA = devs[didA]
        else:
            print 'Device id %d not found' % self.deviceA

        if didB in devs:
            self.deviceB = devs[didB]
        else:
            print 'Device id %d not found' % self.deviceB

        if iidA in ifaces:
            self.interfaceA = ifaces[iidA]
        else:
            print 'Interface id %d not found' % self.interfaceA

        if iidB in ifaces:
            self.interfaceB = ifaces[iidB]
        else:
            print 'Interface id %d not found' % self.interfaceB

        if nidA in nodes:
            self.nodeA = nodes[nidA]
        else:
            print 'Node id %d not found' % self.nodeA

        if nidB in nodes:
            self.nodeB = nodes[nidB]
        else:
            print 'Node id %d not found' % self.nodeB

    # Cambiar nombres:
    # link_status -> status
    # link_type -> type
    # linked_device_id -> device_id
    # linked_interface_id -> interface_id
    # linked_node_id -> node_id
    @staticmethod
    def parseLxml(l, parent):
        lid = int(l.get('id'))
        status = l.get('link_status')
        ltype = l.get('link_type')
        ldid = int(l.get('linked_device_id'))
        liid = int(l.get('linked_interface_id'))
        lnid = int(l.get('linked_node_id'))

        newlink = CNMLLink(lid, status, ltype, ldid, liid, lnid, parent)
        return newlink

    @staticmethod
    def parseMinidom(l, parent):
        lid = int(l.getAttribute('id'))
        status = l.getAttribute('link_status')
        ltype = l.getAttribute('link_type')
        ldid = int(l.getAttribute('linked_device_id'))
        liid = int(l.getAttribute('linked_interface_id'))
        lnid = int(l.getAttribute('linked_node_id'))

        newlink = CNMLLink(lid, status, ltype, ldid, liid, lnid, parent)
        return newlink

    @staticmethod
    def parse(l, parent):
        if LXML:
            return CNMLLink.parseLxml(l, parent)
        else:
            return CNMLLink.parseMinidom(l, parent)


class Status(object):
    PLANNED = 1
    WORKING = 2
    TESTING = 3
    BUILDING = 4
    RESERVED = 5
    DROPPED = 6

    @staticmethod
    def strToStatus(status):
        if status.lower() == "planned":
            st = Status.PLANNED
        elif status.lower() == "working":
            st = Status.WORKING
        elif status.lower() == "testing":
            st = Status.TESTING
        elif status.lower() == "building":
            st = Status.BUILDING
        elif status.lower() == "reserved":
            st = Status.RESERVED
        elif status.lower() == "dropped":
            st = Status.DROPPED
        else:
            print 'Value:', status
            raise ValueError

        return st

    @staticmethod
    def statusToStr(status):
        if status == Status.PLANNED:
            st = 'Planned'
        elif status == Status.WORKING:
            st = 'Working'
        elif status == Status.TESTING:
            st = 'Testing'
        elif status == Status.BUILDING:
            st = 'Building'
        elif status == Status.RESERVED:
            st = 'Reserved'
        elif status == Status.DROPPED:
            st = 'Dropped'
        else:
            raise ValueError

        return st


class CNMLParser(object):
    def __init__(self, filename, lazy=False):
        self.filename = filename
        self.rootzone = 0

        self.nodes = None
        self.zones = None
        self.devices = None
        self.services = None
        self.radios = None
        self.ifaces = None
        self.links = None

        if not lazy:
            self.loaded = self.load()
            # TODO: raise exception if load failed so that the user interface can show a messagebox
        else:
            self.loaded = False

    def validateDTD(self, tree):
        print 'Validating file "%s"...' % self.filename

        if LXML:
            self.validateDTDLxml(tree)
        else:
            self.validateDTDMinidom(tree)

    def validateDTDLxml(self, tree):
        dtdfile = 'tests/cnml.dtd'
        try:
            with open(dtdfile, 'rb') as dtdfp:
                dtd = etree.DTD(dtdfp)

            print 'DTD validation:', dtd.validate(tree)
            errors = dtd.error_log.filter_from_errors()
            if len(errors) > 0:
                print '%d errors found:' % len(errors)
                print errors

        except IOError:
            print 'DTD Validation failed: %s file not found' % dtdfile

    def validateDTDMinidom(self, tree):
        print 'DTD validation is not implemented with Minidom API'
        pass

    def findNodefromIPv4(self, ipv4):
        for i in self.getInterfaces():
            if i.ipv4 == ipv4:
                radio = i.parentRadio
                if isinstance(radio, CNMLRadio):
                    node = radio.parentDevice.parentNode
                else:
                    # parent of radio is already a device
                    node = radio.parentNode
                return node
        return None

    def getNodes(self):
        return self.nodes.values()

    def getZones(self):
        return self.zones.values()

    def getDevices(self):
        return self.devices.values()

    def getServices(self):
        return self.services.values()

    def getRadios(self):
        return self.radios.values()

    def getInterfaces(self):
        return self.ifaces.values()

    def getLinks(self):
        return self.links.values()

    def loadLxml(self, validate=True):
        try:
            tree = etree.parse(self.filename)
        except XMLSyntaxError, e:
            print 'Error reading CNML file:', e
            print 'The file might be corrupted. Please remove it manually:'
            print 'rm', self.filename
            return False

        if validate:
            print 'Validating file "%s"...' % self.filename
            self.validateDTDLxml(tree)

        # --zones--
        zones = tree.iterfind('//zone')

        self.rootzone = int(tree.find('//zone[1]').get('id'))

        for z in zones:
            zid = int(z.get('id'))
            newzone = CNMLZone.parse(z)
            self.zones[zid] = newzone
            zparentid = newzone.parentzone

            if zid != self.rootzone and zparentid is not None:
                self.zones[zparentid].addSubzone(newzone)

        # --nodes--
        for n in tree.iterfind('//node'):
            nid = int(n.get('id'))
            zid = int(n.getparent().get('id'))
            newnode = CNMLNode.parse(n)
            self.nodes[nid] = newnode
            self.zones[zid].addNode(newnode)

            #assert n.parentNode.localName == u'zone'
            #assert(ndevices == len(devicestree))

            # --devices--
            for d in n.iterfind('device'):
                did = int(d.get('id'))
                newdevice = CNMLDevice.parse(d, newnode)
                self.devices[did] = newdevice
                self.nodes[nid].addDevice(newdevice)

                # --interfaces--
                # If there's a working service in this device, it has interfaces (and it's not a son of a radio!)
                for i in d.iterchildren('interface'):
                    iid = int(i.get('id'))
                    newiface = CNMLInterface.parse(i, newdevice)
                    self.ifaces[iid] = newiface
                    self.devices[did].addInterface(newiface)

                # --services--
                for s in d.iterfind('service'):
                    sid = int(s.get('id'))
                    newservice = CNMLService.parse(s, newdevice)
                    self.services[sid] = newservice
                    self.nodes[nid].addService(newservice)

                # --radios--
                for r in d.iterfind('radio'):
                    rid = int(r.get('id'))
                    newradio = CNMLRadio.parse(r, newdevice)
                    self.devices[did].addRadio(newradio)

                    # --interfaces--
                    for i in r.iterfind('interface'):
                        iid = int(i.get('id'))
                        newiface = CNMLInterface.parse(i, newradio)
                        self.ifaces[iid] = newiface
                        self.devices[did].radios[rid].addInterface(newiface)

                        # --links--
                        for l in i.iterfind('link'):
                            lid = int(l.get('id'))

                            if lid in self.links:
                                self.links[lid].parseLinkB(l)
                                self.ifaces[iid].addLink(self.links[lid])
                            else:
                                newlink = CNMLLink.parse(l, newiface)
                                self.links[lid] = newlink
                                self.ifaces[iid].addLink(newlink)

        # Replace None by true reference of nodes/devices/interfaces
        # Note that if they belong to a different zone they might not be defined in the CNML file
        for link in self.getLinks():
            link.setLinkedParameters(self.devices, self.ifaces, self.nodes)

        return True

    def loadMinidom(self, validate=True):
        tree = MD.parse(self.filename)

        if validate:
            print 'Validating file "%s"...' % self.filename
            self.validateDTDMinidom(tree)

        # --zones--
        zones = tree.getElementsByTagName("zone")

        self.rootzone = int(zones[0].getAttribute("id"))

        for z in zones:
            zid = int(z.getAttribute("id"))
            newzone = CNMLZone.parse(z)
            self.zones[zid] = newzone
            zparentid = newzone.parentzone

            if zid != self.rootzone and zparentid is not None:
                self.zones[zparentid].addSubzone(newzone)

        # --nodes--
        for n in tree.getElementsByTagName("node"):
            nid = int(n.getAttribute("id"))
            zid = int(n.parentNode.getAttribute('id'))
            newnode = CNMLNode.parse(n)
            self.nodes[nid] = newnode
            self.zones[zid].addNode(newnode)

            #assert n.parentNode.localName == u'zone'
            #assert(ndevices == len(devicestree))

            # --devices--
            for d in n.getElementsByTagName("device"):
                did = int(d.getAttribute("id"))
                newdevice = CNMLDevice.parse(d, newnode)
                self.devices[did] = newdevice
                self.nodes[nid].addDevice(newdevice)

                # --interfaces--
                # TODO: If there's a working service in this device, it has interfaces (and it's not a son of a radio!)
                # Look at the lxml parsing

                # --services--
                for s in d.getElementsByTagName('service'):
                    sid = int(s.getAttribute('id'))
                    newservice = CNMLService.parse(s, newdevice)
                    self.services[sid] = newservice
                    self.nodes[nid].addService(newservice)

                # --radios--
                for r in d.getElementsByTagName("radio"):
                    rid = int(r.getAttribute('id'))
                    newradio = CNMLRadio.parse(r, newdevice)
                    self.devices[did].addRadio(newradio)

                    # --interfaces--
                    for i in r.getElementsByTagName("interface"):
                        iid = int(i.getAttribute('id'))
                        newiface = CNMLInterface.parse(i, newradio)
                        self.ifaces[iid] = newiface
                        self.devices[did].radios[rid].addInterface(newiface)

                        # --links--
                        for l in i.getElementsByTagName("link"):
                            lid = int(l.getAttribute('id'))

                            if lid in self.links:
                                self.links[lid].parseLinkB(l)
                                self.ifaces[iid].addLink(self.links[lid])
                            else:
                                newlink = CNMLLink.parse(l, newiface)
                                self.links[lid] = newlink
                                self.ifaces[iid].addLink(newlink)

        # Replace None by true reference of nodes/devices/interfaces
        # Note that if they belong to a different zone they might not be defined in the CNML file
        for link in self.getLinks():
            link.setLinkedParameters(self.devices, self.ifaces, self.nodes)

        # Fix: return False
        return True

    def load(self, validate=True):
        self.zones = dict()
        self.nodes = dict()
        self.devices = dict()
        self.services = dict()
        self.radios = dict()
        self.ifaces = dict()
        self.links = dict()

        if LXML:
            loaded = self.loadLxml(validate)
        else:
            loaded = self.loadMinidom(validate)

        if loaded:
            print 'Loaded "%s" successfully' % self.filename
        else:
            print 'There were some errors loading "%s"' % self.filename

        return loaded

    def getNodesFromZone(self, zid):
        if not self.loaded:
            self.load()
        return self.zones[zid].nodes.values()

    def getSubzonesFromZone(self, zid):
        if not self.loaded:
            self.load()
        return self.zones[zid].subzones.values()

    def getInterface(self, iid):
        if not self.loaded:
            self.load()
        return self.ifaces[iid]

    def getNode(self, nid):
        if not self.loaded:
            self.load()
        return self.nodes[nid]

    def getZone(self, zid):
        if not self.loaded:
            self.load()
        return self.zones[zid]

    def getLink(self, lid):
        if not self.loaded:
            self.load()
        return self.links[lid]

    def getDevice(self, did):
        if not self.loaded:
            self.load()
        return self.devices[did]

    def getZonesNames(self):
        if not self.loaded:
            self.load()

        return [z.title for z in self.getZones()]

    def getTitles(self):
        if not self.loaded:
            self.load()

        return [n.title for n in self.getNodes()]

    # Filename loaded
    def getFilename(self):
        return self.filename


# <interface> cuelga de <device> WTF?!:
#   <device created="20101105 0125" firmware="AirOsv52" id="25621" name="AirMaxM2 Bullet/PwBrg/AirGrd/NanoBr" status="Working" title="MLGInvisibleRd1" type="radio" updated="20110724 0113">
#       <radio antenna_gain="8" device_id="25621" id="0" mode="client" protocol="802.11b" snmp_name="ath0" ssid="MlagaMLGnvsbltmpRd1CPE0">
#           <interface id="48981" ipv4="10.228.172.36" mac="00:15:6D:4E:AF:13" mask="255.255.255.224" type="Wan">
#               <link id="28692" link_status="Working" link_type="ap/client" linked_device_id="19414" linked_interface_id="19414" linked_node_id="26999"/>
#           </interface>
#       </radio>
#       <interface id="48981" ipv4="10.228.172.36" mac="00:15:6D:4E:AF:13" mask="255.255.255.224" type="Wan"/>
#   </device>
