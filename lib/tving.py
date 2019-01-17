# -*- coding: utf-8 -*-
from util import *

class TVING:
    COOKIE_FILENAME = 'tving2.txt'

    DEFAULT_PARAM = '&screenCode=CSSD0100&networkCode=CSND0900&osCode=CSOD0900&teleCode=CSCD0900&apiKey=1e7952d0917d6aab1f0293a063697610'
    QUALITYS = {'FHD':'stream50', 'HD':'stream40', 'SD':'stream30'}
    QUALITYS_STRING = ['FHD', 'HD', 'SD']

    # 로그인
    def DoLogin(self, user_id, user_pw, type ):
        e = 'Log'
        isLogin = False
        try:
            loginData = {}
            url = 'https://user.tving.com/user/doLogin.tving'
            if type == 'CJONE': loginType = '10'
            else: loginType = '20'
            params = { 'userId' : user_id,
                   'password' : user_pw,
                   'loginType' : loginType }
            
            postdata = urllib.urlencode( params )
            request = urllib2.Request(url, postdata)
            response = urllib2.urlopen(request)
            cookie = response.info().getheader('Set-Cookie')
            for c in cookie.split(','):
                c = c.strip()
                if c.startswith('cs'): 
                    loginData['p'] = c.split('=')[1].split(';')[0].replace('%3D', '=').replace('%3B', '&')
                if c.startswith('_tving_token'):
                    loginData['t'] = c.split(';')[0]
            if 't' in loginData:
                file = open(GetFilename(self.COOKIE_FILENAME), 'wb')
                pickle.dump(loginData, file)
                file.close()
            isLogin = True
        except Exception as e:
            #print(e)
            credential = 'none'
        return (isLogin, e)

    def DoLoginFromSC(self, id, pw, type):
        try:
            if not os.path.isfile(GetFilename(self.COOKIE_FILENAME)):
                self.DoLogin(id, pw, type)
            else:
                create_time = os.path.getctime(GetFilename(self.COOKIE_FILENAME))
                diff = time.gmtime(time.time() - create_time)
                if diff.tm_mday > 1:
                    self.DoLogin(id, pw, type)
        except Exception as e:
            #print(e)
            pass
    
    def GetLoginData(self):
        try:
            file = open(GetFilename(self.COOKIE_FILENAME), 'rb')
            login = pickle.load(file)
            file.close()
        except Exception, e:
            #print(e)
            login = []
        return login


    # 채널 목록
    def GetChannelList( self, list_type=0):
        if list_type == 0: params = ['&channelType=CPCS0100']
        elif list_type == 1: params = ['&channelType=CPCS0300']
        else: params = ['&channelType=CPCS0100', '&channelType=CPCS0300']
        ret = []
        for param in params:
            page = 1
            while True:
                hasMore, list = self.GetList('LIVE', param, page)
                for i in list: ret.append(i)
                if hasMore == 'N': break
                page += 1

        return ret


    def GetList( self, type, param, page ):
        has_more = 'N'
        try:
            result = []
            if type == 'LIVE': url = 'http://api.tving.com/v1/media/lives?pageNo=%s&pageSize=20&order=rating&adult=all&free=all&guest=all&scope=all' % page
            else: url = 'http://api.tving.com/v1/media/episodes?pageNo=%s&pageSize=18&adult=all&guest=all&scope=all&personal=N' % page
            if param is not None: url += param
            url += self.DEFAULT_PARAM			

            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            data = json.load(response, encoding="utf-8")
            for item in data["body"]["result"]:
                try:
                    info = {}
                    if type == 'LIVE':
                        info['id'] = item["live_code"]
                        info['title'] = item['schedule']['channel']['name']['ko']
                        info['episode_title'] = ' '
                        info['img'] = 'http://image.tving.com/upload/cms/caic/CAIC1900/%s.png' % item["live_code"]
                        if item['schedule']['episode'] is not None:
                            info['episode_title'] = item['schedule']['episode']['name']['ko']
                            if info['title'].startswith('CH.') and len(item['schedule']['episode']['image']) > 0:
                                info['img'] = 'http://image.tving.com' + item['schedule']['episode']['image'][0]['url']
                        info['free'] = (item['schedule']['broadcast_url'][0]['broad_url1'].find('drm') == -1)
                        info['summary'] = info['episode_title']
                    result.append(info)
                except Exception as e:
                    print(e)
            has_more = data["body"]["has_more"]
        except Exception as e:
            print('<<<Exception>>> GetList: %s' % e)
            result = []
        return has_more, result

    # URL
    PROXY_URL = 'http://soju6jan.synology.me/tving/tving.php?c=%s&q=%s&l=%s'
    def GetURL(self, code, quality ):
        return self.GetBroadURL(code, quality, self.GetLoginData())
        #return self.GetBroadURLDecrypt(code, quality, self.GetLoginData())
    
    def GetBroadURL(self, code, quality, login ):
        try:
            login2 = login['t'].split('=')[1] if login is not None and 't' in login else ''
            url =  self.PROXY_URL % (code, quality, login2)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            return response.read().strip()
        except Exception as e:
            print(e)
            pass
        return

    def ReturnUrl(self, ret):
        try:
            temp = ret.split('playlist.m3u8')
            request = urllib2.Request(ret)
            response = urllib2.urlopen(request)
            data = response.read()
            if data.find('chunklist.m3u8') != -1:
                url = '%schunklist.m3u8%s' % (temp[0], temp[1])
                request = urllib2.Request(url)
                response = urllib2.urlopen(request)
                data = response.read()
                result = re.compile('(.*?)\.ts').findall(data)
                for r in result:
                    data = data.replace(r, '%s%s' % (temp[0], r))
                    data = data.replace('.ts', '.ts%s' % temp[1])
                return data
            return ret
        except Exception as e:
            print(e)
            pass
        return ret

    """
    def GetBroadURLDecrypt(self, code, quality, login):
        ts = '%d' % time.time()
        url = 'http://api.tving.com/v1/media/stream/info?info=y&screenCode=CSSD0100&apiKey=1e7952d0917d6aab1f0293a063697610&networkCode=CSND0900&noCache=%s&teleCode=CSCD0900&mediaCode=%s&osCode=CSOD0900&streamCode=%s' % (ts, code, quality)

        request = urllib2.Request(url)
        if login is not None and 't' in login:
            request.add_header('Cookie', login['t'])

        response = urllib2.urlopen(request)
        data = json.load(response, encoding='utf-8')
        url = data['body']['stream']['broadcast']['broad_url']

        ret = decrypt(code, ts, url)
        
        if ret.find('m3u8') == -1:
            ret = ret.replace('rtmp', 'http')
            ret = ret.replace('?', '/playlist.m3u8?')
        return ret
    """

    # M3U
    def MakeM3U(self, php, list_type=0):
        type = 'TVING'
        str = ''
        list = self.GetChannelList(list_type)
        for item in list:
            if not item['id'] in ['C07381', 'C04601', 'C07382']:
                url = BROAD_URL % (php, type, item['id'])
                tvgid = '%s|%s' % (type, item['id'])
                tvgname = '%s|%s' % (type, item['title'])
                title = '%s(%s)' % (item['title'], item['episode_title'].replace('\n', '')) if item['title'].startswith('CH.') else item['title'] 
                str += M3U_FORMAT % (tvgid, tvgname, item['img'], type, title, url)
        return str
    
    # EPG
    GRADE_STR = {	'CPTG0100' : '전체 관람가',
            'CPTG0200' : '전체 관람가',
            'CPTG0300' : '12세 이상 관람가',
            'CPTG0400' : '15세 이상 관람가',
            'CPTG0500' : '19세 이상 관람가'}
    
    def MakeEPG(self, prefix, list_type=0, channel_list=None):
        list = self.GetChannelList(list_type)
        import datetime
        startDate = datetime.datetime.now()
        startParam = startDate.strftime('%Y%m%d')
        endDate = startDate + datetime.timedelta(days=1)
        endParam = endDate.strftime('%Y%m%d')

        str = ''
        count = 200 if list_type == 0 else 900
        type_count = 0
        for item in list:
            try:
                count += 1
                channel_number = count
                channel_name = item['title']
                if channel_list is not None:
                    if len(channel_list['TVING']) == type_count: break
                    if item['id'] in channel_list['TVING']:
                        type_count += 1
                        channel_number = channel_list['TVING'][item['id']]['num']
                        if len(channel_list['TVING'][item['id']]['name']) is not 0: channel_name = channel_list['TVING'][item['id']]['name']
                    else:
                        continue

                if item['id'] in ['C07381', 'C04601', 'C07382']: continue
                print('TVING %s / %s make EPG' % (count, len(list)))
                str += '\t<channel id="TVING|%s" video-src="%surl&type=TVING&id=%s" video-type="HLS">\n' % (item['id'], prefix, item['id'])
                str += '\t\t<display-name>%s</display-name>\n' % channel_name
                str += '\t\t<display-name>%s</display-name>\n' % channel_number
                str += '\t\t<display-number>%s</display-number>\n' % channel_number
                str += '\t\t<icon src="%s" />\n' % item['img']
                str += '\t</channel>\n'


                #continue
                try:
                    for date_param in [startParam, endParam]:
                    
                        url = 'http://api.tving.com/v1/media/schedules/%s/%s?pageNo=1&pageSize=200&order=&scope=all&adult=&free=&broadcastDate=%s&broadTime=%s000000&channelCode=%s%s' % (item['id'],date_param,date_param,date_param, item['id'], self.DEFAULT_PARAM)
                        #print(url)
                        request = urllib2.Request(url)
                        response = urllib2.urlopen(request)
                        #print response.read().encode('euc-kr')
                        #return
                        data = json.load(response, encoding='utf8')
                        #print(data)
                        #return

                        #currentDate = startDate
                        for epg in data['body']['result']:
                            if long(epg['broadcast_start_time']) >= long(epg['broadcast_end_time']): continue
                            str += '\t<programme start="%s +0900" stop="%s +0900" channel="TVING|%s">\n' %  (epg['broadcast_start_time'], epg['broadcast_end_time'], item['id'])

                            name = epg['program']['name']['ko']
                            if 'episode' in epg and epg['episode'] is not None:
                                if 'frequency' in epg['episode']: 
                                    #str += '\t\t<sub-title lang="kr">%s화</sub-title>\n' % epg['episode']['frequency']
                                    name += ', %s화' % epg['episode']['frequency']

                            str += '\t\t<title lang="kr">%s</title>\n' % name.replace('<',' ').replace('>',' ')
                        
                            if len(epg['program']['image']) > 0:
                                str += '\t\t<icon src="http://image.tving.com%s" />\n' % epg['program']['image'][0]['url']


                            grade = epg['program']['grade_code']
                            age_str = self.GRADE_STR[grade]
                            str += '\t\t<rating system="KMRB"><value>%s</value></rating>\n' % age_str
                            desc = '등급 : %s\n' % age_str

                            str += '\t\t<category lang="kr">%s</category>\n' % epg['program']['category1_name']['ko']
                            desc += '장르 : %s\n' % epg['program']['category1_name']['ko']
                        
                            actor = epg['program']['actor']
                            director = epg['program']['director']

                            if len(actor) != 0 or len(director) != 0: str += '\t\t<credits>\n'
                    
                            if len(actor) != 0:
                                for name in actor: str += '\t\t\t<actor>%s</actor>\n' % name.strip().replace('<',' ').replace('>',' ')
                                desc += '출연 : %s\n' % (','.join(actor))
                            if len(director) != 0:
                                for name in director: str += '\t\t\t<producer>%s</producer>\n' % name.strip().replace('<',' ').replace('>',' ')
                                desc += '연출 : %s\n' % (','.join(director))
                            if len(actor) != 0 or len(director) != 0: str += '\t\t</credits>\n'
                        
                            if 'episode' in epg and epg['episode'] is not None:
                                if epg['episode']['synopsis']['ko'] is not None:
                                    #desc += epg['episode']['synopsis']['ko']
                                    desc = epg['episode']['synopsis']['ko'] + '\n' + desc
                                    desc == desc.strip()
                            else:
                                if epg['program']['synopsis']['ko'] is not None:
                                    #desc += epg['program']['synopsis']['ko']
                                    desc = epg['program']['synopsis']['ko'] + '\n' + desc
                                    desc == desc.strip()
                            

                            str += '\t\t<desc lang="kr">%s</desc>\n' % desc.strip().replace('<',' ').replace('>',' ')
                            str += '\t</programme>\n'
                        time.sleep(SLEEP_TIME)
                except:
                    exc_info = sys.exc_info()
                    traceback.print_exception(*exc_info)
            except:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                #print str
        return str
    
