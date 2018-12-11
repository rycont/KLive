# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib
import json, re
import os
from util import *


class SBS:
	MENU_SBS = [
		'S01|SBS|Y|http://i.imgur.com/K2ztoDT.png',
		'S03|SBS Plus|Y|http://i.imgur.com/asfyrTm.png',
		'S02|SBS Sports|Y|http://i.imgur.com/j1vHAu6.png',
		'S05|SBS Golf|Y|http://i.imgur.com/HdS0GNV.png',
		'S06|SBS CNBC|Y|http://i.imgur.com/SfDs4qN.png',
		'S04|SBS funE|Y|http://i.imgur.com/D1EYJmr.png',
		'S09|SBS MTV|Y|http://i.imgur.com/OeSJ9Ik.png',
		'S07|SBS 파워FM|N|http://img.pooq.co.kr/BMS/ChannelImg/SBSpowerFM_730x411.jpg',
		'S17|SBS 파워FM 보라|B|http://img.pooq.co.kr/BMS/ChannelImg/SBSpowerFM_730x411.jpg',
		'S08|SBS 러브FM|N|http://img.pooq.co.kr/BMS/ChannelImg/SBSloveFM_730x411.jpg',
		'S18|SBS 러브FM 보라|B|http://img.pooq.co.kr/BMS/ChannelImg/SBSloveFM_730x411.jpg' 
		]
	
	COOKIE_FILENAME = 'sbs2.txt'

	#Login
	def DoLogin(self, id, pw):
		url = 'https://join.sbs.co.kr/login/login.do?div=pc_login'
		request = urllib2.Request(url)
		response = urllib2.urlopen(request)
		data = response.read()
		regax = 'loginPageCheck\"\svalue\=\"(.*?)\"'
		r = re.compile(regax)
		m = r.findall(data)
		loginPageCheck = m[0]
		
		url = 'https://join.sbs.co.kr/login/loginChk.do'
		params = {	'returnUrl' : '',
				'web_app' : '',
				'lang' : 'k',
				'loginPageCheck' : loginPageCheck,
				'id' : id,
				'passwd' : pw, }
		ret = ''
		cj = cookielib.CookieJar()
		cookieprocessor = urllib2.HTTPCookieProcessor(cj)
		opener = urllib2.build_opener(urllib2.HTTPRedirectHandler, cookieprocessor)
		urllib2.install_opener(opener)
		postdata = urllib.urlencode(params)
		response =urllib2.urlopen(url, postdata )
		for cookie in cj:
			if cookie.name == 'LOGIN_JWT':
				ret = cookie.value
				break
		cj.clear_session_cookies()
		#if ret != '':
			#logindata = '%s=%s' % ('LOGIN_JWT', ret)
			#WriteFile(self.COOKIE_FILENAME, ret)
		return ret
	
	def DoLoginFromSC(self, id, pw):
		try:
			if not os.path.isfile(GetFilename(self.COOKIE_FILENAME)):
				ret = self.DoLogin(id, pw)
				if len(ret) != 0: WriteFile(GetFilename(self.COOKIE_FILENAME), ret)
			else:	
				create_time = os.path.getctime(GetFilename(self.COOKIE_FILENAME))
				diff = time.gmtime(time.time() - create_time)
				if diff.tm_mday > 1:
					ret = self.DoLogin(id, pw)
					if len(ret) != 0: WriteFile(GetFilename(self.COOKIE_FILENAME), ret)
		except Exception as e:
			#print(e)
			pass
	
	# List
	def GetChannelList(self):
		token = ''
		list = []
		for item in self.MENU_SBS:
			try:
				temp = item.split('|')
				info = {}
				info['title'] = temp[1]
				url = 'http://apis.sbs.co.kr/play-api/1.0/onair/channel/%s?v_type=2&platform=pcweb&protocol=hls&jwt-token=%s' % (temp[0], '')
				request = urllib2.Request(url)
				response = urllib2.urlopen(request)
				data = json.load(response, encoding='utf8')
				info['summary'] = data['onair']['info']['title']
				#info['img'] = data['onair']['info']['thumbimg']
				info['img'] = temp[3]
				info['url'] = data['onair']['source']['mediasource']['mediaurl']
				info['id'] = temp[0]
				info['isTv'] = temp[2]
				list.append(info)
			except Exception as e:
				#LOG(e)
				pass
		return list
	
	# URL
	def GetURL(self, id):
		try:
			token = ReadFile(GetFilename(self.COOKIE_FILENAME)) if os.path.exists ( GetFilename(self.COOKIE_FILENAME) ) else ''

			url = 'http://apis.sbs.co.kr/play-api/1.0/onair/channel/%s?v_type=2&platform=pcweb&protocol=hls&jwt-token=%s' % (id, token)
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			data = json.load(response, encoding='utf8')
			#data = response.read()
			#print(data)
			return data['onair']['source']['mediasource']['mediaurl']
		except:
			return None

	# M3U
	def MakeM3U(self, php):
		type = 'SBS'
		str = ''
		for item in self.MENU_SBS:
			temp = item.split('|')
			url = BROAD_URL % (php, type, temp[0])
			tvgid = '%s|%s' % (type, temp[0])
			#tvgname = '%s|%s' % (type, temp[1])
			t = temp[1].replace('보라', '').strip()
			tvgname = '%s|%s' % ('SBS', t)
			if temp[2] == 'Y':
				str += M3U_FORMAT % (tvgid, tvgname, temp[3], type, temp[1], url)
			else :
				str += M3U_RADIO_FORMAT % (tvgid, tvgname, temp[3], 'RADIO1', temp[1], url)
				
		return str

	def MakeEPG(self, prefix, channel_list=None):
		from pooq import *
		list = self.GetChannelList()
		str = ''
		count = 90
		type_count = 0
		pooq = POOQ()

		for item in self.GetChannelList():
			count += 1
			channel_number = count
			channel_name = item['title']
			if channel_list is not None:
				if len(channel_list['SBS']) == type_count: break
				if item['id'] in channel_list['SBS']:
					type_count += 1
					channel_number = channel_list['SBS'][item['id']]['num']
					if len(channel_list['SBS'][item['id']]['name']) is not 0: channel_name = channel_list['SBS'][item['id']]['name']
				else:
					continue
			print('SBS %s / %s make EPG' % (count, len(list)))
			str += '\t<channel id="SBS|%s" video-src="%surl&type=SBS&id=%s" video-type="HLS">\n' % (item['id'], prefix, item['id'])
			str += '\t\t<display-name>%s</display-name>\n' % channel_name
			str += '\t\t<display-name>%s</display-name>\n' % channel_number
			str += '\t\t<display-number>%s</display-number>\n' % channel_number
			str += '\t\t<icon src="%s" />\n' % item['img']
			str += '\t</channel>\n'

			if item['id'] in self.pooq_id:
				str += pooq.MakeEPG_ID(self.pooq_id[item['id']], 'SBS|%s' % item['id'])

		return str

	pooq_id = {
			'S01' : 'S01',
			'S03' : 'S03',
			'S02' : 'S02',
			'S06' : 'S06',
			'S04' : 'S04',
			'S09' : 'S09',
			'S07' : 'S07',
			'S08' : 'S08',
		}
