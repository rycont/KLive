# -*- coding: utf-8 -*-
import sys, os
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join( os.getcwd(), 'lib' ))

from setting import *
from pooq import *
from tving import *
from oksusu import *
from everyon import *
from sbs import *
from kbs import *
from mbc import *
from util import *
from radio import *
from olleh import *
from videoportal import *

import operator
def MakeM3U(url):
	print('START MakeM3U : %s' % url)
	temp = CONTENTS_LIST.split('|')
	str = '#EXTM3U\n'
	for item in temp:
		if item == 'KBS': str += KBS().MakeM3U(url)
		if item == 'MBC': str += MBC().MakeM3U(url)
		if item == 'SBS': str += SBS().MakeM3U(url)
		if item == 'RADIO1': str += RADIO1().MakeM3U(url)
		#if item == 'RADIO2': str += RADIO2(RADIO2_XML).MakeM3U(url)
		if item == 'POOQ': str += POOQ().MakeM3U(url)
		if item == 'TVING': str += TVING().MakeM3U(url)
		if item == 'OKSUSU': str += OKSUSU().MakeM3U(url)
		if item == 'EVERYON': str += EVERYON().MakeM3U(url)
		if item == 'OLLEH': str += OLLEH().MakeM3U(url)
		if item == 'TVING_VOD': str += TVING().MakeM3U(url, list_type=1)
		if item == 'VIDEOPORTAL': str += VIDEOPORTAL().MakeM3U(url)
	#str = ChangeM3UForEPG(str)
	current_path = os.path.dirname(os.path.abspath(__file__))
	WriteFile( os.path.join(current_path, PATH_OUTPUT, FILENAME_M3U) , str)
	print('END MakeM3U : %s' % url)
	return str

def ChangeM3UForEPG(str):
	list = [
		['\"KBS|KBS 1TV\"',		'\"POOQ|KBS 1TV\"'],
		['\"KBS|KBS 2TV\"',		'\"POOQ|KBS 2TV\"'],
		['\"KBS|KBSN Drama\"',		'\"POOQ|KBS DRAMA\"'],
		['\"KBS|KBSN Joy\"',		'\"POOQ|KBS JOY\"'],
		['\"KBS|KBSN W\"',		'\"POOQ|KBS W\"'],
		['\"KBS|KBSN Life\"',		'\"POOQ|KBSN Life\"'],
		['\"KBS|KBS 1Radio\"',		'\"POOQ|KBS1RADIO\"'],
		['\"KBS|KBS 2FM Cool FM\"',	'\"POOQ|KBSCOOLFM\"'],
		['\"KBS|KBS 2FM Cool FM 보라\"',	'\"POOQ|KBSCOOLFM\"'],
		['\"MBC|MBC\"',			'\"POOQ|MBC\"'],
		['\"MBC|MBC 표준FM\"',		'\"POOQ|MBC 표준 FM\"'],
		['\"MBC|MBC FM4U\"',		'\"POOQ|MBC FM4U\"'],
		['\"MBC|MBC 무한도전24\"',	'\"POOQ|MBC 무한도전\"'],
		['\"POOQ|CCTV4\"',		'\"EVERYON|CH.28 CCTV-4\"'],
		['\"POOQ|ANIMAX\"',		'\"OKSUSU|Animax\"'],
		]
	for item in list:
		str = str.replace(item[0], item[1])
	return str


def MakeEPG(prefix, list=None):
	print('START MakeEPG : %s' % prefix)
	current_path = os.path.dirname(os.path.abspath(__file__))
	if list is None:
		_EPG = os.path.join(current_path, PATH_OUTPUT, FILENAME_EPG)
		_EPG_TEMP = os.path.join(current_path, PATH_OUTPUT, FILENAME_EPG+'.tmp')
	else:
		_EPG = os.path.join(current_path, PATH_OUTPUT, USE_CUSTOM_EPG)
		_EPG_TEMP = os.path.join(current_path, PATH_OUTPUT, USE_CUSTOM_EPG+'.tmp')
	
	temp = CONTENTS_LIST.split('|')
	str = ''
	str += '<?xml version="1.0" encoding="UTF-8"?>\n'
	str += '<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'
	str += '<tv generator-info-name="klive">\n'
	WriteFile(_EPG_TEMP, str)
	file = None
	for item in temp:
		str = ''
		try:
			if item == 'KBS': 
				if list is None or (list is not None and 'KBS' in list):
					str = KBS().MakeEPG(prefix, list)
			if item == 'MBC': 
				if list is None or (list is not None and 'MBC' in list):
					str = MBC().MakeEPG(prefix, list)
			if item == 'SBS': 
				if list is None or (list is not None and 'SBS' in list):
					str = SBS().MakeEPG(prefix, list)
			if item == 'POOQ': 
				if list is None or (list is not None and 'POOQ' in list):
					str = POOQ().MakeEPG(prefix, list)
			elif item == 'TVING': 
				if list is None or (list is not None and 'TVING' in list):
					str = TVING().MakeEPG(prefix, list_type=0, channel_list=list)
			elif item == 'OKSUSU': 
				if list is None or (list is not None and 'OKSUSU' in list):
					str = OKSUSU().MakeEPG(prefix, list)
			elif item == 'OLLEH': 
				if list is None or (list is not None and 'OLLEH' in list):
					str = OLLEH().MakeEPG(prefix, list)
			elif item == 'VIDEOPORTAL': 
				if list is None or (list is not None and 'VIDEOPORTAL' in list):
					str = VIDEOPORTAL().MakeEPG(prefix, list)
			elif item == 'EVERYON': 
				if list is None or (list is not None and 'EVERYON' in list):
					str = EVERYON().MakeEPG(prefix, list)
			elif item == 'TVING_VOD': 
				if list is None or (list is not None and 'TVING' in list):
					str = TVING().MakeEPG(prefix, list_type=1, channel_list=list)
			elif item == 'RADIO1': 
				if list is None or (list is not None and 'RADIO1' in list):
					str = RADIO1().MakeEPG(prefix, channel_list=list)
			if str != '': AppendEPG(_EPG_TEMP, str)
		except: 
			exc_info = sys.exc_info()
			traceback.print_exception(*exc_info)
	str = '</tv>\n'
	AppendEPG(_EPG_TEMP, str)
	import shutil
	if os.path.exists( _EPG ):
		os.remove( _EPG )
	shutil.move(_EPG_TEMP, _EPG)
	print('END MakeEPG : %s' % prefix)
	return None





def MakeCustom(prefix, list_return=False):
	current_path = os.path.dirname(os.path.abspath(__file__))
	_CUSTOM_SOURCE = os.path.join(current_path, USE_CUSTOM_SOURCE)
	if not os.path.exists( _CUSTOM_SOURCE ):
		print('no custom..')
		return False

	try:
		with open(_CUSTOM_SOURCE, "r", encoding='utf8') as f:
			data = f.readlines()
		f.close()
	except:
		exc_info = sys.exc_info()
		traceback.print_exception(*exc_info)
		return False

	list = {}
	list['all'] = []
	channel_number = 1
	for line in data:
		if line.startswith('#'): continue
		elif line.startswith('CHANNEL_NUMBER_START') : channel_number = int(line.split(':')[1])
		match = re.compile(USE_CUSTOM_REGEX).match(line)
		if match:
			entity = {}
			entity['id_str'] = match.group('channel_id')
			entity['type'], entity['id'] = entity['id_str'].split('|')
			if len(match.group('channel_number').strip()) == 0:
				entity['num'] = channel_number
				channel_number += 1
			else:
				try: entity['num'] = int(match.group('channel_number').strip())
				except: entity['num'] = match.group('channel_number').strip()
			entity['name'] = match.group('channel_name').strip()
			if entity['type'] not in list:
				list[entity['type']] = {}
			list[entity['type']][entity['id']] = entity
			list['all'].append(entity)			
	list['all'].sort(key=operator.itemgetter('num'))
	#print list
	if list_return: return list
	MakeCustomM3U(list)
	MakeEPG(prefix, list=list)
	return True

def MakeCustomM3U(list):
	current_path = os.path.dirname(os.path.abspath(__file__))
	_FILENAME_M3U = os.path.join(current_path, PATH_OUTPUT, FILENAME_M3U)
	_USE_CUSTOM_M3U = os.path.join(current_path, PATH_OUTPUT, USE_CUSTOM_M3U)
	m3u_list = ParsingM3U(_FILENAME_M3U )
	str = "#EXTM3U\n"
	for item in list['all']:
		if item['id_str'] in m3u_list:
			str += '%s\n' % m3u_list[item['id_str']]['line']
			str += '%s\n' % m3u_list[item['id_str']]['url']
	WriteFile(_USE_CUSTOM_M3U, str)


def ParsingM3U(file):
	try:
		with open(file, "r", encoding='utf8') as f:
			data = f.readlines()
		f.close()
	except:
		exc_info = sys.exc_info()
		traceback.print_exception(*exc_info)
		return None
	ret = {}
	for line in data:
		try:
			if line.startswith("#EXTINF"):
				entity = {}
				properties = ['tvg-id', 'tvg-name', 'tvg-logo', 'group-title', 'type', 'radio']
				for pro in properties:
					entity[pro] = get_property_by_tag(pro, line)
				regex = '^#EXTINF:(?P<value>\-?\d*?)[\s|\,]'
				entity['during'] = int(get_property(regex, line))
				regex = '^#EXTINF:.*?,(?P<value>.*?)$'
				entity['name'] = get_property(regex, line)
				entity['line'] = line.strip()
			elif line.startswith("#"):
				continue
			elif line.find('://') != -1:
				entity['url'] = line.strip()
				ret[entity['tvg-id']] = entity
		except:
			exc_info = sys.exc_info()
			traceback.print_exception(*exc_info)
	return ret

def get_property_by_tag(property, data):
	regex = '^#EXTINF.*?%s=\"(?P<value>.*?)\".*?' % property
	return get_property(regex, data)

def get_property(regex, data):
	match = re.compile(regex).match(data)
	if match:
		return match.group('value').strip()
	return None





def GetURL(type, id):
	if type == 'SBS': 
		#SBS().DoLoginFromSC(SBS_ID, SBS_PW)
		ret = SBS().GetURL(id)
	elif type == 'EVERYON': 
		ret = EVERYON().GetURLFromSC(id)
	elif type == 'POOQ': 
		POOQ().DoLoginFromSC(POOQ_ID, POOQ_PW)
		ret = POOQ().GetURL(id, POOQ_QUALITY)
	elif type == 'TVING':
		TVING().DoLoginFromSC(TVING_ID, TVING_PW, TVING_LOGIN_TYPE)
		ret = TVING().GetURL(id, TVING_QUALITY)
	elif type == 'OKSUSU':
		OKSUSU().DoLoginFromSC(OKSUSU_ID, OKSUSU_PW)
		ret = OKSUSU().GetURLFromSC(id, OKSUSU_QUALITY)
	elif type == 'OLLEH':
		OLLEH().DoLoginFromSC(OLLEH_ID, OLLEH_PW)
		ret = OLLEH().GetURLFromSC(id, OLLEH_QUALITY)
	elif type == 'KBS':
		ret = KBS().GetURLWithLocalID(id)
	elif type == 'MBC':
		#MBC().DoLoginFromSC(MBC_ID, MBC_PW)
		ret = MBC().GetURLWithLocalID(id)
	elif type == 'VIDEOPORTAL':
		ret = VIDEOPORTAL().GetURL(id)
	elif type == 'RADIO1':
		ret = RADIO1().GetURLFromID(id)
	return ret



class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    https_response = http_response









def main():
	mode = 'm3u'
	argLen = len(sys.argv)
	if len(sys.argv) > 1:
		mode = sys.argv[1]
	if mode == 'm3u':
		php = sys.argv[2] if argLen > 2 else 'http://localhost/klive/klive.php'
		ret = MakeM3U(php)
	elif mode == 'url':
		type = sys.argv[2]
		id = sys.argv[3]
		ret = GetURL(type, id)
	elif mode == 'epg':
		ret = MakeEPG(sys.argv[2])
	if ret is not None:
		print(ret)

if __name__ == '__main__':
	main()