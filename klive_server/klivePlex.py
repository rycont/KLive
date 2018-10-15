
config = {
	'bindAddr':BIND_ADDR,
    'bindPort': BIND_PORT,
    'tvhURL': TVH_URL,
    'tunerCount': 6,
    'tvhWeight': 300,
    'streamProfile': 'pass',
    'ffmpeg' : 'ffmpeg',
}

discoverData= {
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
#################################################
# for PLEX DVR with Tvheadend
#################################################
@app.route('/discover.json')
def discover():
	global discoverData
	return jsonify(discoverData)

@app.route('/lineup_status.json')
def status():
    return jsonify({
        'ScanInProgress': 0,
        'ScanPossible': 1,
        'Source': "Cable",
        'SourceList': ['Cable']
    })

@app.route('/lineup.json')
def lineup():
	# cannot direct plex 
	#if USE_TVH_PROXY == True: return lineup_tvh()
	#else: return lineup_plex()
	return lineup_tvh()

def lineup_plex():
	lineup = []
	count = 0
	prefix_m3u = 'http://%s:%s/url' % (config['bindAddr'], config['bindPort'])
	current_path = os.path.dirname(os.path.abspath(__file__))
	_FILENAME_M3U = os.path.join(current_path, PATH_OUTPUT, FILENAME_M3U)
	_USE_CUSTOM_M3U = os.path.join(current_path, PATH_OUTPUT, USE_CUSTOM_M3U)
	m3u_list = ParsingM3U(_FILENAME_M3U )
	custom = MakeCustom(prefix_m3u, list_return=True)
	for c in custom['all']:
		if c['id_str'] in m3u_list:
			lineup.append({
				'GuideNumber': str(c['num']),
				'GuideName': m3u_list[c['id_str']]['name'],
				'URL': m3u_list[c['id_str']]['url']
			})
	return jsonify(lineup)

def lineup_tvh():
	lineup = []
	count = 0
	url = '%s/api/channel/grid?start=0&limit=999999' % config['tvhURL']
	print url
	try:
		#request = urllib2.Request(url)
		#response = urllib2.urlopen(request)
		#list = json.load(response, encoding="utf-8")
		#list = list['entries']
		r = requests.get(url)
		list = r.json()['entries']
	except:
		exc_info = sys.exc_info()
		traceback.print_exception(*exc_info)
		return
	for c in list:
		if c['enabled']:
			count += 1
			url = '%s/stream/channel/%s?profile=%s&weight=%s' % (config['tvhURL'], c['uuid'], config['streamProfile'],int(config['tvhWeight']))
			name = c['name']
			lineup.append({
				'GuideNumber': str(c['number']), #채널번호를 넣었다면 이 주석을 풀고 아래줄 주석처리
				#'GuideNumber': str(count),
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


@app.route('/epg_plex')
def server_epg_plex():
	ret = server_epg()
	return ret.replace('display-number', 'display-name')


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
			ret += 'pipe://%s -i %s -c copy -f mpegts pipe:1\n' % (config['ffmpeg'], line)
		else:
			ret += line + '\n'
	return ret
