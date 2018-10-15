# KLive
KLive는 라이브 방송을 제공하는 사이트 및 앱을 크롤링하는 python 코드이다.

- KODI addon
- PLEX plugin
- KLive Server + Android TV App


# 설치
# 소스 다운로드
````
soju6jan@soju6jan-ubuntu:~$ git clone https://github.com/soju6jan/Klive.git
'Klive'에 복제합니다...
remote: Counting objects: 152, done.
remote: Compressing objects: 100% (103/103), done.
remote: Total 152 (delta 68), reused 108 (delta 39), pack-reused 0
오브젝트를 받는 중: 100% (152/152), 146.04 KiB | 111.00 KiB/s, 완료.
델타를 알아내는 중: 100% (68/68), 완료.
연결을 확인하는 중입니다... 완료.
````

- lib 폴더 복사
````
soju6jan@soju6jan-ubuntu:~$ cd Klive/
soju6jan@soju6jan-ubuntu:~/Klive$ mv lib/ klive/
````

- pip 설치
````
soju6jan@soju6jan-ubuntu:~/Klive/klive$ sudo apt install python-pip
[sudo] password for soju6jan:
패키지 목록을 읽는 중입니다... 완료
의존성 트리를 만드는 중입니다
상태 정보를 읽는 중입니다... 완료
다음 패키지가 자동으로 설치되었지만 더 이상 필요하지 않습니다:
  libavdevice-ffmpeg56 libsdl1.2debian linux-headers-4.13.0-36
  linux-headers-4.13.0-36-generic linux-headers-4.13.0-37
````

- 필요 패키지 설치 (virtualenv)
````
soju6jan@soju6jan-ubuntu:~/Klive/klive$ pip install virtualenv
Collecting virtualenv
  Downloading https://files.pythonhosted.org/packages/b6/30/96a02b2287098b23b875bc8c2f58071c35d2efe84f747b64d523721dc2b5/virtualenv-16.0.0-py2.py3-none-any.whl (1.9MB)
    100% |████████████████████████████████| 1.9MB 201kB/s
Installing collected packages: virtualenv
Successfully installed virtualenv
````

- 가상환경 세팅
````
soju6jan@soju6jan-ubuntu:~/Klive/klive$ virtualenv venv
New python executable in /home/soju6jan/Klive/klive/venv/bin/python
Installing setuptools, pip, wheel...done.
soju6jan@soju6jan-ubuntu:~/Klive/klive$ . venv/bin/activate
````

- 필요 모듈 설치
````
(venv) soju6jan@soju6jan-ubuntu:~/Klive/klive$ pip install -r requirements.txt
Collecting flask (from -r requirements.txt (line 1))
  Downloading https://files.pythonhosted.org/packages/7f/e7/08578774ed4536d3242b14dacb4696386634607af824ea997202cd0edb4b/Flask-1.0.2-py2.py3-none-any.whl (91kB)
    100% |████████████████████████████████| 92kB 391kB/s
````

- 세팅 수정
nano, vi 등 문서편집기를 사용하여 settings.py 수정
````
config = { 'bindAddr': 'http://192.168.0.41', 'bindPort': 5003, 'tvhURL': os.environ.get('TVH_URL') or 'http://soju6jan:PW@192.168.0.15:9981', 'tunerCount': os.environ.get('TVH_TUNER_COUNT') or 6, # number of tuners in t$ 'tvhWeight': os.environ.get('TVH_WEIGHT') or 300, # subscription priority 'streamProfile': os.environ.get('TVH_PROFILE') or 'pass', # specifiy a stream$ 'ffmpeg' : 'ffmpeg' }
````

- 실행
````
(venv) soju6jan@soju6jan-ubuntu:~/Klive/klive$ python kliveProxy.py
````

- 서비스 등록
kliveProxy.service 수정

````
[Unit]
Description=KLive Server

[Service]
Environment=
WorkingDirectory=/home/soju6jan/Klive/klive/
ExecStart=/home/soju6jan/Klive/klive/venv/bin/python /home/soju6jan/Klive/klive/kliveProxy.py
Restart=always

[Install]
WantedBy=multi-user.target
````

````
sudo cp kliveProxy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kliveProxy.service
sudo systemctl start kliveProxy.service
````

- 서비스 관련 명령
````
sudo service kliveProxy stop
sudo service kliveProxy start
sudo service kliveProxy restart
````

---
## 지원목록
https://github.com/soju6jan/KLive/wiki/지원-사이트&앱-목록


---
## WIKI
https://github.com/soju6jan/KLive/wiki

---
## 폴더구조
####  lib 폴더 내 파일은 공용파일이다. 직접 파일을 복사한 후 설치 해야한다.
  - KODI
  ```
    - plugin.video.KLive
        resoureces
          language
            Korean
            English
          lib  (lib 폴더 복사)
  ```

  - PLEX
  ```
    - KLive.bundle
        Contents
          Code (lib 폴더 내 파일 복사)
          esources
            English
  ```
  - Server
  ```
    - KLive
        data
        lib  (lib 폴더 복사)
  ```


---
## 변경사항
#### 0.2.2 (2018-08-28)
  - 일부 OS에서 옥수수 안되는 문제 수정

#### 0.2.1 (2018-08-28)
  - KBS 수정

#### 0.1.4 (2018-04-01)
  - KODI / PLEX RADIO2 버그 수정

#### 0.1.3 (2018-03-28)
  - 일부 OS에서 m3u, xml 파일 쓰기가 안되는 문제 수정

#### 0.1.0 (2018-03-18)
  - First Release
