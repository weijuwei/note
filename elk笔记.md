#### 官方指南

> https://www.elastic.co/guide/index.html

#### 准备

系统环境：

- CentOS7.5

  + lab1: 192.168.10.200

  + lab2: 192.168.10.201

关闭防火墙 禁用selinux 

修改/etc/hosts文件

```shell
vim /etc/hosts
192.168.10.201 lab2
192.168.10.200 lab1
```

安装包：

+ jdk:jdk-8u201-linux-x64.rpm 

  > https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html  

+ elasticsearch: 5.6.15 rpm   

  > https://www.elastic.co/downloads/past-releases 

+ logstash:5.6.15 rpm

+ kibana:5.6.15 rpm  

+ filebeat:5.6.15 rpm  

#### 1、安装elasticsearch

yum安装相关包

```shell
yum install jdk-8u201-linux-x64.rpm elasticsearch-5.6.15.rpm -y
```

创建elasticsearch存放数据和日志的目录,修改目录所有者为elasticsearch
```shell
mkdir /elk/{data,logs}
chown elasticsearch.elasticsearch /elk/ -R
```

在lab1上修改/etc/elasticsearch/elasticsearch.yml文件
```shell
grep '^[a-Z]' elasticsearch.yml 
cluster.name: my-application
node.name: node-1
path.data: /elk/data
path.logs: /elk/logs
network.host: 192.168.10.200
http.port: 9200
discovery.zen.ping.unicast.hosts: ["192.168.10.200", "192.168.10.201"]
```


lab2上面配置如下：

```shell
grep '^[a-Z]' elasticsearch.yml 
cluster.name: my-application
node.name: node-2
path.data: /elk/data
path.logs: /elk/logs
network.host: 192.168.10.201
http.port: 9200
discovery.zen.ping.unicast.hosts: ["192.168.10.200", "192.168.10.201"]
```

启动服务

```shell
systemctl start elasticsearch
```

验证elasticsearch：
访问elasticsearch端口：
 	**9200：客户端访问端口**
	 **9300：集群情况下服务器之间的通信端口**
访问客户端端口，正常如下显示：

```shell
curl 192.168.10.200:9200
{
  "name" : "node-1",
  "cluster_name" : "my-application",
  "cluster_uuid" : "u2Woi-9iQJe5fdHYKO0eaw",
  "version" : {
    "number" : "5.6.15",
    "build_hash" : "fe7575a",
    "build_date" : "2019-02-13T16:21:45.880Z",
    "build_snapshot" : false,
    "lucene_version" : "6.6.1"
  },
  "tagline" : "You Know, for Search"
}
```

创建测试索引
```shell
curl -XPUT 192.168.10.200:9200/test_index/books/1 -d '       
{ "name": "elasticsearch"
  "price": "20"
}'
```

查看指定索引
```shell
curl -XGET 192.168.10.200:9200/test_index/books/1?pretty=true
{
  "_index" : "test_index", #索引名称
  "_type" : "books",       #类型
  "_id" : "1",             #id
  "_version" : 1,
  "found" : true,
  "_source" : {
    "name" : "elasticsearch",
    "price" : "20"
  }
}
```

更新索引
```shell
curl -XPOST 192.168.10.200:9200/test_index/books/1/_update -d '
{"doc":{
	"price": 30
	}
}'
```

删除指定的索引文档
```shell
curl -XDELETE 192.168.10.200:9200/test_index/books/1
```

删除指定索引
```shell
curl -XDELETE 192.168.10.200:9200/test_index/
```

**安装head插件**

```shell
yum install npm -y
git clone git://github.com/mobz/elasticsearch-head.git
cd elasticsearch-head
npm install
#后台启动
npm run start & 
```

配置elasticsearch允许远程访问：

```shell
# vim /etc/elasticsearch/elasticsearch.yml
http.cors.enabled: true
http.cors.allow-origin: "*"
```

浏览器访问，验证是否可用
http://192.168.10.201:9100/

#### 2、安装logstash

安装包

```shell
yum install logstash-5.6.15.rpm -y
```

验证：
1、通过命令行验证：

```shell
/usr/share/logstash/bin/logstash -e “input {stdin{}} output{stdout{ codec=>”rubydebug“}}”
```

2、通过指定配置文件验证
在/etc/logstash/conf.d/下新建测试文件以.conf结尾

```shell
[root@lab1 ~]# cat /etc/logstash/conf.d/test.conf 
input {
        stdin {
        }
}
output {
        stdout {
                codec => "rubydebug"
        }
}
```

通过指定文件启动：

```shell
 /usr/share/logstash/bin/logstash -f  /etc/logstash/conf.d/test.conf 
```

通过指定文件启动：
 /usr/share/logstash/bin/logstash -f  /etc/logstash/conf.d/test.conf  

**显示提示信息**

```shell
WARNING: Could not find logstash.yml which is typically located in $LS_HOME/config or /etc/logstash. You can specify the path using --path.settings. Continuing using the defaults

解决：
[root@anatronics logstash]# ln -sv /etc/logstash/ /usr/share/logstash/config
```

3、验证结果显示

```shell
The stdin plugin is now waiting for input:
hello
{
      "@version" => "1",
          "host" => "lab1",
    "@timestamp" => 2019-02-22T12:32:40.088Z,
       "message" => "hello"
}
```

**将标准输入的数据写入到elasticsearch中，并在标准输出中显示**

```shell
# /usr/share/logstash/bin/logstash -e '
input {
 stdin {
 }
}
output {
  elasticsearch {
     hosts => ["192.168.10.200:9200"]
     index => "test_logstash"
  }
  stdout {
   codec => "rubydebug"
 }
}'
显示如下：
The stdin plugin is now waiting for input:
test logstash 2
{
      "@version" => "1",
          "host" => "lab1",
    "@timestamp" => 2019-02-22T12:48:08.309Z,
       "message" => "test logstash 2"

## }
```

**将标准输入 输出到指定文件中**

```shell
# cat stdout.conf 
input {
        stdin {
        }
}
output {
        elasticsearch {
                hosts => ["192.168.10.200:9200"]
                index => "test_logstash"
        }
        file {
                path => "/tmp/logstash-%{+YYYY.MM.dd}.txt"
        }
        stdout {
                codec => "rubydebug"
        }
}
The stdin plugin is now waiting for input:
hellphello world
{
      "@version" => "1",
          "host" => "lab1",
    "@timestamp" => 2019-02-23T10:38:00.688Z,
       "message" => "hellphello world"
}
ni hao shijie
{
      "@version" => "1",
          "host" => "lab1",
    "@timestamp" => 2019-02-23T10:38:22.016Z,
       "message" => "ni hao shijie"
}

查看结果显示
[root@lab1 tmp]# cat logstash-2019.02.23.txt 
{"@version":"1","host":"lab1","@timestamp":"2019-02-23T10:38:00.688Z","message":"hellphello world"}
{"@version":"1","host":"lab1","@timestamp":"2019-02-23T10:38:22.016Z","message":"ni hao shijie"} 
```
**收集系统日志 /var/log/messages 存到elasticsearch中，并在/tmp/下生成文件**
```shell
1、配置
# cat system_log.conf 
input {
        file {
                path => "/var/log/messages"
                type => "system-log"
                start_position => "beginning"
        }
}

output {
        elasticsearch {
                hosts => ["192.168.10.200"]
                index => "system-log-%{+YYYY.MM.dd}"
        }
        file {
                path => "/tmp/system-log-%{+YYYY.MM.dd}"
        }
}
2、需要修改messages文件权限为644:
chmod 644 /var/log/messages

3、执行:
# /usr/share/logstash/bin/logstash -f /etc/logstash/conf.d/system_log.conf

4、查看结果
[root@lab1 tmp]# ls
logstash-2019.02.23.txt  system-log-2019.02.23
[root@lab1 tmp]# tail -n2 system-log-2019.02.23  
{"@version":"1","host":"lab1","path":"/var/log/messages","@timestamp":"2019-02-23T11:38:54.007Z","message":"Feb 23 19:36:56 lab1 logstash: \"type\" => \"system-log\"","type":"system-log"}
{"@version":"1","host":"lab1","path":"/var/log/messages","@timestamp":"2019-02-23T11:38:54.007Z","message":"Feb 23 19:36:56 lab1 logstash: }","type":"system-log"}
[root@lab1 tmp]#
```
**多行处理**
```shell
# 匹配以[开头的，之前的行
[root@anatronics conf.d]# cat multiline.conf 
input {
    file {
        codec => multiline {
            pattern => "^\["
            negate => true
            what => "previous"
        }
    }
}

output {
    stdout {
        codec => "rubydebug"
    }
}
```
**收集syslog**
1、配置syslog日志输出
```shell
# vim /etc/rsyslog.conf 
*.* @@192.168.1.254:514

# systemctl restart rsyslogd
```
2、配置
```shell
# cat syslog.conf 
input {
	syslog {
		type => "system-syslog"
		port => "514"
	}
}

output {
	stdout {
		codec => "rubydebug"
	}

#	redis {
#		host => "192.168.1.201"
#		port => 6379
#		key => "syslog"
#		db => 0
#		data_type => "list"
#	}
	elasticsearch {
		hosts => ["192.168.1.254"]
		index => "syslog"
	}
}`
```
3、启动
```shell
/usr/share/logstash/bin/logstash -f /etc/logstash/conf.d/mutiple_logs.conf
```
在本机可查看514端口被打开

**收集多个日志文件到es**
```shell
1、配置
# cat mutiple_logs.conf 
input {
        file {
                path => "/var/log/messages"
                type => "system-log"
                start_position => "beginning"
        }
        file {
                path => "/var/log/nginx/access.log"
                type => "nginx-log"
                start_position => "beginning"
        }
}
output {
        if [type] == "system-log" {
                elasticsearch {
                        hosts => ["192.168.10.200"]
                        index => "system-log-%{+YYYY.MM.dd}"
                }
        }
        if [type] == "nginx-log" {
                elasticsearch {
                        hosts => ["192.168.10.200"]
                        index => "nginx-log-%{+YYYY.MM.dd}"
                }
        }
}

2、nginx日志格式修改成json格式输出
vim /etc/nginx/nginx.conf
	log_format json1 '{"@timestamp":"$time_iso8601",'
	 '"host":"$server_addr",'
	 '"clientip":"$remote_addr",'
	 '"size":$body_bytes_sent,'
	 '"responsetime":$request_time,'
	 '"upstreamtime":"$upstream_response_time",'
	 '"upstreamhost":"$upstream_addr",'
	 '"http_host":"$host",'
	 '"url":"$uri",'
	 '"domain":"$host",'
	 '"xff":"$http_x_forwarded_for",'
	 '"referer":"$http_referer",'
	 '"status":"$status"}';

3、启动
/usr/share/logstash/bin/logstash -f /etc/logstash/conf.d/mutiple_logs.conf

4、查看结果
生成了nginx-log*索引
# curl -XGET 192.168.10.200:9200/nginx-log*?pretty=true

{
  "nginx-log-2019.02.23" : {
    "aliases" : { },
    "mappings" : {
      "nginx-log" : {
        "properties" : {
          "@timestamp" : {
            "type" : "date"
          }..........
```

**mysql**

mysql数据导入到ES
```
[root@anatronics conf.d]# cat es-mysql.conf 
input {
	jdbc {
		jdbc_driver_library => "/etc/logstash/conf.d/mysql-connector-java-8.0.18.jar"
		jdbc_driver_class => "com.mysql.cj.jdbc.Driver"
		jdbc_connection_string => "jdbc:mysql://192.168.1.201:33060/hellodb"
		jdbc_user => "root"
		jdbc_password => "123456"
		schedule => "* * * * *"
		statement => "SELECT * from teachers"
	}
}

output {
	stdout {
		codec => rubydebug
	}

	elasticsearch {
		hosts => ["192.168.1.254"]
		index => "mysql-hellodb"
	}
}
```
ES数据到mysql
```
[root@anatronics conf.d]# logstash-plugin install logstash-output-jdbc
Validating logstash-output-jdbc
Installing logstash-output-jdbc
Installation successful

#创建测试表
MariaDB [hellodb]> create table test (id int,name varchar(15) not null,age int);

[root@anatronics conf.d]# cat es-mysql1.conf 
input {
	stdin {}
}

filter {
	json {
		source => "message"
	}
}

output {
	jdbc {
		driver_jar_path => "/etc/logstash/conf.d/mysql-connector-java-8.0.18.jar"
		driver_class => "com.mysql.cj.jdbc.Driver"
		connection_string => "jdbc:mysql://192.168.1.201:33060/hellodb?user=root&password=123456"
		statement => ["insert into test values(?,?,?)","id","name","age"] 

	}
	stdout {
		codec => rubydebug
	}
}

#在命令行输入
{"id":"1","name":"tom","age":"18"}

MariaDB [hellodb]> select * from test;
+------+------+------+
| id   | name | age  |
+------+------+------+
|    1 | tom  |   32 |
+------+------+------+
1 row in set (0.00 sec)

```

#### 3、安装kibana

1、安装包

```shell
yum install -y kibana-5.6.15-x86_64.rpm 
```

2、修改配置文件

```shell
# vim /etc/kibana/kibana.yml
# grep '^[a-Z]' /etc/kibana/kibana.yml
server.port: 5601
server.host: "192.168.10.200"
elasticsearch.url: "http://192.168.10.200:9200"
```

3、启动服务

```shell
systemctl start kibana
```

4、浏览器打开http://192.168.10.200:5601验证是否成功

#### 4、安装fliebeat

安装包

```shell
yum install -y filebeat-5.6.15-x86_64.rpm
```

作用：
 在web端时时收集日志并传递给logstash进一步处理

为什么不用logstash在web端收集？
 依赖java环境，一旦java出问题，可能影响到web服务
 系统资源占用率高，且存在bug风险
 配置比较复杂，支持匹配过滤
 Filebeat挺好的，专注日志收集，语法简单，安装快捷，配置方便

配置文件/etc/filebeat/filebeat.yml

**简单应用**
通过filebeat将/var/log/messages收集到/tmp下filebeat_syslog.txt中
配置内容:

```shell
# grep -v '#' filebeat.yml | grep '[a-Z]'
filebeat.prospectors:
- input_type: log
  paths:
	- /var/log/messages
  exclude_lines: ["^DBG"]
  document_type: system-log
output.file:
  path: "/tmp"
  filename: "filebeat_syslog.txt"
```

启动服务

```shell
systemctl start filebeat.service
```

查看目标文件是否成功写入
```shell
# tail /tmp/filebeat_syslog.txt
{"@timestamp":"2019-02-24T08:45:32.341Z","beat":{"hostname":"lab1","name":"lab1","version":"5.6.15"},"input_type":"log","message":"hello world","offset":2849895,"source":"/var/log/messages","type":"system-log"}
{"@timestamp":"2019-02-24T08:45:47.373Z","beat":{"hostname":"lab1","name":"lab1","version":"5.6.15"},"input_type":"log","message":"hello worldecho hello world \u003e\u003e /var/log/messagesecho hello world \u003e\u003e /var/log/messages","offset":2849981,"source":"/var/log/messages","type":"system-log"}
```

#### 5、安装redis

配置reids，不需要数据持久化，将rdb保存方式关闭

```shell
 vim redis.conf
 daemonize yes
 bind 0.0.0.0
 save "“
 requirepass 123456
```

进入redis管理命令行

```shell
redis-cli -h 192.168.10.200 -a 123456 
```

**配置filebeat.yml文件，通过filebeat收集日志，并将收集结果写入redis中**

```shell
output.redis:
  hosts: ["192.168.10.200"]
  password: "123456"
  key: "system-log"
  db: 10
  timeout: 5
```

进入redis查看

```shell
192.168.10.200:6379> SELECT 10
OK
192.168.10.200:6379[10]> KEYS *
1) "system-log"
192.168.10.200:6379[10]> RPOP system-log

## "{\"@timestamp\":\"2019-02-24T09:07:08.153Z\",\"beat\":{\"hostname\":\"lab1\",\"name\":\"lab1\",\"version\":\"5.6.15\"},\"input_type\":\"log\",\"message\":\"Feb 24 17:07:08 lab1 systemd: Starting filebeat...\",\"offset\":659,\"source\":\"/var/log/messages\",\"type\":\"system-log\"}"
```

#### 6、整合使用

filebeat redis logstash elasticsearch
filebeat收集日志 --> 写入redis
filebeat收集日志 --> 写入logstash //filebeat收集多个类型的日志
logstash写入 --> redis  
logstash读取 <-- redis
logstash --> 写入到elasticsearch

**filebeat搜集多个日志，输出到logstash，然后再输出到redis中**

1、filebeat配置文件

```shell
# grep -v "#" filebeat.yml |grep -v '^
filebeat.prospectors:
- input_type: log
  paths:
    - /var/log/messages
  exclude_lines: ["^DBG"]
  document_type: system-log
- input_type: log
  paths:
    - /var/log/nginx/access.log
  document_type: nginx-access-log
output.logstash:
  hosts: ["192.168.10.200:5044"]
  enabled: true
```

2、logstash开启beat读取filebeat输入的数据

```shell
# cat filebeat.conf 
input {
	beats {
		port => 5044
		codec => "json"
	}
}
output {
	stdout {
		codec => "rubydebug"
	}
}
```

启动 查看信息

```
# /usr/share/logstash/bin/logstash -f filebeat.conf 

{
    "@timestamp" => 2019-02-24T10:30:23.223Z,
        "offset" => 1506,
      "@version" => "1",
    "input_type" => "log",
          "beat" => {
            "name" => "lab1",
        "hostname" => "lab1",
         "version" => "5.6.15"
    },
          "host" => "lab1",
        "source" => "/var/log/messages",
       "message" => "Feb 24 18:30:23 lab1 systemd: Started filebeat.",
          "type" => "system-log",
          "tags" => [
        [0] "_jsonparsefailure",
        [1] "beats_input_codec_json_applied"
    ]
}
{
    "@timestamp" => 2019-02-24T10:30:23.223Z,
        "offset" => 1557,
      "@version" => "1",
          "beat" => {
            "name" => "lab1",
        "hostname" => "lab1",
         "version" => "5.6.15"
    },
    "input_type" => "log",
          "host" => "lab1",
        "source" => "/var/log/messages",
       "message" => "Feb 24 18:30:23 lab1 systemd: Starting filebeat...",
          "type" => "system-log",
          "tags" => [
        [0] "_jsonparsefailure",
        [1] "beats_input_codec_json_applied"
    ]
}
```


3、logstash读取的数据根据type输出到redis中不同的key

```shell
# cat /etc/logstash/conf.d/filebeat.conf 

input {
	beats {
		port => 5044
		codec => "json"
	}
}
output {
	if [type] == "system-log" {
		redis {
			host => "192.168.10.200"
			port => 6379
			password => "123456"
			key => "system-log"
			db => 10
			data_type => "list"
		}
	}
	if [type] == "nginx-access-log" {
		redis {
			host => "192.168.10.200"
			port => 6379
			password => "123456"
			key => "nginx-access-log"
			db => 10
			data_type => "list"
			codec => "json"
		}
	}
}
```

redis中验证：

```shell
192.168.10.200:6379[10]> KEYS *
1) "nginx-access-log"
2) "system-log"
192.168.10.200:6379[10]> LPOP nginx-access-log
"{\"referer\":\"-\",\"offset\":524,\"input_type\":\"log\",\"source\":\"/var/log/nginx/access.log\",\"type\":\"nginx-access-log\",\"http_host\":\"192.168.10.200\",\"url\":\"/index.html\",\"tags\":[\"beats_input_codec_json_applied\"],\"upstreamhost\":\"-\",\"@timestamp\":\"2019-02-24T12:06:37.804Z\",\"size\":11,\"clientip\":\"192.168.10.200\",\"domain\":\"192.168.10.200\",\"host\":\"192.168.10.200\",\"@version\":\"1\",\"beat\":{\"name\":\"lab1\",\"hostname\":\"lab1\",\"version\":\"5.6.15\"},\"responsetime\":0.0,\"xff\":\"-\",\"upstreamtime\":\"-\",\"status\":\"200\"}"
192.168.10.200:6379[10]> LPOP system-log
"{\"@timestamp\":\"2019-02-24T11:01:04.826Z\",\"offset\":1619,\"@version\":\"1\",\"input_type\":\"log\",\"beat\":{\"name\":\"lab1\",\"hostname\":\"lab1\",\"version\":\"5.6.15\"},\"host\":\"lab1\",\"source\":\"/var/log/messages\",\"message\":\"Feb 24 19:01:02 lab1 systemd: Started Session 7 of user root.\",\"type\":\"system-log\",\"tags\":[\"_jsonparsefailure\",\"beats_input_codec_json_applied\"]}"
192.168.10.200:6379[10]> 
```

4、logstash从redis中取得的数据，并将数据写入到elasticsearch中
*取得单个key，创建索引*

```shell
# cat system_redis_es.conf 
input {
	redis {
		host => "192.168.10.200"
		port => 6379
		db => 10
		password => "123456"
		key => "system-log"
		data_type => "list"
	}
}
output {
	elasticsearch {
		hosts => ["192.168.10.200:9200"]
		index => "system-log-redis-%{+YYYY.MM.dd}"
	}
}	
```

*取得多个key的数据，分别创建对应elasticsearch索引*

```shell
# cat es_syslog_nginxlog_redis.conf

input {
	redis {
		host => "192.168.10.200"
		db => 10
		port => 6379
		password => "123456"
		key => "system-log"
		data_type => "list"
	}
	redis {
		host => "192.168.10.200"
		db => 10
		port => 6379
		password => "123456"
		key => "nginx-access-log"
		data_type => "list"
	}
}
output {
	if [type] == "system-log" {
		elasticsearch {
			hosts => ["192.168.10.200:9200"]
			index => "system-log-redis-%{+YYYY.MM.dd}"
		}
	}
	if [type] == "nginx-access-log" {
		elasticsearch {
			hosts => ["192.168.10.200:9200"]
			index => "nginx-access-log-redis-%{+YYYY.MM.dd}"
		}
	}
}
```

启动logstash
```shell
/usr/share/logstash/bin/logstash -f es_syslog_nginxlog_redis.conf
```

验证查看










