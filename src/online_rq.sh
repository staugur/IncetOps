#!/bin/bash
#
#启动rq异步任务队列进程
#启动rqscheduler定时任务调度队列进程
#

dir=$(cd $(dirname $0); pwd)
cd $dir

useRqscheduler=true
pidfile1=${dir}/logs/rq.pid
logfile1=${dir}/logs/rq.log
pidfile2=${dir}/logs/rqscheduler.pid
logfile2=${dir}/logs/rqscheduler.log
[ -d ${dir}/logs ] || mkdir -p ${dir}/logs

case "$1" in
start)
    if [ -f $pidfile1 ]; then
        echo "$pidfile1 exists, process is already running or crashed"
    else
        echo "Starting rq server..."
        python -O rq_worker.py &>> $logfile1 &
        pid=$!
        echo $pid > $pidfile1
    fi
    # rqscheduler
    if [ "$useRqscheduler" = "true" ];then
        if [ -f $pidfile2 ]; then
            echo "$pidfile2 exists, process is already running or crashed"
        else
            echo "Starting rqscheduler server..."
            python -O rqscheduler_worker.py &>> $logfile2 &
            pid=$!
            echo $pid > $pidfile2
        fi
    fi
    ;;

stop)
    if [ ! -f $pidfile1 ]; then
        echo "$pidfile1 does not exist, process is not running"
    else
        echo "Stopping rq server..."
        pid=$(cat $pidfile1)
        kill $pid
        while [ -x /proc/${pid} ]
        do
            echo "Waiting for rq to shutdown ..."
            kill $pid ; sleep 1
        done
        echo "rq stopped"
        rm -f $pidfile1
    fi
    # rqscheduler
    if [ "$useRqscheduler" = "true" ]; then
        if [ ! -f $pidfile2 ]; then
            echo "$pidfile2 does not exist, process is not running"
        else
            echo "Stopping rqscheduler server..."
            pid=$(cat $pidfile2)
            kill $pid
            while [ -x /proc/${pid} ]
            do
                echo "Waiting for rqscheduler to shutdown ..."
                kill $pid ; sleep 1
            done
            echo "rqscheduler stopped"
            rm -f $pidfile2
        fi
    fi
    ;;

status)
    if [ -f $pidfile1 ]; then
        PID1=$(cat $pidfile1)
        if [ ! -x /proc/${PID1} ]
        then
            echo 'rq is not running'
        else
            echo "rq is running ($PID1)"
        fi
    else
        echo "$pidfile1 is not exist"
    fi
    # rqscheduler
    if [ "$useRqscheduler" = "true" ]; then
        if [ -f $pidfile2 ]; then
            PID2=$(cat $pidfile2)
            if [ ! -x /proc/${PID2} ]
            then
                echo 'rqscheduler is not running'
            else
                echo "rqscheduler is running ($PID2)"
            fi
        else
            echo "$pidfile2 is not exist"
        fi
    fi
    ;;

restart)
    bash $0 stop
    bash $0 start
    ;;

*)
    echo "Usage: $0 start|stop|restart|status"
    ;;
esac
