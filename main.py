#!/usr/bin/kivy
# -*- coding: utf-8 -*-

'''
Geekland remote by Yann Cardon
	https://github.com/ycardon
using phue by Nathanaël Lécaudé
	https://github.com/studioimaginaire/phue
'''

KODI_HOSTNAME = 'openelec.local'
HUE_HOSTNAME = '192.168.1.10'

from kivy.app import App
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.network.urlrequest import UrlRequest
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.logger import Logger

from phue import Bridge

import random
import json
import socket

# --- Kodi Remote ---
class VideoPanel(BoxLayout):
	kody_url = 'http://' + socket.gethostbyname(KODI_HOSTNAME) + ':80/jsonrpc'

	def kodiRemote(self, key, param = None):
#		def log(req, results):
#			pass # TODO Logger.debug(results)

		body = {'jsonrpc': '2.0', 'method': key, 'id': 1}
		if param:
			body.update({'params': param})

		UrlRequest(
			url = self.kody_url,
#			on_success = log,
#			on_failure = log,
#			on_error = log,
			req_body = json.dumps(body),
			req_headers = {'Content-Type': 'application/json'},
			debug = True
		)


# --- Philips Hue remote ---
class KivyLight:
	pass

class LightSwitch(BoxLayout):
	light = ObjectProperty()

class LightPanel(BoxLayout):
	lights = Bridge(HUE_HOSTNAME).get_light_objects()

	def __init__(self, **kwargs):
		super(LightPanel, self).__init__(**kwargs)
		for light in self.lights:
			self.add_widget(LightSwitch(light=light))

	def party(self):
		for light in self.lights:
			light.brightness = 254
			light.xy = [random.random(), random.random()]

	def all_on(self, value):
		for light in self.lights:
			light.on = value


# --- main widget ---
class GeeklandRemote(BoxLayout):
	pass

# --- main app ---
class GeeklandApp(App):
	def build(self):
		return GeeklandRemote()

if __name__ == '__main__':
	GeeklandApp().run()
