#!/usr/bin/env python3

import udi_interface
import json
from sensibo_api import SensiboAPI
from sensibo_node import SensiboNode

LOGGER = udi_interface.LOGGER

class Controller(object):
    def __init__(self, polyglot):
        super(Controller, self).__init__()
        self.poly = polyglot
        self.name = 'Sensibo Controller'
        self.api_key = ''
        self.scanning = False

        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.DISCOVER, self.discover)

        polyglot.updateProfile()
        polyglot.ready()
    
    def parameterHandler(self, params):
        self.poly.Notices.clear()

        if 'api_key' in params and params['api_key'] != '':
            self.api_key = params['api_key']
            self.discover()
        else:
            LOGGER.info('Missing api_key value.')
            self.poly.Notices['api'] = 'Please define Sensibo API key'


    def discover(self, *args, **kwargs):
        self.scanning = True
        LOGGER.info('Scanning mode in process')

        try:
            sensibo = SensiboAPI(self.api_key)
            devices = sensibo.devices()
            
            if(self.api_key != ''):
                for dv in devices:
                    LOGGER.info(dv['id'])
                    if not self.poly.getNode(dv['id'].lower()):
                        self.poly.addNode(SensiboNode(self.poly, dv['id'].lower(), dv['id'].lower(), dv, sensibo))

        except Exception as err:
            LOGGER.info('Scanning fail', err)
        else:
            LOGGER.info('Scanning finished')

        self.scanning = False

    def stop(self):
        LOGGER.info('Sensibo NodeServer Stopped')

if __name__ == '__main__':
    try:
        polyglot = udi_interface.Interface('SensiboNodeServer')
        polyglot.start('2.0.7')
        Controller(polyglot)
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
