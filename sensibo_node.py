import udi_interface

LOGGER = udi_interface.LOGGER

FAN_LEVEL = ["low", "medium", "high", "auto", "not supported"]
MODES = ['cool', 'heat', 'fan', 'dry', 'auto']

# Not sure about this. Shouldn't this match modes above?
#MODE-0 = Cool
#MODE-1 = Heat
#MODE-2 = Fan
#MODE-3 = Dry
#MODE-4 = Auto

#MODE_COUNTER = { 'cool': 2, 'heat': 1, 'fan': 6 }
#
# Try this instead???
MODE_COUNTER = { 'cool': 0, 'heat': 1, 'fan': 2, 'dry': 3, 'auto': 4 }

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

            Certainly if we call it with fields="*"
            '''

            try:
                dinfo = self.api.device(self.deviceId)
                LOGGER.debug ('device info = {}'.format(dinfo))
                self._update(dinfo)
            except Exception as e:
                LOGGER.error ('Device query failed: {}'.format(e))

    def _update(self, data):
        '''
        temperatureUnit: string F or C
        acState.on (true/false)
        acState.mode (string)
        acState.targetTemperature (in units specified above)
        acState.fanLevel: (string)

        measurements.time.secondsAgo
        measurements.temperature (in native units (C))
        measurements.humidity (in percent)
        measurements.feelslike (in native units (C))
        measurements.rssi 

        connectionStatus.isAlive  (true/false)
        connectionStatus.lastSeen.secondsAgo (seconds)
        '''

        temp = data['measurements']['temperature']

        if data['temperatureUnit'] == 'C':
            temp_uom = 4
        else:
            temp_uom = 17
            temp = round(((temp * 9) / 5) + 32, 1)

        self.setDriver('ST', 1 if data['acState']['on'] else 0)
        # target temp units should match temperatureUnit
        self.setDriver('CLITEMP', temp, uom=temp_uom )
        self.setDriver('CLIHUM', data['measurements']['humidity'], uom=51)
        self.setDriver('CLIMD', MODE_COUNTER[data['acState']['mode']])
        self.setDriver('GV0', 1 if data['connectionStatus']['isAlive'] else 0)
        self.setDriver('GV1', data['connectionStatus']['lastSeen']['secondsAgo'])

        # target temp units should match temperatureUnit
        self.setDriver('GV2', data['acState']['targetTemperature'], uom=temp_uom)

        try:
            if(data['acState']['fanLevel'] in FAN_LEVEL):
                self.setDriver('CLIFRS', FAN_LEVEL.index(data['acState']['fanLevel']))
            else:
                self.setDriver('CLIFRS', FAN_LEVEL.index("not supported"))
        except:
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
        '''
        User can select a target temperature in either C or F but
        the API wants it in C.

        Show the user what they set using the units they chose but
        if the preferred units are different, the next query will 
        change it back to those units.
        '''
        try:
            temp = int(param['value'])
            self.setDriver('GV2', temp, uom=param['uom'])

            if param['uom'] == 17:
                # expects temp in C?
                temp = round(((temp - 32) * 5) / 9, 0)

            self._changeProperty('targetTemperature', temp)
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
        {'driver': 'GV2', 'value': 0, 'uom': 4},      # target temperature
        {'driver': 'CLIFRS', 'value': 0, 'uom': 25},
        {'driver': 'CLITEMP', 'value': 10, 'uom': 4},
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
