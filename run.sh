#!/bin/bash

function run_web
{
	python -m run_web  & 
}

function run
{
	#Runs in the background

	# cp web/static/logs/lastVisited.log.bak web/static/logs/lastVisited.log #debug only
	
	#clean prev results
	find web/templates/ -maxdepth 1 -name 'temp*.html' -delete

	redis-server  & 
	celery worker -A web.celery_worker.celery_app --loglevel=info  & 
	run_web
}


function kill_all_celery
{
    echo "Killing all celery processes"
    ps aux | grep celery | xargs -0 -n1 | awk '{print $2}' | xargs kill -9

}

function kill_redis
{
    echo "Killing redis-server"
    redis-cli flushall #clear cache
    redis-cli shutdown
    
    ps aux | grep redis | xargs -0 -n1 | awk '{print $2}' | xargs kill -9 #just in case the previous shutdown failed
    rm dump.rdb

}

function kill_py_script
{
	echo "Killing py script"
    ps aux | grep fashionFeed/run_web.py | xargs -0 -n1 | awk '{print $2}' | xargs kill -9
	
}
if [ -z "$1" ]; then 
	#conditional tests if the program has received an argument
	echo usage: $0 [START, STOP]
	exit
fi

opt=$1

if [ "$opt" = "START" ]; then
	echo "Starting"
	run
	exit

elif [ "$opt" = "WEB_ONLY" ]; then
	# For debugging purposes
	run_web
	exit
	
elif [ "$opt" = "STOP" ]; then
	echo "Stopping"
	kill_all_celery
	kill_py_script
	kill_redis
	exit

else
	echo "Unsupported option. Available ones: [START, STOP, WEB_ONLY]"

fi

