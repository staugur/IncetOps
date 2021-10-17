FROM python:2.7-slim
ARG PIPMIRROR=https://pypi.org/simple
COPY requirements.txt .
RUN apt update &&\
    apt install -y --no-install-recommends default-libmysqlclient-dev python-dev build-essential &&\
    sed '/st_mysql_options options;/a unsigned int reconnect;' /usr/include/mysql/mysql.h -i.bkp &&\
    pip install --timeout 30 --index $PIPMIRROR --no-cache-dir -r requirements.txt &&\
    rm -rf /var/lib/apt/lists/* requirements.txt
COPY misc/supervisord.conf /etc/
COPY src /IncetOps
WORKDIR /IncetOps
EXPOSE 16000
ENTRYPOINT ["supervisord"]