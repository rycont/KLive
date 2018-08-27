# -*- coding: utf-8 -*-
import urllib, urllib2
import json
from util import *

class KBS:
	#LIST
	def GetChannelList(self, includeURL = False):
		list = []
		url = 'http://onair.kbs.co.kr'
		request = urllib2.Request(url)
		response = urllib2.urlopen(request)
		data = response.read()
		idx1 = data.find('var channelList = JSON.parse') + 30
		idx2 = data.find(');', idx1)-1
		data = data[idx1:idx2].replace('\\', '')
		data = json.loads(data)
		for channel in data['channel']:
			for channel_master in channel['channel_master']:
				info = {}
				info['id'] = channel_master['channel_code']
				info['title'] = channel_master['title']
				info['isTv'] = 'Y' if channel_master['item'][0]['bitrate'].find('128') == -1 else 'N'
				info['img'] = channel_master['image_path_channel_logo']
				info['summary'] = '' # for kodi/plex addon
				list.append(info)
		return list

	#URL
	def GetURLWithLocalID(self, id):
		url = 'http://onair.kbs.co.kr/index.html?sname=onair&stype=live&ch_code=%s' % id
		request = urllib2.Request(url)
		response = urllib2.urlopen(request)
		data = response.read()
		idx1 = data.find('var channel = JSON.parse') + 26
		idx2 = data.find(');', idx1)-1
		data = data[idx1:idx2].replace('\\', '')
		data = json.loads(data)
		max = 0
		for item in data['channel_item']:
			tmp = int(item['bitrate'].replace('Kbps', ''))
			if tmp > max:
				ret = item['service_url']
				max = tmp
		return ret

	# M3U
	def MakeM3U(self, php):
		type = 'KBS'
		str = ''
		for item in self.GetChannelList():
			url = BROAD_URL % (php, type, item['id'])
			tvgid = '%s|%s' % (type, item['id'])
			tvgname = '%s|%s' % (type, item['title'])
			if item['isTv'] == 'Y':
				str += M3U_FORMAT % (tvgid, tvgname, item['img'], type, item['title'], url)
			else :
				str += M3U_RADIO_FORMAT % (tvgid, tvgname, item['img'], 'RADIO1', item['title'], url)				
		return str
