#!/bin/sh

### BEGIN INIT INFO
# Provides: klive
# Required-Start: $network $remote_fs $local_fs
# Required-Stop: $network $remote_fs $local_fs
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: klive
# Description: klive , initscript by djjproject
### END INIT INFO

pid=`ps ax | grep python | grep kliveProxy | awk '{ print $1 }'`

do_start() {
if [ -z "$pid" ]; then
echo "start klive server."
cd /home/klive
su root -c "nohup /usr/bin/python /home/klive/kliveProxy.py &" > /dev/null 2>&1
else
echo "kilve server already running."
fi
}

do_stop() {
if [ -z "$pid" ]; then
echo "klive server not running"
else
echo "klive server stopped"
kill -9 "$pid"
fi
}

case "$1" in
start)
do_start
;;
stop)
do_stop
;;
restart)
$0 stop
$0 start
;;
*)
echo "Usage: "$1" {start|stop|restart}"
exit 1
;;
esac

exit 0
