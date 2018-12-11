# -*- coding: utf-8 -*-
from util import *

class KBS:
	#LIST
	def GetChannelList(self):
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
				info['isTv'] = 'N' if len(channel_master['item']) > 0 and channel_master['item'][0]['bitrate'].find('128') != -1 else 'Y'
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

	def MakeEPG(self, prefix, channel_list=None):
		from pooq import *
		list = self.GetChannelList()
		str = ''
		count = 0
		type_count = 0
		pooq = POOQ()
		for item in self.GetChannelList():
			count += 1
			channel_number = count
			channel_name = item['title']
			if channel_list is not None:
				if len(channel_list['KBS']) == type_count: break
				if item['id'] in channel_list['KBS']:
					type_count += 1
					channel_number = channel_list['KBS'][item['id']]['num']
					if len(channel_list['KBS'][item['id']]['name']) is not 0: channel_name = channel_list['KBS'][item['id']]['name']
				else:
					continue
			print('KBS %s / %s make EPG' % (count, len(list)))
			str += '\t<channel id="KBS|%s" video-src="%surl&type=KBS&id=%s" video-type="HLS">\n' % (item['id'], prefix, item['id'])
			str += '\t\t<display-name>%s</display-name>\n' % channel_name
			str += '\t\t<display-name>%s</display-name>\n' % channel_number
			str += '\t\t<display-number>%s</display-number>\n' % channel_number
			str += '\t\t<icon src="%s" />\n' % item['img']
			str += '\t</channel>\n'
			if item['id'] in self.pooq_id:
				str += pooq.MakeEPG_ID(self.pooq_id[item['id']], 'KBS|%s' % item['id'])
		return str

	pooq_id = {
			'11' : 'K01',
			'12' : 'K02',
			'N91' : 'K06',
			'N92' : 'K04',
			'N94' : 'K09',
			'N93' : 'K05',
		}
