# IncetOps
基于Inception，一个审计、执行、回滚、统计sql的开源系统

## Environment
> 1. Python Version: 2.7
> 2. 框架: Flask
> 3. 依赖包: requirements.txt
> 4. 依赖服务: MySQL + Redis + Passport(认证)


## Usage
```
1. 安装依赖环境:
    1.0 git clone https://github.com/staugur/IncetOps && cd IncetOps
    1.1 yum install -y gcc gcc-c++ python-devel libffi-devel openssl-devel mysql-devel
    (或者Ubuntu下`apt-get install build-essential libmysqld-dev libssl-dev python-dev libffi-dev`)
    1.2 pip install -r requirements.txt
    1.3 需要安装 mysql && redis, mysql需要导入incetops.sql
    1.4 认证需要安装`https://github.com/staugur/passport`,体验时可以将main.py中g.signin设置为True

2. 修改配置文件:
    可以直接修改配置文件，或者是添加环境变量, 环境变量的key均在config.py中定义, 必须参数主要有:
    > MYSQL段，设置incetops_mysql_url环境变量
    > REDIS段，设置incetops_redis_url环境变量
    > SSO段，设置incetops_sso_app_id、incetops_sso_app_secret、incetops_sso_server等环境变量

3. 启动队列进程:
    sh online_rq.sh start|stop|restart #启动|停止|重启rq、rqscheduler队列服务

4. 启动Web进程:
    3.1 python main.py #开发环境启动
    3.2 sh online_gunicorn.sh start|stop|restart #生产环境后台启动,采用uwsgi,不需要额外安装,推荐使用!
```
