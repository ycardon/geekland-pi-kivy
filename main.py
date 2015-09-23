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

from kivy.app import App
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ObjectProperty
from kivy.network.urlrequest import UrlRequest
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.core.text import LabelBase

from phue import Bridge
from rgb_cie import Converter
from ConfigParser import ConfigParser

import random
import json
import socket

# --- Init ---
config = ConfigParser()
config.read('geeklandremote.ini')
KODI_HOSTNAME = config.get('kodi', 'hostname')
HUE_HOSTNAME = config.get('hue', 'hostname')
FORECAST_URL = str.format(
	'https://api.forecast.io/forecast/{0}/{1},{2}?units=si',
	config.get('forecast', 'api_key'),
	config.get('forecast', 'latitude'),
	config.get('forecast', 'longitude'))

color_converter = Converter()

KIVY_FONTS = [{'name': 'Glyph', 'fn_regular': 'fonts/glyphicons-halflings-regular.ttf'}]
for font in KIVY_FONTS:
	LabelBase.register(**font)


# --- Weather ---
class WeatherPanel(BoxLayout):
	temperature = NumericProperty()

	def getWeatherCallback(self, req, results):
		print(results)
		self.temperature = results['hourly']['data'][0]['temperature']

	def getWeather(self):
		UrlRequest(FORECAST_URL, self.getWeatherCallback)


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
	lightSwitchs = []

	def __init__(self, **kwargs):
		super(LightPanel, self).__init__(**kwargs)
		for light in Bridge(HUE_HOSTNAME).get_light_objects():
			ls = LightSwitch(light=light)
			self.add_widget(ls)
			self.lightSwitchs.append(ls)

	def party(self):
		for ls in self.lightSwitchs:
			ls.light.brightness = 254
			ls.light.xy = [random.random(), random.random()]

	def all_on(self, value):
		for ls in self.lightSwitchs:
			ls.ids.is_on.active = value

	def set_color(self):
		xy = color_converter.hexToCIE1931(self.ids.color_picker.hex_color[1:])
		for ls in self.lightSwitchs:
			if ls.ids.is_colorable.active:
				ls.light.xy = xy

	def check_all(self, value):
		for ls in self.lightSwitchs:
			if value == None:
				ls.ids.is_colorable.active = not(ls.ids.is_colorable.active)
			else:
				ls.ids.is_colorable.active = value


# --- main widget ---
class GeeklandRemote(BoxLayout):
	pass

# --- main app ---
class GeeklandRemoteApp(App):
	def build(self):
		return GeeklandRemote()

if __name__ == '__main__':
	GeeklandRemoteApp().run()
