import requests
import json

URI = 'https://home.sensibo.com/api/v2'

class SensiboAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def _get(self, path, **params):
        params['apiKey'] = self.api_key
        response = requests.get(URI + path, params = params)
        response.raise_for_status()
        return response.json()

    def _patch(self, path, data, **params):
        params['apiKey'] = self.api_key
        response = requests.patch(URI + path, params = params, data = data)
        response.raise_for_status()
        return response.json()

    def _post(self, path, data, **params):
        params['apiKey'] = self.api_key
        response = requests.post(URI + path, params = params, data = data)
        response.raise_for_status()
        return response.json()

    def device(self, id, fields="*"):
        response = self._get('/pods/%s' % id, fields = fields)
        return response['result']

    def devices(self, fields='*'):
        response = self._get('/users/me/pods', fields = fields)
        return response['result']

    def update(self, id, currentAcState, property, value):
        data = json.dumps({ 'currentAcState': currentAcState, 'newValue': value })
        response = self._patch("/pods/%s/acStates/%s" % (id, property), data)
        return response['result'] 
