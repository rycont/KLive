# -*- coding: utf-8 -*-
# 주소 포트
BIND_ADDR = 'soju6jan.iptime.org'
BIND_PORT = 9801

# 푹
POOQ_ID				= 'soju6jan'
POOQ_PW				= 'dlgkdbs02!0'
POOQ_QUALITY		= '5000'		# 5000 2000 1000 500

# 티빙
TVING_ID			= 'soju6jan'
TVING_PW			= 'dlgkdbs02!0'
TVING_QUALITY		= 'stream50'	# stream50 stream40 stream30
TVING_LOGIN_TYPE	= 'CJONE'		# CJONE TVING

# 옥수수
OKSUSU_ID			= 't01020125641'
OKSUSU_PW			= 'dlgkdbs02!0'
OKSUSU_QUALITY		= 'FHD'			# FHD HD SD

# 올레 모바일 TV
OLLEH_ID			= 'deuxist21c'
OLLEH_PW			= 'bob0211!@#'
OLLEH_QUALITY		= '4000'		# 4000 2000 1000

# 커스텀
USE_CUSTOM			= True 
USE_CUSTOM_SOURCE	= 'custom.txt'



## 수정 X #############################################################
USE_CUSTOM_SPLIT_CHAR	= ':'
USE_CUSTOM_REGEX		= '^(?P<channel_id>.*?)%s(?P<channel_number>.*?)%s(?P<channel_name>.*?)$' % (USE_CUSTOM_SPLIT_CHAR, USE_CUSTOM_SPLIT_CHAR)
USE_CUSTOM_M3U			= 'klive_custom.m3u'
USE_CUSTOM_EPG			= 'klive_custom.xml'

CONTENTS_LIST		= 'KBS|MBC|SBS|POOQ|TVING|OKSUSU|OLLEH|VIDEOPORTAL|EVERYON|TVING_VOD|RADIO1'
FILENAME_M3U		= 'klive.m3u'
FILENAME_EPG 		= 'klive.xml'
