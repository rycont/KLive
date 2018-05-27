# -*- coding: utf-8 -*-
import sys, os
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join( os.getcwd(), 'lib' ))

from klive import *

from gevent import monkey; monkey.patch_all()
import time
import os
import requests
from gevent.pywsgi import WSGIServer
from flask import Flask, Response, request, jsonify, abort, render_template, redirect


app = Flask(__name__)

config = {
    'bindAddr': 'http://localhost',
    'bindPort': 5003,

    'tvhURL': os.environ.get('TVH_URL') or 'http://ID:PW@localhost:9981',
    'tunerCount': os.environ.get('TVH_TUNER_COUNT') or 6,  # number of tuners in tvh
    'tvhWeight': os.environ.get('TVH_WEIGHT') or 300,  # subscription priority
    'streamProfile': os.environ.get('TVH_PROFILE') or 'pass',  # specifiy a stream profile that you want to use for adhoc transcoding in tvh, e.g. mp4

    'ffmpeg' : 'ffmpeg'
}

discoverData = {
    'FriendlyName': 'kliveProxy',
    'Manufacturer' : 'Silicondust2',
    'ModelNumber': 'HDTC-2US',
    'FirmwareName': 'hdhomeruntc_atsc',
    'TunerCount': int(config['tunerCount']),
    'FirmwareVersion': '20150826',
    'DeviceID': '123456789',
    'DeviceAuth': 'test1234',
    'BaseURL': '%s' % config['bindAddr'],
    'LineupURL': '%s/lineup.json' % config['bindAddr']
}

@app.route('/discover.json')
def discover():
    return jsonify(discoverData)


@app.route('/lineup_status.json')
def status():
    return jsonify({
        'ScanInProgress': 0,
        'ScanPossible': 1,
        'Source': "Cable",
        'SourceList': ['Cable']
    })


"""
@app.route('/lineup.json')
def lineup():
	lineup = []
	
	m3u = MakeM3U('%s:%s/url' % (config['bindAddr'], config['bindPort']))
	lines = m3u.split('\n')
	count = 0
	for i in range(0, len(lines)):
		if lines[i].startswith('#EXTINF:'):
			count += 1
			tmp1 = lines[i].find('tvg-name="')
			tmp1 = lines[i].find('"', tmp1)+1
			tmp2 = lines[i].find('"', tmp1)
			name = lines[i][tmp1:tmp2]
			i += 1
			lineup.append({'GuideNumber': str(count),
				'GuideName': name,
				'URL': lines[i]
			})
	return jsonify(lineup)
"""

@app.route('/lineup.json')
def lineup():
    lineup = []
    count = 0
    for c in _get_channels():
        if c['enabled']:
	    count += 1
            url = '%s/stream/channel/%s?profile=%s&weight=%s' % (config['tvhURL'], c['uuid'], config['streamProfile'],int(config['tvhWeight']))
	    name = c['name']
	   
	    if config['icon'].find('pooq') != -1:
		name = 'POOQ|' + name
	    elif config['icon'].find('tving') != -1:
		name = 'TVING|' + name
	    elif config['icon'].find('oksusu') != -1:
		name = 'OKSUSU|' + name
	    elif config['icon'].find('megatvdnp') != -1:
		name = 'OLLEH|' + name
            elif config['icon'].find('210.182.60.11') != -1:
		name = 'VIDEOPORTAL|' + name
		
            lineup.append({
		#'GuideNumber': str(c['number']), #채널번호를 넣었다면 이 주석을 풀고 아래줄 주석처리
		'GuideNumber': str(count),
                'GuideName': name,
                'URL': url
            })

    return jsonify(lineup)



@app.route('/lineup.post', methods=['GET', 'POST'])
def lineup_post():
    return ''

@app.route('/')
@app.route('/device.xml')
def device():
    return render_template('device.xml',data = discoverData),{'Content-Type': 'application/xml'}


def _get_channels():
    url = '%s/api/channel/grid?start=0&limit=999999' % config['tvhURL']

    try:
        r = requests.get(url)
        return r.json()['entries']

    except Exception as e:
	print('An error occured: ' + repr(e))

@app.route('/')
@app.route('/m3u')
def server_m3u():
	return MakeM3U('%s:%s/url' % (config['bindAddr'], config['bindPort']))

@app.route('/m3ufile')
def server_m3ufile():
	if FILENAME_M3U != '':
		return ReadFile(FILENAME_M3U) 

@app.route('/m3upipe')
def server_m3upipe():
	m3u = MakeM3U('%s:%s/url' % (config['bindAddr'], config['bindPort']))
	
	lines = m3u.split('\n')
	ret = ''
	for line in lines:
		if line.startswith('http'):
			ret += 'pipe://%s -i %s -c copy -f mpegts pipe:1\n' % (config['ffmpeg'], line)
		else:
			ret += line + '\n'
	return ret


@app.route('/url')
def server_url():
	type = request.args.get('type')
	id = request.args.get('id').split('?')[0]
	ret = GetURL(type, id)
	#print('URL : %s' % ret)
	return redirect(ret, code=302)


@app.route('/epg')
def server_epg():
	MakeEPG()
	return 'Done'


if __name__ == '__main__':
	http = WSGIServer(('', config['bindPort']), app.wsgi_app)
	http.serve_forever()

