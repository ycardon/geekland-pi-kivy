from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.network.urlrequest import UrlRequest
import json

KODI_URL = 'http://192.168.1.27:80'

class VideoPanel(BoxLayout):

	def kodiRemote_POST(self, body):
		UrlRequest(
			url = KODI_URL + '/jsonrpc',
			req_body = json.dumps(body),
			req_headers = {'Content-Type': 'application/json'},
			debug = True
		)

	def kodiRemote(self, key, param = None):
		body = {'jsonrpc': '2.0', 'method': key, 'id': 1}
		if param:
			body.update({'params': param})
		self.kodiRemote_POST(body)

class GeeklandApp(App):
	pass

if __name__ == '__main__':
	GeeklandApp().run()
