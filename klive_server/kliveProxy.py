# -*- coding: utf-8 -*-
import sys, os
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join( os.getcwd(), 'lib' ))

from klive import *
from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer
from flask import Flask, Response, request, jsonify, abort, render_template, redirect
import time, requests, thread

app = Flask(__name__)
#################################################
@app.route('/')
def root():
	return 'Klive'

@app.route('/m3u')
def m3u():
	current_path = os.path.dirname(os.path.abspath(__file__))
	if USE_CUSTOM: _filepath = os.path.join(current_path, PATH_OUTPUT, USE_CUSTOM_M3U)
	else: _filepath = os.path.join(current_path, PATH_OUTPUT, FILENAME_M3U)
	if os.path.exists(_filepath): return ReadFile(_filepath)

@app.route('/m3uall')
def m3uall():
	current_path = os.path.dirname(os.path.abspath(__file__))
	_filepath = os.path.join(current_path, PATH_OUTPUT, FILENAME_M3U)
	if os.path.exists(_filepath): return ReadFile(_filepath)

@app.route('/epg')
def server_epg():
	current_path = os.path.dirname(os.path.abspath(__file__))
	if USE_CUSTOM: _filepath = os.path.join(current_path, PATH_OUTPUT, USE_CUSTOM_EPG)
	else: _filepath = os.path.join(current_path, PATH_OUTPUT, FILENAME_EPG)
	if os.path.exists( _filepath ): 
		ret = ReadFile( _filepath )
		#Response(ret, mimetype='text/xml')
		return ret

@app.route('/url')
def server_url():
	mode = request.args.get('mode')
	type = request.args.get('type')
	id = request.args.get('id').split('?')[0]
	ret = GetURL(type, id)
	# everyon
	if type == 'EVERYON':
		return EVERYON().ReturnUrl(ret)
	print('TYPE : %s' % type)
	print('ID : %s' % id)
	print('URL : %s' % ret)

	if ret == None: return
	if mode == 'url':
		return redirect(ret, code=302)
	elif mode == 'lc':
		if type == 'OLLEH':
			cj = cookielib.CookieJar()
			opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cj))
			data = {}
			response = opener.open(ret)
			print response.code
			if response.code / 100 == 3:
				redirection_target = response.headers['Location']
				return redirection_target
		return ret
#################################################

def prepare():
	everyon_seq = ''
	current_path = os.path.dirname(os.path.abspath(__file__))
	if not os.path.isdir( os.path.join(current_path, PATH_DATA) ):
		os.mkdir(os.path.join(current_path, PATH_DATA))
	if not os.path.isdir( os.path.join(current_path, PATH_OUTPUT) ):
		os.mkdir(os.path.join(current_path, PATH_OUTPUT))


def thread_main():
	prepare()
	first = True
	hour = -1
	while True:
		try:
			t = time.localtime()
			print('TIME - %s:%s hour:%s' % (t.tm_hour, t.tm_min, hour))
			if t.tm_hour != hour:
				hour = t.tm_hour
				prefix_m3u = 'http://%s:%s/url' % (BIND_ADDR, BIND_PORT)
				prefix_epg = prefix_m3u + '?mode='
				current_path = os.path.dirname(os.path.abspath(__file__))
				if USE_CUSTOM: filepath = os.path.join(current_path, PATH_OUTPUT, USE_CUSTOM_EPG)
				else: filepath = os.path.join(current_path, PATH_OUTPUT, FILENAME_EPG)
				if first or hour < 1 or need_makeepg(filepath):
					print('condition : %s %s' % (first, hour))
					MakeM3U(prefix_m3u)
					if USE_CUSTOM: MakeCustom(prefix_epg)
					else: MakeEPG(prefix_epg)
			first = False
		except:
			exc_info = sys.exc_info()
			traceback.print_exception(*exc_info)
		time.sleep(60)

def need_makeepg(filepath):
	if not os.path.exists( filepath ): return True
	create_time =  os.path.getctime(filepath)
	diff = time.gmtime(time.time() - create_time)
	if diff.tm_hour >= 3:
		return True
	return False

@app.route('/m3upipe')
def server_m3upipe():
	current_path = os.path.dirname(os.path.abspath(__file__))
	if USE_CUSTOM: _filepath = os.path.join(current_path, PATH_OUTPUT, USE_CUSTOM_M3U)
	else: _filepath = os.path.join(current_path, PATH_OUTPUT, FILENAME_M3U)
	if os.path.exists(_filepath): m3u = ReadFile(_filepath)

	lines = m3u.split('\n')
	ret = ''
	for line in lines:
		if line.startswith('http'):
			ret += 'pipe://%s -i %s -c copy -f mpegts pipe:1\n' % ('ffmpeg', line)
		else:
			ret += line + '\n'
	return ret



if __name__ == '__main__':
	t = thread.start_new_thread(thread_main,())
	
	print ('WSGIServer start..')
	http = WSGIServer(('0.0.0.0', BIND_PORT), app.wsgi_app)
	http.serve_forever()

