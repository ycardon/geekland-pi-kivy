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
		body = {'jsonrpc': '2.0', 'method': key, 'id': 1}
		if param:
			body.update({'params': param})

		UrlRequest(
			url = self.kody_url,
			req_body = json.dumps(body),
			req_headers = {'Content-Type': 'application/json'},
			debug = True
		)


# --- Philips Hue remote ---
class LightSwitch(BoxLayout):
	light = ObjectProperty()

class LightPanel(BoxLayout):
	lights = Bridge(HUE_HOSTNAME).get_light_objects()
	childs = []

	def __init__(self, **kwargs):
		super(LightPanel, self).__init__(**kwargs)
		for light in self.lights:
			child = LightSwitch(light=light)
			self.add_widget(child)
			self.childs.append(child)

	def party(self):
		for light in self.lights:
			light.brightness = 254
			light.xy = [random.random(), random.random()]

	def all_on(self, value):
		for child in self.childs:
			child.ids.is_on.active = value


# --- main widget ---
class GeeklandRemote(BoxLayout):
	pass

# --- main app ---
class GeeklandApp(App):
	def build(self):
		return GeeklandRemote()

if __name__ == '__main__':
	GeeklandApp().run()
