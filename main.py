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
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ObjectProperty, ListProperty
from kivy.network.urlrequest import UrlRequest
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.core.text import LabelBase

from phue import Bridge
from rgb_cie import Converter
from ConfigParser import ConfigParser

import json
import socket
import time

# --- Init ---

# consts from config file
config = ConfigParser()
config.read('geeklandremote.ini')
KODI_HOSTNAME = config.get('kodi', 'hostname')
HUE_HOSTNAME = config.get('hue', 'hostname')
FORECAST_URL = str.format(
	'https://api.forecast.io/forecast/{0}/{1},{2}?units=si',
	config.get('forecast', 'api_key'),
	config.get('forecast', 'latitude'),
	config.get('forecast', 'longitude'))

# factories
color_converter = Converter()

# fonts
KIVY_FONTS = [
	{'name': 'Glyphicons', 'fn_regular': 'fonts/glyphicons-halflings-regular.ttf'},
	{'name': 'Octicons', 'fn_regular': 'fonts/octicons.ttf'}]
for font in KIVY_FONTS:
	LabelBase.register(**font)

# waiting for network
while True:
	try:
		socket.gethostbyname(KODI_HOSTNAME)
		break
	except:
		print('GeeklandRemote is waiting for network')
		time.sleep(1)


# --- Main ---
class MainPanel(BoxLayout):
	ip = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

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
	light = ObjectProperty() # FIXME useful ?

	# set light and linked lights on/off
	def set_on(self, active): # TODO potential loop
		self.light.on = active
		for ls in self.parent.lightSwitchs:
			if ls.ids.is_linked.active:
				ls.ids.is_on.active = active

	# set light and linked lights brightness
	def set_brightness(self, value): # TODO potential loop
		self.light.brightness = int(value)
		for ls in self.parent.lightSwitchs:
			if ls.ids.is_linked.active:
				ls.ids.is_brightness.value = value

class LightPanel(BoxLayout):
	lightSwitchs = ListProperty()

	def __init__(self, **kwargs):
		super(LightPanel, self).__init__(**kwargs)
		for light in Bridge(HUE_HOSTNAME).get_light_objects():
			ls = LightSwitch(light=light)
			self.add_widget(ls)
			self.lightSwitchs.append(ls)

	# light all/none
	def all_on(self, value):
		for ls in self.lightSwitchs:
			ls.ids.is_on.active = value

	# set colors for selected lights
	def set_color(self):
		xy = color_converter.hexToCIE1931(self.ids.color_picker.hex_color[1:])
		for ls in self.lightSwitchs:
			if ls.ids.is_linked.active:
				ls.light.xy = xy

	# select all/none/invert lights
	def check_all(self, value):
		for ls in self.lightSwitchs:
			if value == None:
				ls.ids.is_linked.active = not(ls.ids.is_linked.active)
			else:
				ls.ids.is_linked.active = value

	# apply preset to all lights
	def preset(self, hex_color, brightness):
		xy = color_converter.hexToCIE1931(hex_color[1:])
		for ls in self.lightSwitchs:
			ls.ids.is_on.active = True
			ls.ids.is_brightness.value = brightness
			ls.light.xy = xy

	def preset_bright(self):
		self.preset('#ffdfcc', 254)

	def preset_soft(self):
		self.preset('#ff9f65', 20)


# --- main widget ---
class GeeklandRemote(BoxLayout):
	pass

# --- main app ---
class GeeklandRemoteApp(App):
	def build(self):
		return GeeklandRemote()

if __name__ == '__main__':
	GeeklandRemoteApp().run()
