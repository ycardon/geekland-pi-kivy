#!/usr/local/bin/kivy
# -*- coding: utf-8 -*-

'''
Geekland remote by Yann Cardon
	https://github.com/ycardon
using phue by Nathanaël Lécaudé
	https://github.com/studioimaginaire/phue
using rgb_cie by Benjamin Knight
	https://github.com/benknight/hue-python-rgb-converter
'''

KODI_HOSTNAME = 'openelec.local'

HUE_HOSTNAME = '192.168.1.10'

KIVY_FONTS = [{
		'name': 'Glyph',
		'fn_regular': 'fonts/glyphicons-halflings-regular.ttf'
	}]

from kivy.app import App
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.network.urlrequest import UrlRequest
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.core.text import LabelBase

from phue import Bridge
from rgb_cie import Converter

import random
import json
import socket


# --- Init ---
for font in KIVY_FONTS:
	LabelBase.register(**font)

color_converter = Converter()

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
	lightSwitchs = []

	def __init__(self, **kwargs):
		super(LightPanel, self).__init__(**kwargs)
		for light in self.lights:
			ls = LightSwitch(light=light)
			self.add_widget(ls)
			self.lightSwitchs.append(ls)

	def party(self):
		for light in self.lights:
			light.brightness = 254
			light.xy = [random.random(), random.random()]

	def all_on(self, value):
		for ls in self.lightSwitchs:
			ls.ids.is_on.active = value

	def set_color(self):
		xy = color_converter.hexToCIE1931(self.ids.color_picker.hex_color[1:])
		for ls in self.lightSwitchs:
			if ls.ids.is_colorable.active:
				ls.light.xy = xy


# --- main widget ---
class GeeklandRemote(BoxLayout):
	pass

# --- main app ---
class GeeklandRemoteApp(App):
	def build(self):
		return GeeklandRemote()

if __name__ == '__main__':
	GeeklandRemoteApp().run()
