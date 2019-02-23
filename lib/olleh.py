# -*- coding: utf-8 -*-
from util import *

class OLLEH:
	COOKIE_FILENAME = 'olleh2.txt'
	USER_AGENT = 'OMS (compatible;ServiceType/OTM;DeviceType/WIN8PAD;DeviceModel/AllSeries;OSType/WINM;OSVersion/8.1.0;AppVersion/1.2.1.9))'

	# Login
	def DoLoginFromSC(self, id, pw):
		try:
			if not os.path.isfile(GetFilename(self.COOKIE_FILENAME)):
				self.DoLogin(id, pw)
			else:	
				create_time = os.path.getctime(GetFilename(self.COOKIE_FILENAME))
				diff = time.gmtime(time.time() - create_time)
				if diff.tm_mday > 1:
					self.DoLogin(id, pw)
		except:
			pass

	def DoLogin(self, id, pw ):
		timestamp = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S%f')[:-3])
		transactionid = str(timestamp) + '000000000000001'
		headers = {'User-Agent': self.USER_AGENT, 'Transactionid': transactionid, 'Requesthostname': 'android.otm.kt.com', 'Timestamp': timestamp, 'Applicationkey': 'otmapp42test', 'Content-Type': 'application/json'}
		try:
			url = 'https://omas.megatvdnp.co.kr/login/olleh'
			params = {'userId': id, 'userPwd': pw}
			request = urllib2.Request(url, headers = headers, data = json.dumps(params))
			response = urllib2.urlopen(request)
			content = json.load(response, encoding="utf-8")
			toknVal = content['accList'][0]['toknVal']
			svcUniqId = content['accList'][0]['svcUniqId']
			circuitSaid = content['accList'][0]['circuitSaid']
			autoLoginYn = content['accList'][0]['regYn']
						
			url = 'https://omas.megatvdnp.co.kr/login/device/prov'
			params = {'toknVal': toknVal, 'svcUniqId': svcUniqId, 'circuitSaid': circuitSaid, 'termlUserAgent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36', 'termlDeviceId': '224B29B0FD52', 'autoLoginYn': autoLoginYn, 'appDivCd': 'MOBILE_AND'}

			cj = cookielib.CookieJar()
			cookieprocessor = urllib2.HTTPCookieProcessor(cj)
			opener = urllib2.build_opener(cookieprocessor)
			request = urllib2.Request(url, headers = headers, data = json.dumps(params))
			response = opener.open(request)
			ret = ''
			for cookie in cj:
				ret += '%s=%s;' % (cookie.name, cookie.value)
			cj.clear_session_cookies()
			if ret != '':
				dic = {}
				dic['cookie'] = ret
				file = open(GetFilename(self.COOKIE_FILENAME), 'wb')
				pickle.dump(dic, file)
				file.close()

			#WriteFile(GetFilename(self.COOKIE_FILENAME), ret)
		except Exception as e:
			print(e)
		return cookie

	def GetLoginData(self):
		try:
			file = open(GetFilename(self.COOKIE_FILENAME), 'rb')
			login = pickle.load(file)
			file.close()
			return login['cookie']
			#return ReadFile(GetFilename(self.COOKIE_FILENAME))
		except Exception, e:
			pass
		return None

	# List
	def GetChannelList(self):
		result = []
		cookie = self.GetLoginData()
		url = 'http://menu.megatvdnp.co.kr:38080/app5/0/api/epg_chlist?istest=0&category_id=1'
		request = urllib2.Request(url, headers = {'User-Agent': self.USER_AGENT})
		response = urllib2.urlopen(request)
		data = json.load(response, encoding="utf-8")
		for item in data['data']['list'][0]['list_channel']:
			info = {}
			info['id'] = item['ch_no']
			info['title'] = item['service_ch_name'].replace(',', ' ')
			info['img'] = item['ch_image_list']
			info['isTv'] = 'Y' if item['type'] != 'AUDIO_MUSIC' else 'N'
			if item['adult_yn'] == 'N': result.append(info)
			from urllib import unquote
			info['summary'] = unquote(item['program_name'].encode('utf8'))
			info['summary'] = info['summary'].replace('+', ' ')
		return result

	# URL
	def GetURL(self, id, quality):
		try:
			if id[-1:] == 'A': 
				id = id[:-1]
				quality = '128' 
			cookie = self.GetLoginData()
			#ReadFile(GetFilename(self.COOKIE_FILENAME))
			params = {'istest': '0', 'ch_no': id, 'bit_rate': 'S', 'bit_rate_option': quality, 'user_model': 'Redmi', 'user_os': '6.0.1', 'user_type': 'Android', 'user_net': 'WIFI'}
			url = 'http://menu.megatvdnp.co.kr:38080/app5/0/api/epg_play?%s' % urllib.urlencode( params )
			request = urllib2.Request(url, headers = {'Cookie': cookie, 'User-Agent': self.USER_AGENT})
			response = urllib2.urlopen(request)
			data = json.load(response, encoding="utf-8")
			return data['data']['live_url']
		except Exception as e:
			#print(e)
			pass
		return

	def GetURLFromSC(self, code, quality):
		return self.GetURL(code, quality)

	
	# M3U
	def MakeM3U(self, php):
		type = 'OLLEH'
		str = ''
		list = self.GetChannelList()
		for item in list:
			url = BROAD_URL % (php, type, item['id'])
			tvgid = '%s|%s' % (type, item['id'])
			tvgname = '%s|%s' % (type, item['title'])
			if item['isTv'] == 'Y':
				str += M3U_FORMAT % (tvgid, tvgname, item['img'], type, item['title'], url)				
			else:
				str += M3U_RADIO_FORMAT % (tvgid, tvgname, item['img'], '%s RADIO' % type, item['title'], url+'A')
		return str

	# EPG
	def MakeEPG(self, prefix, channel_list=None):
		import datetime
		startDate = datetime.datetime.now()
		startParam = startDate.strftime('%Y%m%d')
		endDate = startDate + datetime.timedelta(days=1)
		endParam = endDate.strftime('%Y%m%d')

		str = ''
		#url = 'http://www.oksusu.com/api/live/channel?startTime=%s00&endTime=%s24' % (startParam, endParam)
		#url = 'http://www.oksusu.com/api/live/channel?startTime=%s00&endTime=%s06' % (startParam, startParam)
		#request = urllib2.Request(url)
		#response = urllib2.urlopen(request)
		#data = json.load(response, encoding='utf8')

		list = self.GetChannelList()
		#list = list[2:4]
		count = 500
		type_count = 0
		for channel in list:
			count += 1
			channel_number = count
			channel_name = channel['title']
			if channel_list is not None:
				if len(channel_list['OLLEH']) == type_count: break
				if channel['id'] in channel_list['OLLEH']:
					type_count += 1
					channel_number = channel_list['OLLEH'][channel['id']]['num']
					if len(channel_list['OLLEH'][channel['id']]['name']) is not 0: channel_name = channel_list['OLLEH'][channel['id']]['name']
				else:
					continue

			print('OLLEH %s / %s make EPG' % (count, len(list)))
			str += '\t<channel id="OLLEH|%s" video-src="%slc&type=OLLEH&id=%s" video-type="HLS2">\n' % (channel['id'], prefix, channel['id'])
			str += '\t\t<display-name>%s</display-name>\n' % channel_name
			str += '\t\t<display-name>%s</display-name>\n' % channel_number
			str += '\t\t<display-number>%s</display-number>\n' % channel_number
			str += '\t\t<icon src="%s" />\n' % channel['img']
			str += '\t</channel>\n'

			url = 'http://menu.megatvdnp.co.kr:38080/app5/0/api/epg_proglist?istest=&ch_no=%s' % channel['id']
			request = urllib2.Request(url, headers = {'User-Agent' : self.USER_AGENT})
			response = urllib2.urlopen(request)
			data = json.load(response, encoding="utf-8")
	
			

			#continue


			for epg in data['data']['list']:
				startDate = datetime.datetime.strptime(epg['start_ymd'],"%Y%m%d")
				startTime = '%s%s00' % (epg['start_ymd'],epg['start_time'].replace(':', ''))
				if int(epg['start_time'].replace(':', '')) > int(epg['end_time'].replace(':', '')):
					startDate = startDate + datetime.timedelta(days=1)
				endTime = '%s%s00' % (startDate.strftime('%Y%m%d'), epg['end_time'].replace(':', ''))
				if long(startTime) >= long(endTime): continue
				str += '\t<programme start="%s +0900" stop="%s +0900" channel="OLLEH|%s">\n' %  (startTime, endTime, channel['id'])
				str += '\t\t<title lang="kr">%s</title>\n' % urllib.unquote(epg['program_name'].encode('utf8')).replace('<',' ').replace('>',' ').replace('+', ' ')
				# 에피소드 이미지 없음
				#str += '\t\t<icon src="%s" />\n' % epg['ch_image_detail']
				
				age_str = '%s세 이상 관람가' % epg['rating'] if epg['rating'] != '0' else '전체 관람가'
				str += '\t\t<rating system="KMRB"><value>%s</value></rating>\n' % age_str
				desc = '등급 : %s\n' % age_str

				actorName = epg['cast'].strip() if 'cast' in epg and epg['cast'] is not None else None
				actorName = actorName if actorName.strip() != '' else None
				directorName  = epg['director'].strip() if 'director' in epg and epg['director'] is not None else None
				directorName = directorName if directorName.strip() != '' else None
				if actorName is not None or directorName is not None: str += '\t\t<credits>\n'
			
				if actorName is not None:
					temp = actorName.split(',')
					for actor in temp: 
						if actor.strip() != '': str += '\t\t\t<actor>%s</actor>\n' % actor.strip().replace('<',' ').replace('>',' ')
					desc += '출연 : %s\n' % actorName
				if directorName is not None:
					temp = directorName.split(',')
					for actor in temp: 
						if actor.strip() != '': str += '\t\t\t<producer>%s</producer>\n' % actor.strip().replace('<',' ').replace('>',' ')
					desc += '연출 : %s\n' % directorName
				if actorName is not None or directorName is not None: str += '\t\t</credits>\n'
				# summary  없음
				desc += urllib.unquote(epg['program_subname'].encode('utf8')).replace('+', ' ')

				str += '\t\t<desc lang="kr">%s</desc>\n' % desc.strip().replace('<',' ').replace('>',' ')
				str += '\t</programme>\n'
			time.sleep(SLEEP_TIME)
		return str


	def GetLiveCategory(self):
		result = []
		url = 'http://menu.megatvdnp.co.kr:38080/app5/0/api/epg_chCategory?istest=0'
		request = urllib2.Request(url, headers = {'User-Agent' : self.USER_AGENT})
		response = urllib2.urlopen(request)
		data = json.load(response, encoding="utf-8")
		for item in data['data']['list']:
			info = {}
			info['id'] = item['category_id']
			info['title'] = item['category_name']
			result.append(info)
		return result
	
	def GetVodList(self, menu_id, page):
		result = []
		url = 'http://menu.megatvdnp.co.kr:38080/app5/0/api/vod_list?istest=0&menu_id=%s&orderby=regdate&page=%s&count=30&adult_yn=Y' % (menu_id, page)
		request = urllib2.Request(url, headers = {'User-Agent' : self.USER_AGENT})
		response = urllib2.urlopen(request)
		data = response.read()
		#print(url)
		#data = json.load(response, encoding="utf-8")
		#print(data)
		#print(data)
		"""
		for item in data['data']['list']:
			info = {}
			info['id'] = item['category_id']
			info['title'] = item['category_name']
			result.append(info)
		return result
		"""


if __name__ == '__main__':
	olleh = OLLEH()
	olleh.GetChannelList()
	print olleh.GetURL('280', '4000')
