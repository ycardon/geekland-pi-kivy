#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Geekland remote by Yann Cardon
https://github.com/ycardon
'''

KODI_URL = 'http://192.168.1.27:80'
HUE_IP = '192.168.1.10'

from kivy.app import App
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.network.urlrequest import UrlRequest
from kivy.logger import Logger
from phue import Bridge
import random
import json


# --- Kodi Remote ---
class VideoPanel(BoxLayout):

	def kodiRemote_POST(self, body):
		def log(req, results):
			#Logger.debug(results)
			pass

		UrlRequest(
			url = KODI_URL + '/jsonrpc',
			on_success = log,
			on_failure = log,
			on_error = log,
			req_body = json.dumps(body),
			req_headers = {'Content-Type': 'application/json'},
			debug = True
		)

	def kodiRemote(self, key, param = None):
		body = {'jsonrpc': '2.0', 'method': key, 'id': 1}
		if param:
			body.update({'params': param})
		self.kodiRemote_POST(body)


# --- Philips Hue remote ---
class LightSwitch(BoxLayout):
	light = ObjectProperty()
	
	def switched(self, instance, value):
		self.light.on = value

class LightPanel(BoxLayout):
	bridge = Bridge(HUE_IP)

	def __init__(self, **kwargs):
		super(LightPanel, self).__init__(**kwargs)
		for light in self.bridge.get_light_objects():
			self.add_widget(LightSwitch(light=light))

	def party(self):
		lights = self.b.get_light_objects()
		for light in lights:
			light.brightness = 254
			light.xy = [random.random(), random.random()]

	def info(self):
		print(self.b.get_light_objects())


# --- main ---
class GeeklandApp(App):
	pass

if __name__ == '__main__':
	GeeklandApp().run()
