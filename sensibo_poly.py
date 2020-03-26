#!/usr/bin/env python3

try:
    import polyinterface
except:
    import pgc_interface as polyinterface

import json

from sensibo_api import SensiboAPI
from sensibo_node import SensiboNode

LOGGER = polyinterface.LOGGER

class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Sensibo Controller'
        self.api_key = 'YourApiKey'
        self.scanning = False
    
    def start(self):
        LOGGER.info('Sensibo NodeServer Starting')
        self.check_params()
        self.setDriver('ST', 1)
        LOGGER.info('Sensibo NodeServer Started')

    def shortPoll(self):
        if(self.scanning):
            LOGGER.info('Skipping shortPoll() - NodeServer in scanning mode')
        else:
            sensibo = SensiboAPI(self.api_key)
            devices = sensibo.devices()
            for node in self.nodes:
                self.nodes[node].update(devices)

    def longPoll(self):
        if(self.scanning):
            LOGGER.info('Skipping longPoll() - NodeServer in scanning mode')
        else:
            sensibo = SensiboAPI(self.api_key)
            devices = sensibo.devices()
            for node in self.nodes:
                self.nodes[node].update(devices)

    def query(self):
        self.reportDrivers()

    def discover(self, *args, **kwargs):
        self.scanning = True
        LOGGER.info('Scanning mode in process')

        try:
            sensibo = SensiboAPI(self.api_key)
            devices = sensibo.devices()
            
            if(self.api_key != 'YourApiKey'):
                for dv in devices:
                    LOGGER.info(dv['id'])
                    self.addNode(SensiboNode(self, self.address, dv['id'].lower(), dv, sensibo))

        except(err):
            LOGGER.info('Scanning fail', err)
        else:
            LOGGER.info('Scanning finished')

        self.scanning = False

    def stop(self):
        self.setDriver('ST', 0)
        LOGGER.info('Sensibo NodeServer Stopped')

    def check_params(self):
        if('api_key' in self.polyConfig['customParams']):
            self.api_key = self.polyConfig['customParams']['api_key']

        self.removeNoticesAll()
        self.addCustomParam({'api_key': self.api_key})

        if(self.api_key == 'YourApiKey'):
            self.addNotice('Please define Sensibo API key')
        else:
            self.discover()
        
        self.reportDrivers()

    def update(self, data):
        pass

    id = 'controller'
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]
    commands = {'DISCOVER': discover}


if __name__ == '__main__':
    try:
        polyglot = polyinterface.Interface('SensiboNodeServer')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
