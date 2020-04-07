try:
    import polyinterface
except:
    import pgc_interface as polyinterface

LOGGER = polyinterface.LOGGER

FAN_LEVEL = ["low", "medium", "high", "auto", "not supported"]
MODES = ['cool', 'heat', 'fan']
MODE_COUNTER = { 'cool': 2, 'heat': 1, 'fan': 6 }

class SensiboNode(polyinterface.Node):
    def __init__(self, controller, primary, address, data, api):
        super().__init__(controller, primary, address, data['room']['name'])
        self.api = api
        self.data = data
        self.deviceId = data['id']
        self._update(data)

    def update(self, data):
        for dv in data:
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
        {'driver': 'ST', 'value': 0, 'uom': 25},
        {'driver': 'GV0', 'value': 0, 'uom': 2},
        {'driver': 'GV1', 'value': 0, 'uom': 57},
        {'driver': 'GV2', 'value': 0, 'uom': 25},
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