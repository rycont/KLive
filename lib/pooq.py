# -*- coding: utf-8 -*-
from util import *

class POOQ:
	COOKIE_FILENAME = 'pooq2.txt'

	def __init__( self ):
		self.DEVICE_TYPE_ID = 'pc'
		self.MARKET_TYPE_ID = 'generic'
		self.DEVICE_MODEL_ID = 'none'
		self.DRM = 'WC'
		self.COUNTRY = 'KOR'
		self.API_ACCESS_CREDENTIAL = 'EEBE901F80B3A4C4E5322D58110BE95C'
		self.LIMIT = 30

	# 로그인
	def DoLogin( self, user_id, user_pw ):
		credential = ''
		try:
			url = 'https://wapie.pooq.co.kr/v1/login30/'
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'credential' : 'none',
					   'mode' : 'id',
					   'id' : user_id,
					   'password' : user_pw }
			postdata = urllib.urlencode( params )
			request = urllib2.Request('%s?%s' % (url, postdata), '')
			response = urllib2.urlopen(request)
			data = json.load(response, encoding='utf8')
			credential = data['result']['credential']
		except Exception as e:
			#print(e)       
			return None
		return credential

	def DoLoginFromSC(self, id, pw):
		try:
			if not os.path.isfile(GetFilename(self.COOKIE_FILENAME)):
				ret = self.DoLogin(id, pw)
				if ret is not None: WriteFile(GetFilename(self.COOKIE_FILENAME), ret)
			else:	
				create_time = os.path.getctime(GetFilename(self.COOKIE_FILENAME))
				diff = time.gmtime(time.time() - create_time)
				if diff.tm_mday > 1:
					ret = self.DoLogin(id, pw)
					if ret is not None: WriteFile(GetFilename(self.COOKIE_FILENAME), ret)

		except:
			print(e)
			pass

	# 채널 목록
	def GetChannelList( self ):
		try:
			url = 'http://wapie.pooq.co.kr/v1/livesgenresort30/' 
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'authType' : 'cookie',
					   'orderby' : 'g', #'h',
					   'credential' : 'none' }
			postdata = urllib.urlencode( params )
			request = urllib2.Request('%s?%s' % (url, postdata))
			response = urllib2.urlopen(request)
			data = json.load(response, encoding='utf8')
			result = data['result']['list']
			list = []
			for lists in result:
				for item in lists['list']:
					info = {}
					info['title'] = item['channelTitle']
					info['id'] = item['id']
					info['img'] = item['image']
					info['isRadio'] = item['isRadio']
					info['summary'] = item['title']
					list.append(info)
			return list
		except Exception as e:
			print(e)
			result = []
		return result

	# URL
	def GetGUID( self ):
		import hashlib
		m = hashlib.md5()

		def GenerateID( media ):
			from datetime import datetime
			requesttime = datetime.now().strftime('%Y%m%d%H%M%S')
			randomstr = GenerateRandomString(5)
			uuid = randomstr + media + requesttime
			return uuid

		def GenerateRandomString( num ):
			from random import randint
			rstr = ""
			for i in range(0,num):
				s = str(randint(1,5))
				rstr += s
			return rstr

		uuid = GenerateID("POOQ")
		m.update(uuid)

		return str(m.hexdigest())



	
	def GetLiveQualityList( self, channelID ):
		try:
			url = 'http://wapie.pooq.co.kr/v1/lives30/%s' % channelID
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'credential' : 'none' }
			postdata = urllib.urlencode( params )
			request = urllib2.Request('%s?%s' % (url, postdata))
			response = urllib2.urlopen(request)
			data = json.load(response, encoding='utf8')
			result = data['result']['qualityList'][0]['quality']
		except Exception as e:
			print(e)
			result = None
		return result


	def GetURL( self, channelID, quality):
		surl = ''
		result = None
		try:
			credential = ReadFile(GetFilename(self.COOKIE_FILENAME))
			quality_list = self.GetLiveQualityList(channelID)
			if not quality in quality_list: quality = quality_list[0]

			url = 'http://wapie.pooq.co.kr/v1/lives30/%s/url' % channelID
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'deviceModelId' : 'Macintosh',
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'authType' : 'cookie',
					   'guid' : self.GetGUID(),
					   'lastPlayId' : 'none',
					   'credential' : credential,
					   'quality' : quality }
			postdata = urllib.urlencode( params )
			request = urllib2.Request('%s?%s' % (url, postdata))
			response = urllib2.urlopen(request)
			data = json.load(response, encoding='utf8')
			surl = data['result']['signedUrl']
			#print data
			#print surl
			#print credential
			###############
			filename = GetFilename('pooq_url.txt')
			if surl is None:
				if os.path.isfile(filename):
					file = open(filename, 'rb')
					urls = pickle.load(file)
					surl = urls[channelID] if channelID in urls else None
					surl = urls['recent'] if surl is None and 'recent' in urls else surl
					file.close()
			else:
				if os.path.isfile(filename):
					file = open(filename, 'rb')
					urls = pickle.load(file)
					file.close()
				else: urls = {}
				urls[channelID] = surl
				urls['recent'] = surl
				file = open(filename, 'wb')
				pickle.dump(urls, file)
				file.close()
			return surl
			"""
			if surl is not None:
				request = urllib2.Request(surl)
				response = urllib2.urlopen(request)
				data = response.read()
				idx1 = surl.find('radio.m3u8')
				if idx1 != -1:
					data = data.replace('live.m3u8', surl[:idx1] + 'live.m3u8')
				return data
			"""
		except Exception as e:
			pass
		return surl

	# M3U
	def MakeM3U(self, php):
		type = 'POOQ'
		str = ''
		
		list = self.GetChannelList()
		for item in list:
			url = BROAD_URL % (php, type, item['id'])
			tvgid = '%s|%s' % (type, item['id'])
			tvgname = '%s|%s' % (type, item['title'])
			if item['isRadio'] == 'N':
				str += M3U_FORMAT % (tvgid, tvgname, item['img'], type, item['title'], url)
			else:
				str += M3U_RADIO_FORMAT % (tvgid, tvgname, item['img'], '%s RADIO' % type, item['title'], url)
		return str

	# EPG
	def MakeEPG(self, prefix, channel_list=None):
		list = self.GetChannelList()
		import datetime
		startDate = datetime.datetime.now()
		startParam = startDate.strftime('%Y/%m/%d')
		endDate = startDate + datetime.timedelta(days=2)
		endParam = endDate.strftime('%Y/%m/%d')

		str = ''
		count = 100
		type_count = 0
		for item in list:
			count += 1
			channel_number = count
			channel_name = item['title']
			if channel_list is not None:
				if len(channel_list['POOQ']) == type_count: break
				if item['id'] in channel_list['POOQ']:
					type_count += 1
					channel_number = channel_list['POOQ'][item['id']]['num']
					if len(channel_list['POOQ'][item['id']]['name']) is not 0: channel_name = channel_list['POOQ'][item['id']]['name']
				else:
					continue
			print('POOQ %s / %s make EPG ' % (count, len(list)))
			str += '\t<channel id="POOQ|%s" video-src="%slc&type=POOQ&id=%s" video-type="HLS2">\n' % (item['id'], prefix, item['id'])
			str += '\t\t<display-name>%s</display-name>\n' % channel_name
			str += '\t\t<display-name>%s</display-name>\n' % channel_number
			str += '\t\t<display-number>%s</display-number>\n' % channel_number
			str += '\t\t<icon src="%s" />\n' % item['img']
			str += '\t</channel>\n'

			url = 'http://wapie.pooq.co.kr/v1/epgs30/%s/?deviceTypeId=pc&marketTypeId=generic&apiAccessCredential=EEBE901F80B3A4C4E5322D58110BE95C&drm=WC&country=KOR&offset=0&limit=1000&startTime=%s+00:00&pooqzoneType=none&credential=none&endTime=%s+00:00' % (item['id'], startParam, endParam)
			
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			data = json.load(response, encoding='utf8')

			for epg in data['result']['list']:
				ep_startDate = datetime.datetime.strptime(epg['startDate'].replace('-',''), "%Y%m%d").date()
				startTime = '%s%s' % (epg['startDate'].replace('-',''), epg['startTime'].replace(':', ''))
				temp_startTime = int(epg['startTime'].replace(':', ''))
				temp_endTime = int(epg['endTime'].replace(':', ''))
				if temp_startTime > temp_endTime:
					ep_startDate = ep_startDate + datetime.timedelta(days=1)
				endTime = '%s%s' % (ep_startDate.strftime("%Y%m%d"), epg['endTime'].replace(':', ''))
				if long(startTime) >= long(endTime) : continue
				str += '\t<programme start="%s00 +0900" stop="%s00 +0900" channel="POOQ|%s">\n' %  (startTime, endTime, item['id'])
				#str += '\t\t<title lang="kr"><![CDATA[%s]]></title>\n' % epg['programTitle']
				str += '\t\t<title lang="kr">%s</title>\n' % epg['programTitle'].replace('<',' ').replace('>',' ')
				str += '\t\t<icon src="http://img.pooq.co.kr/BMS/program_poster/201802/%s_210.jpg" />\n' % epg['programId']
				
				age_str = '%s세 이상 관람가' % epg['age'] if epg['age'] != '0' else '전체 관람가'
				str += '\t\t<rating system="KMRB"><value>%s</value></rating>\n' % age_str
				desc = '등급 : %s\n' % age_str

				staring = epg['programStaring'].strip() if 'programStaring' in epg and epg['programStaring'] is not None else None
				if staring is not None and staring != '':
					temp = staring.split(',')
					if len(temp) > 0:
						str += '\t\t<credits>\n'
						for actor in temp:
							str += '\t\t\t<actor>%s</actor>\n' % actor.strip().replace('<',' ').replace('>',' ')
						str += '\t\t</credits>\n'
						desc += '출연 : %s\n' % epg['programStaring'] 
				if 'programSummary' in epg and epg['programSummary'] is not None:
					#desc += epg['programSummary'].replace('<','&lt').replace('>','&gt')
					#desc += epg['programSummary']
					desc = epg['programSummary'] + '\n' + desc
					desc == desc.strip()
				str += '\t\t<desc lang="kr">%s</desc>\n' % desc.strip().replace('<',' ').replace('>',' ')
				str += '\t</programme>\n'
			time.sleep(SLEEP_TIME)
		return str

	# 공중파에서 호출하며 하나의 ID에 대한 <programme> 태그만 넘긴다
	def MakeEPG_ID(self, pooq_id, original_type_id):
		import datetime
		startDate = datetime.datetime.now()
		startParam = startDate.strftime('%Y/%m/%d')
		endDate = startDate + datetime.timedelta(days=2)
		endParam = endDate.strftime('%Y/%m/%d')

		str = ''
		url = 'http://wapie.pooq.co.kr/v1/epgs30/%s/?deviceTypeId=pc&marketTypeId=generic&apiAccessCredential=EEBE901F80B3A4C4E5322D58110BE95C&drm=WC&country=KOR&offset=0&limit=1000&startTime=%s+00:00&pooqzoneType=none&credential=none&endTime=%s+00:00' % (pooq_id, startParam, endParam)
			
		request = urllib2.Request(url)
		response = urllib2.urlopen(request)
		data = json.load(response, encoding='utf8')

		for epg in data['result']['list']:
			ep_startDate = datetime.datetime.strptime(epg['startDate'].replace('-',''), "%Y%m%d").date()
			startTime = '%s%s' % (epg['startDate'].replace('-',''), epg['startTime'].replace(':', ''))
			temp_startTime = int(epg['startTime'].replace(':', ''))
			temp_endTime = int(epg['endTime'].replace(':', ''))
			if temp_startTime > temp_endTime:
				ep_startDate = ep_startDate + datetime.timedelta(days=1)
			endTime = '%s%s' % (ep_startDate.strftime("%Y%m%d"), epg['endTime'].replace(':', ''))
			if long(startTime) >= long(endTime) : continue
			str += '\t<programme start="%s00 +0900" stop="%s00 +0900" channel="%s">\n' %  (startTime, endTime, original_type_id)
				#str += '\t\t<title lang="kr"><![CDATA[%s]]></title>\n' % epg['programTitle']
			str += '\t\t<title lang="kr">%s</title>\n' % epg['programTitle'].replace('<',' ').replace('>',' ')
			str += '\t\t<icon src="http://img.pooq.co.kr/BMS/program_poster/201802/%s_210.jpg" />\n' % epg['programId']
				
			age_str = '%s세 이상 관람가' % epg['age'] if epg['age'] != '0' else '전체 관람가'
			str += '\t\t<rating system="KMRB"><value>%s</value></rating>\n' % age_str
			desc = '등급 : %s\n' % age_str

			staring = epg['programStaring'].strip() if 'programStaring' in epg and epg['programStaring'] is not None else None
			if staring is not None and staring != '':
				temp = staring.split(',')
				if len(temp) > 0:
					str += '\t\t<credits>\n'
					for actor in temp:
						str += '\t\t\t<actor>%s</actor>\n' % actor.strip().replace('<',' ').replace('>',' ')
					str += '\t\t</credits>\n'
					desc += '출연 : %s\n' % epg['programStaring'] 
			if 'programSummary' in epg and epg['programSummary'] is not None:
					#desc += epg['programSummary'].replace('<','&lt').replace('>','&gt')
					#desc += epg['programSummary']
				desc = epg['programSummary'] + '\n' + desc
				desc == desc.strip()
			str += '\t\t<desc lang="kr">%s</desc>\n' % desc.strip().replace('<',' ').replace('>',' ')
			str += '\t</programme>\n'
		time.sleep(SLEEP_TIME)
		return str