**官方文档**　
> http://zookeeper.apache.org/doc/r3.5.5/

**单机部署zookeeper集群实例**
##### 1、环境
系统：Fedora release 30 (Thirty)
应用版本：
- openjdk-1.8.0_212
- zookeeper-3.5.5

##### 2、安装
```shell
# 确定已经安装java环境
[root@anatronics ~]# java -version
openjdk version "1.8.0_212"
OpenJDK Runtime Environment (build 1.8.0_212-b04)
OpenJDK 64-Bit Server VM (build 25.212-b04, mixed mode)

# 获取二进制包
[root@anatronics ~]# wget https://mirrors.tuna.tsinghua.edu.cn/apache/zookeeper/zookeeper-3.5.5/apache-zookeeper-3.5.5-bin.tar.gz

# 解压并创建软链接
[root@anatronics ~]# tar xf apache-zookeeper-3.5.5-bin.tar.gz -C /apps/
[root@anatronics apps]# ln -sv apache-zookeeper-3.5.5-bin/ zookeeper/

# 设置环境
[root@anatronics apps]# cat /etc/profile.d/zookeeper.sh 
export PATH="$PATH:/apps/zookeeper/bin"
```
##### 3、配置相关文件
**创建相关目录**
```shell
[root@anatronics ~]# mkdir /data/zookeeper/zoo{1..3}
```
**配置文件**
```shell
[root@anatronics conf]# pwd
/apps/zookeeper/conf

[root@anatronics conf]# cp zoo_sample.cfg zoo1.cfg
[root@anatronics conf]# cp zoo_sample.cfg zoo2.cfg
[root@anatronics conf]# cp zoo_sample.cfg zoo3.cfg

# 节点1配置文件信息
[root@anatronics conf]# grep -v "^#" zoo1.cfg 
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/data/zookeeper/zoo1
dataLogDir=/data/zookeeper/log/zoo1
clientPort=2181
server.1=127.0.0.1:2888:3888
server.2=127.0.0.1:2889:3889
server.3=127.0.0.1:2890:3890

# 节点2配置文件信息
[root@anatronics conf]# grep -v "^#" zoo2.cfg 
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/data/zookeeper/zoo2
dataLogDir=/data/zookeeper/log/zoo2
clientPort=2181
server.1=127.0.0.1:2888:3888
server.2=127.0.0.1:2889:3889
server.3=127.0.0.1:2890:3890

# 节点3配置文件信息
[root@anatronics conf]# grep -v "^#" zoo3.cfg 
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/data/zookeeper/zoo3
dataLogDir=/data/zookeeper/log/zoo3
clientPort=2181
server.1=127.0.0.1:2888:3888
server.2=127.0.0.1:2889:3889
server.3=127.0.0.1:2890:3890
```
**在各节点对应dataDir中创建myid文件，并输入服务标识号**
```shell
[root@anatronics ~]# echo 1 > /data/zookeeper/zoo1/myid 
[root@anatronics ~]# echo 2 > /data/zookeeper/zoo2/myid 
[root@anatronics ~]# echo 3 > /data/zookeeper/zoo3/myid 
```
##### 4、启动服务
**启动**
```shell
# 切换到配置文件目录下
[root@anatronics conf]# pwd
/apps/zookeeper/conf

[root@anatronics conf]# zkServer.sh start zoo1.cfg
[root@anatronics conf]# zkServer.sh start zoo2.cfg
[root@anatronics conf]# zkServer.sh start zoo3.cfg
```
**查看状态**
```shell
[root@anatronics conf]# zkServer.sh status zoo1.cfg
/usr/bin/java
ZooKeeper JMX enabled by default
Using config: /apps/zookeeper/bin/../conf/zoo1.cfg
Client port found: 2181. Client address: localhost.
Mode: follower
[root@anatronics conf]# zkServer.sh status zoo2.cfg
/usr/bin/java
ZooKeeper JMX enabled by default
Using config: /apps/zookeeper/bin/../conf/zoo2.cfg
Client port found: 2182. Client address: localhost.
Mode: follower
[root@anatronics conf]# zkServer.sh status zoo3.cfg
/usr/bin/java
ZooKeeper JMX enabled by default
Using config: /apps/zookeeper/bin/../conf/zoo3.cfg
Client port found: 2183. Client address: localhost.
Mode: leader
```
**note**

```
#服务启动占用8080端口
#解决：
#修改启动脚本zkServer.sh添加
"-Dzookeeper.admin.enableServer=false"
```

##### 5、简单操作

**进入命令行管理操作**
```shell
[root@anatronics conf]# zkCli.sh 
/usr/bin/java
Connecting to localhost:2181
...
[zk: localhost:2181(CONNECTED) 0] 
ZooKeeper -server host:port cmd args
	addauth scheme auth
	close 
	config [-c] [-w] [-s]
	connect host:port
	create [-s] [-e] [-c] [-t ttl] path [data] [acl]
	delete [-v version] path
	deleteall path
	delquota [-n|-b] path
	get [-s] [-w] path
	getAcl [-s] path
	history 
	listquota path
	ls [-s] [-w] [-R] path
	ls2 path [watch]
	printwatches on|off
	quit 
	reconfig [-s] [-v version] [[-file path] | [-members serverID=host:port1:port2;port3[,...]*]] | [-add serverId=host:port1:port2;port3[,...]]* [-remove serverId[,...]*]
	redo cmdno
	removewatches path [-c|-d|-a] [-l]
	rmr path
	set [-s] [-v version] path data
	setAcl [-s] [-v version] [-R] path acl
	setquota -n|-b val path
	stat [-w] path
	sync path
```

**python连接服务并创建键值**
```python
from kazoo.client import KazooClient
import json
zk = KazooClient(hosts="127.0.0.1:2181, 127.0.0.1:2182, 127.0.0.1:2183")
zk.start()
znode = {
  "hello": "world",
}
znode = json.dumps(znode)
znode = bytes(znode, encoding="utf-8")
zk.set("/test", znode)
```
切换到命令行，查看结果
```shell
[zk: localhost:2181(CONNECTED) 6] get /test
{"hello": "world"}
```