# -*- coding: utf-8 -*-
from util import *
from datetime import datetime, timedelta

everyon_url_data = None

class EVERYON:
	EVERYON_LIST = ['전체채널|all', '종편/뉴스|20100', '경제/정보/해외|20300', '레저/스포츠/게임|20400', '드라마/보험|20500', '연예/오락|20600', '여성/어린이/교육|20700', '종교/지역/공공|20800','홈쇼핑|20200']

	# List
	def  GetChannelList(self):
		return self.GetChannelListFromCate('all', 'all')



	def GetChannelListFromCate(self, menu_id, sub_id):
		url  = 'http://www.everyon.tv/main/proc/ajax_ch_list.php'
		
		params = { 'chNum' : '', 'cate':'', 'sCate':menu_id, 'mCate': sub_id, 'chNm':'', 'srchTxt':''  }
		postdata = urllib.urlencode( params )
		request = urllib2.Request(url, postdata)
		request.add_header('Cookie', 'etv_api_key=88abc0e1c8e61c8c3109788ec8392c7fd86c16765fc0b80d5f2366c84c894203')
		response = urllib2.urlopen(request)
		data = response.read()
		
		regax = 'thumb\"\stitle\=\"(.*?)\".*\s*.*selCh\(\'(.*?)\'.*\s*<img\ssrc\=\"(.*?)\"'
		regax2 = 'ch_name\"\stitle\=\"(.*?)\"'
		r = re.compile(regax)
		r2 = re.compile(regax2)
		m = r.findall(data)
		m2 = r2.findall(data)
		
		listChannel = []
		#for item in m:
		for i in range(len(m)-1):
			channel = {}
			channel['title'] = m[i][0].replace(',', ' ')
			channel['id'] = m[i][1]
			channel['img'] = m[i][2]
			channel['summary'] = m2[i]
			listChannel.append(channel)
		return listChannel
	
	def MakeTSFile(self, url, awcookie, awcookie2):
		request = urllib2.Request(url)
		request.add_header('Cookie', awcookie)
		response = urllib2.urlopen(request)
		data = response.read()

		url2 = url[:url.rfind('/')]

		lines = data.split('\n')
		data = ''
		bFirst = True
		for line in lines:
			if bFirst : bFirst = False
			else: data += '\n'

			if line.find('.ts') != -1: data += '%s/%s?%s'%(url2,line,awcookie2)
			else: data += line	
			
		return data	
	
	# URL
	def GetURLFromSC(self, id):
		url = ''
		awcookie = ''
		awcookie2 = ''
		global everyon_url_data
		
		if everyon_url_data is not None:
			if id in everyon_url_data.keys(): 
				prev_time = everyon_url_data[id]['time']				
				current_time = datetime.now()
				
				delta_time = current_time - prev_time
				#쿠키값을 4분 55초 단위로 갱신(5분 후에 자동으로 쿠키값이 바뀌고 있음)
				if delta_time.total_seconds() < 295:
					try:
						url = everyon_url_data[id]['url']
						awcookie = everyon_url_data[id]['cookie']
						awcookie2 = everyon_url_data[id]['params']
					
						data = self.MakeTSFile(url, awcookie, awcookie2)
						print('EVERYON (%s) data2 :\n%s' % (id, data))	
						return data
						#return self.MakeTSFile(url, awcookie, awcookie2)
					except:
						url = ''
						awcookie = ''
						awcookie2 = ''
				else:
					print('EVERYON(%s) : 쿠키값 변경' % id)
						
		if url == '':
			try:
				params = { 'chId' : id }
				postdata = urllib.urlencode( params )
				request = urllib2.Request('http://www.everyon.tv/main/proc/get_ch_data.php', postdata)
				request.add_header('Cookie', 'etv_api_key=88abc0e1c8e61c8c3109788ec8392c7fd86c16765fc0b80d5f2366c84c894203')
				response = urllib2.urlopen(request)
				url = response.read()
				
				response.close()
				
				cookie = response.info().getheader('Set-Cookie')
				
				for c in cookie.split(','):
					c = c.strip()
					if c.startswith('CloudFront-Key-Pair-Id'):
						awcookie = c.split(';')[0] + ';'
					if c.startswith('CloudFront-Policy'):
						awcookie += c.split(';')[0] + ';'
					if c.startswith('CloudFront-Signature'):
						awcookie += c.split(';')[0]
					
				awcookie2 = awcookie.replace('CloudFront-', '')
				awcookie2 = awcookie2.replace(';', '&')
				
				if everyon_url_data is None:
					everyon_url_data = {}
				
				if id not in everyon_url_data.keys():
					request = urllib2.Request(url)
					request.add_header('Cookie', awcookie)
					response = urllib2.urlopen(request)
					lines = response.read().split('\n')
				
					response.close()
				
					url2 = url[:url.rfind('/')]
					url = ''
					for line in lines:
						if line.find('m3u8') != -1:
							url = '%s/%s' % (url2, line)
							break

					everyon_url_data[id] = {}
					everyon_url_data[id]['url'] = url
				else:
					url = everyon_url_data[id]['url']

				everyon_url_data[id]['cookie'] = awcookie
				everyon_url_data[id]['params'] = awcookie2
				everyon_url_data[id]['time'] = datetime.now()

				print('EVERYON(%s) url : %s' % (id, url))
			except:
				url = ''
				awcookie = ''
				awcookie2 = ''			

		data = ''
		if url == '':
			print('EVERYON(%s) : 정보가져오는데 실패' % id)
		else:
			try:
				data = self.MakeTSFile(url, awcookie, awcookie2)			
				print('EVERYON(%s) data1 :\n%s' % (id, data))
			except:
				data = ''
				print('EVERYON(%s) : 정보가져오는데 실패' % id)
			
		return data

		#return ret + "|" + tmp

	# M3U	
	def MakeM3U(self, php):
		type = 'EVERYON'
		str = ''
		for item in self. GetChannelList():
			url = BROAD_URL % (php, type, item['id'])
			tvgid = '%s|%s' % (type, item['id'])
			tvgname = '%s|%s' % (type, item['title'])
			str += M3U_FORMAT % (tvgid, tvgname, item['img'], type, item['title'], url)
		return str

	def MakeEPG(self, prefix, channel_list=None):
		list = self. GetChannelList()
		#list = list[2:3]
		import datetime
		startDate = datetime.datetime.now()
		startParam = startDate.strftime('%Y%m%d')
		endDate = startDate + datetime.timedelta(days=1)
		endParam = endDate.strftime('%Y%m%d')

		str = ''
		regax = '\<td\>(.*?)\<'
		p = re.compile(regax)

		count = 700
		type_count = 0
		for item in list:
			count += 1
			channel_number = count
			channel_name = item['title']
			if channel_list is not None:
				if len(channel_list['EVERYON']) == type_count: break
				if item['id'] in channel_list['EVERYON']:
					type_count += 1
					channel_number = channel_list['EVERYON'][item['id']]['num']
					if len(channel_list['EVERYON'][item['id']]['name']) is not 0: channel_name = channel_list['EVERYON'][item['id']]['name']
				else:
					continue

			print('EVERYON %s / %s make EPG' % (count, len(list)))
			str += '\t<channel id="EVERYON|%s" video-src="%slc&type=EVERYON&id=%s" video-type="HLS">\n' % (item['id'], prefix, item['id'])
			str += '\t\t<display-name>%s</display-name>\n' % channel_name
			str += '\t\t<display-name>%s</display-name>\n' % channel_number
			str += '\t\t<display-number>%s</display-number>\n' % channel_number
			str += '\t\t<icon src="%s" />\n' % item['img']
			str += '\t</channel>\n'

			url_today = 'http://www.everyon.tv/main/schedule.etv?chNum=%s' % item['id']
			url_next = 'http://www.everyon.tv/main/schedule.etv?chNum=%s&schDt=%s&schFlag=n' % (item['id'], startParam)





			#continue





			for url in [url_today, url_next]:
				current_date = startDate if url == url_today else endDate

				request = urllib2.Request(url)
				response = urllib2.urlopen(request)
				data = response.read()
				idx1 = data.find('<tbody>')
				idx2 = data.find('</tbody>')
				data = data[idx1+7:idx2]
				
				m = p.findall(data)
				for i in range(len(m)/3):
					time2 = m[i*3].replace(':', '')
					title = m[i*3+1]
					age = m[i*3+2]
					
					if time2 == '': continue

					temp = time2.split('~')
					start_time = temp[0]
					end_time = temp[1]
					start_str = '%s%s' % (current_date.strftime('%Y%m%d'),start_time)
					if int(start_time) > int(end_time): current_date = current_date + datetime.timedelta(days=1)
					end_str = '%s%s' % (current_date.strftime('%Y%m%d'),end_time)
					if long(start_str) >= long(end_str): continue
					str += '\t<programme start="%s00 +0900" stop="%s00 +0900" channel="EVERYON|%s">\n' %  (start_str, end_str, item['id'])
					str += '\t\t<title lang="kr">%s</title>\n' % title.replace('<',' ').replace('>',' ')
					
					age_str = '%s세 이상 관람가' % age if age != 'ALL' else '전체 관람가'
					str += '\t\t<rating system="KMRB"><value>%s</value></rating>\n' % age_str
					desc = '등급 : %s\n' % age_str

					str += '\t\t<desc lang="kr">%s</desc>\n' % desc.strip().replace('<',' ').replace('>',' ')
					str += '\t</programme>\n'
				time.sleep(SLEEP_TIME)
		return str


	def ReturnUrl(self, ret):
		tmps = ret.split('?')
		pre = '/'.join ( tmps[0].split('/')[:-1]) + '/'
		post = tmps[1]

		req = urllib2.Request(ret)
		res = urllib2.urlopen(req)
		data = res.read()
		data = re.sub('live', pre+'live', data)
		data = re.sub('.ts', '.ts?' + post, data)
		data = re.sub('chunklist', pre+'chunklist', data)
		#if mode == 'lc' or mode == 'url':
		if data.find('chunklist') == -1:
			return data
		else:
			match = re.search('http(.*?)$' ,data)
			if match:
				req = urllib2.Request(match.group(0))
				res = urllib2.urlopen(req)
				data = res.read()
				result = re.compile('(.*?)\.ts').findall(data)
				for r in result:
					data = data.replace(r, '%s%s' % (pre, r))
				return data
		#for 팟플레이어
		"""
		global everyon_seq
		global everyon_id
		global everyon_time
		if (datetime.datetime.now() - everyon_time).seconds <= 1:
			print('return data by equal time......')
			return data
		if everyon_id != id:
			everyon_id = id;
			everyon_time = datetime.datetime.now()
			print('return data by diff id......')
			return data

		match = re.search('EXT-X-MEDIA-SEQUENCE:(?P<no>\d*?)\D' ,data)
		if match:
			print('sequence : %s' %  match.group('no'))
			print('sequence : %s' %  everyon_seq)

			if abs(int(match.group('no'))  - int(everyon_seq)) < 3:
				print('return not......')
				return ''
			else:
				everyon_seq = match.group('no')
				#print data
				#everyon_time = datetime.datetime.now()
				return data
		"""
