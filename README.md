# IncetOps
基于Inception，一个审计、执行、回滚、统计sql的开源系统


## Document
[https://www.saintic.com/blog/261.html](https://www.saintic.com/blog/261.html "https://www.saintic.com/blog/261.html")


## Environment
> 1. Python Version: 2.7
> 2. 框架: Flask
> 3. 依赖包: requirements.txt
> 4. 依赖服务: MySQL + Redis + Passport(认证)


## Demo

演示站任务无法执行！ [IncetOps Demo](http://incetops.saintic.com "IncetOps Demo")


## Features

  1. 支持多个Inception服务
  2. 支持多个数据库，数据库可设置推荐的Inception
  3. 任务支持立即和定时执行两种方式，且定时任务可取消，备份可选、警告可选等
  4. 任务支持OSC并且可以查看OSC详细进度，可取消OSC任务
  5. 任务支持查看回滚语句
  6. 统计数据
  7. 帮助


## Usage
```
1. 安装依赖环境:
    1.0 git clone https://github.com/staugur/IncetOps && cd IncetOps
    1.1 yum install -y gcc gcc-c++ python-devel libffi-devel openssl-devel mysql-devel
    (或者Ubuntu下`apt-get install build-essential libmysqld-dev libssl-dev python-dev libffi-dev`)
    1.2 pip install -r requirements.txt
    1.3 需要安装 mysql && redis, mysql需要导入misc/incetops.sql
    1.4 认证需要安装`https://github.com/staugur/passport`,体验时可以将main.py中g.signin设置为True

2. 修改配置文件:
    可以直接修改配置文件，或者是添加环境变量, 环境变量的key均在config.py中定义, 必须参数主要有:
    > MYSQL段，设置incetops_mysql_url环境变量
    > REDIS段，设置incetops_redis_url环境变量
    > SSO段，设置incetops_sso_app_id、incetops_sso_app_secret、incetops_sso_server等环境变量
    > PLUGINS段，设置默认备份库地址incetops_defaultbackupdatabase环境变量，默认值是MYSQL段，即查看回滚语句时所在任务使用的inception服务对应的备份库地址，可能是不同的，此键只是默认，实际查看回滚时可以自定义输入。
    > SYSTEM段中的incetops_hmac_sha256_key、incetops_aes_cbc_key、incetops_jwt_secret_key一定要与passport中一致，否则无法使用passport统一登录。

3. 启动队列进程:
    sh online_rq.sh start|stop|restart #启动|停止|重启rq、rqscheduler队列服务，用以执行任务

4. 启动Web进程:
    4.1 python main.py #开发环境启动
    4.2 sh online_gunicorn.sh start|run|stop|restart #生产环境后台启动,run是前台启动
```


## Nginx
```
server {
    listen       80;
    server_name  YourDomain;
    #不允许搜索引擎抓取信息
    if ($http_user_agent ~* "qihoobot|Baiduspider|Googlebot|Googlebot-Mobile|Googlebot-Image|Mediapartners-Google|Adsbot-Google|Feedfetcher-Google|Yahoo! Slurp|Yahoo! Slurp China|YoudaoBot|Sosospider|Sogou spider|Sogou web spider|Sogou+web+spider|bingbot|MSNBot|ia_archiver|Tomato Bot") {
        return 403;
    }
    #处理静态资源:
    location ~ ^\/static\/.*$ {
        root /xxxxx/IncetOps/src/;
    }
    location / {
       proxy_pass http://127.0.0.1:xxxxx;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 效果图
![数据库][1]
![任务][2]

[1]: ./Snapshot/db.png
[2]: ./Snapshot/task.png