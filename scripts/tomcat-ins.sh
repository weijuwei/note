#!/bin/bash
# tomcat instance status script.
#
# tomcat instance directory is located in the Tomcat directory.

if [ $# -ne 2 ];then
	echo "Error in the number of parameters	";
	echo "Usage: "$0" INSTANCE_NAME start|stop|restart";
	exit 10;
fi

export CATALINA_HOME="/apps/tomcat/"
export CATALINA_BASE="$CATALINA_HOME$1"

if [ ! -e "$CATALINA_BASE" ];then
	echo "Instance $1 not found,please check the instance name";
	exit 1;
fi

TOMCAT_ID=`ps aux |grep "java"|grep "Dcatalina.base=$CATALINA_BASE "|grep -v "grep"|awk '{ print $2}'`
TOMCAT_BASENAME=`basename $CATALINA_BASE`

case $2 in
start)
	if [ -n "$TOMCAT_ID" ];then
		echo "$CATALINA_BASE" is running;
		exit 2;
	fi
	$CATALINA_HOME/bin/startup.sh
	echo "$TOMCAT_BASENAME start success."
	;;
stop)
    if [ -z "$TOMCAT_ID" ];then
        echo "$CATALINA_BASE" is stopping;
        exit 3;
    fi

	$CATALINA_HOME/bin/shutdown.sh
	echo "$TOMCAT_BASENAME shutdown success"
	;;
restart)
	$0 stop
	sleep 5
	$0 start
	;;
*)
	echo "parameter error"
	echo "Usage: "$0" INSTANCE_NAME start|stop/restart"
	exit 12
	;;
esac
