# -*- coding: utf-8 -*-
import sys, os
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join( os.getcwd(), 'lib' ))

from klive import *
import xml.etree.ElementTree as ET

import re
import pickle
#import JSON	

DAUM_TV_SRCH   = "http://movie.daum.net/data/movie/search/v2/tv.json?size=20&start=1&searchText=%s"



def insert_image():
	history = GetHistory()
	wrong = {}
	filename = 'klive.xml'
	#filename = '/volume1/homes/soju6jan/soju6jan.github.io/klive.xml'
	tree = ET.parse(filename)
	root = tree.getroot()

	list = root.findall('programme')
	total = len(list)
	count = 0
	for item in list:
		count += 1
		print('%s / %s' % (count, total))
		#print item.tag
		title = item.find('title')
		icon = item.find('icon')
		if icon is None:
			print 'ORIGINAL : %s' % title.text
			search_text = title.text
			patten = re.compile(r'\(.*?\)')
			search_text = re.sub(patten, '', search_text).strip()

			patten = re.compile(r'\[.*?\]')
			search_text = re.sub(patten, '', search_text).strip()

			patten = re.compile(u'\s\d+회$')
			search_text = re.sub(patten, '', search_text).strip()

			patten = re.compile(u'\s\d+화$')
			search_text = re.sub(patten, '', search_text).strip()

			patten = re.compile(u'\s\d+부$')
			search_text = re.sub(patten, '', search_text).strip()

			patten = re.compile(u'^재\s')
			search_text = re.sub(patten, '', search_text).strip()

			print 'SEARCH   : %s' % search_text
			try:
				if search_text in history:
					img = history[search_text]
					print('EXIST IN HISTROTY ')
				elif search_text in wrong:
					print('ALREADY FAIL')
					img = None
				else:
					img = get_daum_poster(search_text)
					if img is not None:
						history[search_text] = img
					else:
						wrong[search_text] = None
				if img is not None:
					element = ET.Element('icon')
					element.attrib['src'] = img
					item.append(element)
			except:
				import traceback
				exc_info = sys.exc_info()
				traceback.print_exception(*exc_info)

		else:
			print('ICON EXIST')
			
		print
	SaveHistory(history)
	tree.write('klive_daum.xml', encoding='utf-8', xml_declaration=True)

from bs4 import BeautifulSoup
# soup = BeautifulSoup(html_doc, 'html.parser')

def get_daum_poster(str):
	#str = urllib.urlencode( str )
	url = 'http://movie.daum.net/data/movie/search/v2/tv.json?size=20&start=1&searchText=%s' % (urllib.quote(str.encode('utf8')))
	request = urllib2.Request(url)
	response = urllib2.urlopen(request)
	data = json.load(response, encoding='utf8')

	#print data
	if data['count'] != 0:
		id = data['data'][0]['tvProgramId']
		url = 'http://movie.daum.net/tv/main?tvProgramId=%s' % id
		request = urllib2.Request(url)
		response = urllib2.urlopen(request)
		data = response.read()
		#print data
		soup = BeautifulSoup(data, 'html.parser') 
		poster_url = soup.find('img', {'class' : 'img_summary'})['src']
		print('POSTER URL : %s' % poster_url)
		return poster_url
	else:
		print('SEARCH FAIL!!')
		return None


def GetHistory():
	try:
		HISTORY = os.path.join( os.getcwd(), 'daum_poster_urls.txt')
		file = open(HISTORY, 'rb')
		history = pickle.load(file)
		file.close()
	except Exception, e:
		#LOG('<<<GetHistory>>> GetLoginData: %s' % e)
		history = {}
	return history

def SaveHistory(history):
	HISTORY = os.path.join( os.getcwd(), 'daum_poster_urls.txt')
	file = open(HISTORY, 'wb')
	pickle.dump(history, file)
	file.close()


if __name__ == '__main__':
	insert_image()

