# -*- coding: utf-8 -*-
from util import *

class RADIO1:
		
	MENU_RADIO = [	
		'01|TBS FM|TBS:fm',
		'02|TBS eFM|TBS:efm',
		'03|CBS 음악FM|CBS:939',
		'04|CBS 표준FM|CBS:981',
		'05|EBS FM|EBS:fm',
		'06|EBS 외국어|EBS:foreign']

	# List
	def GetChannelList(self):
		ret = []
		for item in self.MENU_RADIO:
			info = {}
			info['id'], info['title'], info['param'] = item.split('|')
			info['summary'] = info['title']
			info['img'] = ''
			info['url'] = self.GetURL(info['param'])
			info['isTv'] = 'N'
			ret.append(info)
		return ret


	# URL
	def GetURL(self, param): 
		temp = param.split(':')
		if temp[0] == 'CBS':
			ret = 'http://aac.cbs.co.kr/cbs%s/_definst_/cbs%s.stream/playlist.m3u8' % (temp[1], temp[1])
		elif temp[0] == 'TBS':
			ret = 'http://tbs.hscdn.com/tbsradio/%s/playlist.m3u8' % temp[1]
		elif temp[0] == 'EBS':
			if temp[1] == 'fm': ret = 'http://58.229.187.43/fmradiobandiaod/bandiappaac/playlist.m3u8'
			else: ret = 'http://110.10.122.10/iradio/iradiolive_m4a/playlist.m3u8'
		return ret

	def GetURLFromID(self, id):
		for item in self.MENU_RADIO:
			temp = item.split('|')
			if temp[0] == id:
				return self.GetURL(temp[2])

	# M3U
	def MakeM3U(self, php):
		type = 'RADIO1'
		str = ''
		for item in self.MENU_RADIO:
			temp = item.split('|')
			#url = BROAD_URL % (php, type, temp[0])
			url = self.GetURL(temp[2])
			tvgid = '%s|%s' % (type, temp[0])
			tvgname = '%s|%s' % (type, temp[1])
			str += M3U_RADIO_FORMAT % (tvgid, tvgname, '', type, temp[1], url)
		return str

	def MakeEPG(self, prefix, channel_list=None):
		list = self.GetChannelList()
		str = ''
		count = 1200
		type_count = 0
		for item in self.GetChannelList():
			count += 1
			channel_number = count
			channel_name = item['title']
			#if len(channel_list['MBC']) == type_count: break
			if channel_list is not None:
				if item['id'] in channel_list['RADIO1']:
					type_count += 1
					channel_number = channel_list['RADIO1'][item['id']]['num']
					if len(channel_list['RADIO1'][item['id']]['name']) is not 0: channel_name = channel_list['RADIO1'][item['id']]['name']
				else:
					continue
			print('RADIO1 %s / %s make EPG' % (count, len(list)))
			str += '\t<channel id="RADIO1|%s" video-src="%surl&type=RADIO1&id=%s" video-type="HLS">\n' % (item['id'], prefix, item['id'])
			str += '\t\t<display-name>%s</display-name>\n' % channel_name
			str += '\t\t<display-name>%s</display-name>\n' % channel_number
			str += '\t\t<display-number>%s</display-number>\n' % channel_number
			if len(item['img']) != 0: str += '\t\t<icon src="%s" />\n' % item['img']
			str += '\t</channel>\n'
		return str



class RADIO2:
	def __init__( self, url ):
		self.URL = url

	# List
	def GetChannelList(self):
		try:
			list = []
			import xml.etree.ElementTree as ET
			request = urllib2.Request(self.URL)
			response = urllib2.urlopen(request)
			tree = ET.parse(response)
			root = tree.getroot()
			for item in root.findall('item'):
				info = {}
				info['id'] = info['img'] = info['summary'] = ''
				info['title'] = item.get('title')
				info['url'] = item.get('url')
				info['isTv'] = 'N'
				list.append(info)
			return list
		except Exception as e:
			pass

		try:
			list = []
			root = XML.ElementFromURL(self.URL, 0)
			for item in root.findall('item'):
				info = {}
				info['id'] = info['img'] = info['summary'] = ''
				info['title'] = item.get('title')
				info['url'] = item.get('url')
				info['isTv'] = 'N'
				list.append(info)
			return list
		except Exception as e:
			pass


	def MakeM3U(self, php):
		str = ''
		try:
			request = urllib2.Request(self.URL)
			response = urllib2.urlopen(request)
			import xml.etree.ElementTree as ET
			tree = ET.parse(response)
			root = tree.getroot()
			for item in root.findall('item'):
				str += M3U_RADIO_FORMAT % ('', '', '', 'RADIO2', item.get('title'), item.get('url'))
		except Exception as e:
			print(e)
			pass
		return str

	