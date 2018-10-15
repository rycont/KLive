# -*- coding: utf-8 -*-
from util import *

class EVERYON:
	EVERYON_LIST = ['전체채널|all', '종편/뉴스|20100', '경제/정보/해외|20300', '레저/스포츠/게임|20400', '드라마/보험|20500', '연예/오락|20600', '여성/어린이/교육|20700', '종교/지역/공공|20800','홈쇼핑|20200']

	# List
	def  GetChannelList(self):
		ret = []
		for cate in self.EVERYON_LIST:
			temp = cate.split('|')
			if temp[1] != 'all':
				pageNo = 1
				while True:
					hasMore, list = self.GetChannelListFromCate(temp[1], pageNo)
					for item in list:
						ret.append(item)
					if hasMore == 'N': break
					pageNo += 1
		return ret



	def GetChannelListFromCate(self, cate, pageNo='1'):
		url  = 'http://www.everyon.tv/main/proc/ajax_ch_list.php'
		params = { 'chNum' : '', 'cate':'', 'sCate':cate, 'chNum':'', 'chNm':'', 'page':pageNo, 'perPage':'20', 'srchTxt':''  }
		postdata = urllib.urlencode( params )
		request = urllib2.Request(url, postdata)
		request.add_header('Cookie', 'etv_api_key=88abc0e1c8e61c8c3109788ec8392c7fd86c16765fc0b80d5f2366c84c894203')
		response = urllib2.urlopen(request)
		data = response.read()
		#print(data)
		hasMore = 'Y' if int(data.split('|')[1]) > int(pageNo) * 20 else 'N'
		regax = 'thumb\"\stitle\=\"(.*?)\".*\s*.*selCh\(\'(.*?)\'.*\s*<img\ssrc\=\"(.*?)\"'
		regax2 = 'ch_name\"\stitle\=\"(.*?)\"'
		r = re.compile(regax)
		r2 = re.compile(regax2)
		m = r.findall(data)
		m2 = r2.findall(data)
		list = []
		#for item in m:
		for i in range(len(m)-1):
			info = {}
			info['title'] = m[i][0].replace(',', ' ')
			info['id'] = m[i][1]
			info['img'] = m[i][2]
			info['summary'] = m2[i]
			list.append(info)
		return hasMore, list

	
	# URL
	def GetURLFromSC(self, id):
		url  = 'http://www.everyon.tv/main/proc/get_ch_data.php'
		params = { 'chId' : id }
		postdata = urllib.urlencode( params )
		request = urllib2.Request(url, postdata)
		request.add_header('Cookie', 'etv_api_key=88abc0e1c8e61c8c3109788ec8392c7fd86c16765fc0b80d5f2366c84c894203')
		response = urllib2.urlopen(request)
		#data = json.load(response, encoding='utf8')
		#url2 = data['medias'][0]['url'] if len(data['medias']) > 0 else None	
		#return url2
		ret = response.read()
		#print ret
		cookie = response.info().getheader('Set-Cookie')
		
		info = {}
		info['Key-Pair-Id'] = ''
		info['Policy'] = ''
		info['Signature'] = ''

		for c in cookie.split(','):
			c = c.strip()
			if c.startswith('CloudFront-Key-Pair-Id'):
				info['Key-Pair-Id'] = c.split(';')[0].split('=')[1]
			if c.startswith('CloudFront-Policy'):
				info['Policy'] = c.split(';')[0].split('=')[1]
			if c.startswith('CloudFront-Signature'):
				info['Signature'] = c.split(';')[0].split('=')[1]
		ret = ret.replace('live.m3u8', 'live_hd.m3u8')
		tmp = 'Key-Pair-Id=%s;Policy=%s;Signature=%s' % (info['Key-Pair-Id'], info['Policy'], info['Signature'])
		ret = '%s?Key-Pair-Id=%s&Policy=%s&Signature=%s' % (ret, info['Key-Pair-Id'], info['Policy'], info['Signature'])
		return ret

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
