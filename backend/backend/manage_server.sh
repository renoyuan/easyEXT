
notes="
"${server_name}"
启动服务：bash manage_server.sh start
停止服务：bash manage_server.sh stop
重启服务：bash manage_server.sh restart
"

interpreter=/root/anaconda3/envs/idp_backend/bin/python

# 启动服务
nohup uvicorn main:app --host 0.0.0.0 --port 8000  >  app.log 2>&1  &

# 启动celery
${interpreter} -m celery  -A celery_task:app worker --loglevel=INFO -Q queue1 --concurrency=1 -f celery.log &

function stop_server(){
	echo "关闭celery进程" 
	pkill -f 'celery worker'
}

function stop_server(){
	echo "关闭celery进程" 
	pkill -f 'celery worker'
	pkill -f 'uvicorn'
}

function restart_server(){
	stop_server
	sleep 2
	star_server
}

if [ -z "$action" ];
then
    echo "${notes}"
    echo "Error: action param is not null"
    
elif [ $action = "-h"  ] || [ $action = "--help"  ] || [ $action = "h"  ]
then
	echo "${notes}"
	echo "确保启用了conda环境"
elif [ "$action" = "start"  ]
then
	star_server
elif [ "$action" = "stop"  ]
then
	stop_server
elif [ "$action" = "restart"  ]
then
	restart_server

else
     echo "Error: param error"
fi