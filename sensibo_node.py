import udi_interface

LOGGER = udi_interface.LOGGER

FAN_LEVEL = ["low", "medium", "high", "auto", "not supported"]
MODES = ['cool', 'heat', 'fan', 'dry', 'auto']
MODE_COUNTER = { 'cool': 2, 'heat': 1, 'fan': 6 }

class SensiboNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, data, api):
        super().__init__(polyglot, primary, address, data['room']['name'])
        self.poly = polyglot
        self.api = api
        self.deviceId = data['id']
        self.data = data
        self._update(data)

        polyglot.subscribe(polyglot.POLL, self.update)

    def update(self, pollflag):
        if pollflag == 'shortPoll':
            '''
            Could we call self.api.device(self.deviceId) instead to just
            get the info for the one device?
            '''
            devices = self.api.devices()
            for dv in devices:
                if dv['id'].lower() == self.address:
                    self._update(dv)

    def _update(self, data):
        self.setDriver('ST', 1 if data['acState']['on'] else 0)
        self.setDriver('CLITEMP', data['measurements']['temperature'])
        self.setDriver('CLIHUM', data['measurements']['humidity'])
        self.setDriver('CLIMD', MODE_COUNTER[data['acState']['mode']])
        self.setDriver('GV0', 1 if data['connectionStatus']['isAlive'] else 0)
        self.setDriver('GV1', data['connectionStatus']['lastSeen']['secondsAgo'])
        self.setDriver('GV2', data['acState']['targetTemperature'])

        if(data['acState']['fanLevel'] in FAN_LEVEL):
            self.setDriver('CLIFRS', FAN_LEVEL.index(data['acState']['fanLevel']))
        else:
            self.setDriver('CLIFRS', FAN_LEVEL.index("not supported"))

    def _changeProperty(self, property, value):
        return self.api.update(self.deviceId, self.data['acState'], property, value)

    def setOn(self, param):
        try:
            self._changeProperty('on', True)
            self.setDriver('ST', 1)
        except:
            LOGGER.debug('SET ON: communication fail')

    def setOff(self, param):
        try:
            self._changeProperty('on', False)
            self.setDriver('ST', 0)
        except:
            LOGGER.debug('SET OFF: communication fail')

    def setTemperature(self, param):
        try:
            self._changeProperty('targetTemperature', int(param['value']))
            self.setDriver('GV2', int(param['value']))
        except:
            LOGGER.debug('SET TEMPERATURE: communication fail')

    def setFan(self, param):
        try:
            self._changeProperty('fanLevel', FAN_LEVEL[int(param['value'])])
            self.setDriver('CLIFRS', int(param['value']))
        except:
            LOGGER.debug('SET FAN: communication fail')

    def setMode(self, param):
        try:
            self._changeProperty('mode', MODES[int(param['value'])])
            self.setDriver('CLIMD', MODE_COUNTER[MODES[int(param['value'])]])
        except:
            LOGGER.debug('SET MODE: communication fail')

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 25},       # device state
        {'driver': 'GV0', 'value': 0, 'uom': 2},       # connection status
        {'driver': 'GV1', 'value': 0, 'uom': 57},      # connection last seen
        {'driver': 'GV2', 'value': 0, 'uom': 25},      # target temperature
        {'driver': 'CLIFRS', 'value': 0, 'uom': 25},
        {'driver': 'CLITEMP', 'value': 10, 'uom': 56},
        {'driver': 'CLIHUM', 'value': 0, 'uom': 51},
        {'driver': 'CLIMD', 'value': 0, 'uom': 67},
        {'driver': 'PWR', 'value': 0, 'uom': 25}
    ]

    id = 'sensibo'

    commands = {
        'DON': setOn,
        'DOF': setOff,
        'SET_TEMPERATURE': setTemperature,
        'SET_FAN': setFan,
        'SET_MODE': setMode
    }
