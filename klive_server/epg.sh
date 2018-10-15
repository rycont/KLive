#!/bin/sh
#list=`find /volume1/web/klive -name klive.xml -mtime 1`
#list=`ls /volume1/web/klive -al --time-style=+%D | grep `date +%D``
date=`date -r /volume1/web/klive/klive.xml "+%Y%m%d"`
today=`date +%Y%m%d`
echo $date
echo $today

if [ "$date" == "$today" ]
then
	echo "PASS"
else
	echo "CREATE"
	cd /volume1/web/klive
	python klive.py epg
	python InsertImageInEPG.py
	#cp /volume1/web/klive/klive.xml /volume1/web/epg
	cp /volume1/web/klive/klive_daum.xml /volume1/web/epg/klive.xml
	#cp /volume1/web/klive/klive.xml /volume1/homes/soju6jan/git/soju6jan.github.io/
	cp /volume1/web/klive/klive_daum.xml /volume1/homes/soju6jan/git/soju6jan.github.io/klive.xml
	/volume1/homes/soju6jan/git/soju6jan.github.io/commit.sh
fi