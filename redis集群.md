#### redis集群搭建
##### 环境
- 系统：CentOS7.5
- redis3.2.12
- 节点：
   - node1：192.168.56.3
     - 6380
     - 6381
     - 6382
   - node2：192.168.56.4
     - 6380
     - 6381
     - 6382
##### 安装redis
获取redis源码包,并编译
```
[root@node1 ~]# wget http://download.redis.io/releases/redis-3.2.12.tar.gz
[root@node1 ~]# tar xf redis-3.2.12.tar.gz
[root@node1 ~]# cd redis-3.2.12/
[root@node1 redis-3.2.12]# make
```
查看生成的可执行文件,并将其拷贝到/usr/bin/下
```
[root@node2 redis-3.2.12]# cd src
[root@node2 src]# find ./ -type f -perm +a+x -print
./mkreleasehdr.sh
./redis-trib.rb
./redis-server
./redis-sentinel
./redis-cli
./redis-benchmark
./redis-check-rdb
./redis-check-aof

# 将上面文件拷贝到/usr/bin/下
[root@node2 src]# find ./ -type f -perm +a+x -exec cp {} /usr/bin/ \;
```
##### 集群目录和配置文件
**node1和node2一样操作**
创建目录
```
[root@node2 ~]# mkdir /apps/redis-cluster/ -p
```
拷贝配置文件
```
[root@node1 redis-3.2.12]# pwd
/root/redis-3.2.12
[root@node1 redis-3.2.12]# cp redis.conf /apps/redis-cluster/redis6380.conf
[root@node1 redis-3.2.12]# cp redis.conf /apps/redis-cluster/redis6381.conf
[root@node1 redis-3.2.12]# cp redis.conf /apps/redis-cluster/redis6382.conf
```
修改配置文件,**其它文件，修改相应配置段**
```
[root@node2 redis-cluster]# grep '^[a-Z]' redis6380.conf 
bind 192.168.56.4
protected-mode yes
port 6380
daemonize yes
pidfile "/var/run/redis_6380.pid"
logfile "/var/log/redis/redis6380.log"
dbfilename "dump6380.rdb"
dir "/apps/redis-cluster"
appendonly yes
appendfilename "appendonly6380.aof"
appendfsync everysec
cluster-enabled yes
cluster-node-timeout 8000
cluster-config-file nodes_6380.conf
```
##### 启动redis服务
启动redis
```
# node1
[root@node1 redis-cluster]# redis-server /apps/redis-cluster/redis6380.conf 
[root@node1 redis-cluster]# redis-server /apps/redis-cluster/redis6381.conf 
[root@node1 redis-cluster]# redis-server /apps/redis-cluster/redis6382.conf 
# node2
[root@node2 redis-cluster]# redis-server /apps/redis-cluster/redis6380.conf 
[root@node2 redis-cluster]# redis-server /apps/redis-cluster/redis6381.conf 
[root@node2 redis-cluster]# redis-server /apps/redis-cluster/redis6382.conf 
```
启动后目录结构
```
[root@node2 redis-cluster]# pwd
/apps/redis-cluster
[root@node2 redis-cluster]# tree
.
├── appendonly6380.aof
├── appendonly6381.aof
├── appendonly6382.aof
├── dump6380.rdb
├── dump6381.rdb
├── dump6382.rdb
├── nodes_6380.conf
├── nodes_6381.conf
├── nodes_6382.conf
├── redis6380.conf
├── redis6381.conf
└── redis6382.conf

0 directories, 12 files
```
查看端口情况
```
[root@node2 redis-cluster]# ss -tlnp|grep redis
LISTEN     0      128    192.168.56.4:16380                    *:*                   users:(("redis-server",pid=17677,fd=7))
LISTEN     0      128    192.168.56.4:16381                    *:*                   users:(("redis-server",pid=17681,fd=7))
LISTEN     0      128    192.168.56.4:16382                    *:*                   users:(("redis-server",pid=17685,fd=7))
LISTEN     0      128    192.168.56.4:6380                     *:*                   users:(("redis-server",pid=17677,fd=4))
LISTEN     0      128    192.168.56.4:6381                     *:*                   users:(("redis-server",pid=17681,fd=4))
LISTEN     0      128    192.168.56.4:6382                     *:*                   users:(("redis-server",pid=17685,fd=4))
```
##### 集群创建
使用redis-trib.rb创建

安装相关依赖ruby、rubygems 
```
[root@node2 src]# yum install ruby rubygems -y
```
安装redis-3.2.2.gem
```
[root@node2 src]# gem install redis -v 3.2.2
Fetching: redis-3.2.2.gem (100%)
Successfully installed redis-3.2.2
Parsing documentation for redis-3.2.2
Installing ri documentation for redis-3.2.2
1 gem installed
```
**建立集群**
```
[root@node2 src]# pwd
/root/pkgs/redis-3.2.12/src
[root@node2 src]# ./redis-trib.rb create --replicas 1 192.168.56.3:6380 192.168.56.3:6381 192.168.56.3:6382 192.168.56.4:6380 192.168.56.4:6381 192.168.56.4:6382
>>> Creating cluster
>>> Performing hash slots allocation on 6 nodes...
Using 3 masters:
192.168.56.3:6380
192.168.56.4:6380
192.168.56.3:6381
Adding replica 192.168.56.4:6381 to 192.168.56.3:6380
Adding replica 192.168.56.3:6382 to 192.168.56.4:6380
Adding replica 192.168.56.4:6382 to 192.168.56.3:6381
M: e513a0d904717b87e9b9329ecb48c1b821991ca2 192.168.56.3:6380
   slots:0-5460 (5461 slots) master
M: a0106e454e680fe0addd48d6bfe04de8fab73be0 192.168.56.3:6381
   slots:10923-16383 (5461 slots) master
S: 049971455f15199c92972e9f7c545903d488390e 192.168.56.3:6382
   replicates 20ce6f6eaa252b6420294ca75e9d7073c1989857
M: 20ce6f6eaa252b6420294ca75e9d7073c1989857 192.168.56.4:6380
   slots:5461-10922 (5462 slots) master
S: 3e80bcb136c3410a4533e268553f58db57a3e9b7 192.168.56.4:6381
   replicates e513a0d904717b87e9b9329ecb48c1b821991ca2
S: ffac2a8cd5c0363bc839508dda36d5f9c51b2a86 192.168.56.4:6382
   replicates a0106e454e680fe0addd48d6bfe04de8fab73be0
Can I set the above configuration? (type 'yes' to accept): yes
>>> Nodes configuration updated
>>> Assign a different config epoch to each node
>>> Sending CLUSTER MEET messages to join the cluster
Waiting for the cluster to join....
>>> Performing Cluster Check (using node 192.168.56.3:6380)
M: e513a0d904717b87e9b9329ecb48c1b821991ca2 192.168.56.3:6380
   slots:0-5460 (5461 slots) master
   1 additional replica(s)
M: a0106e454e680fe0addd48d6bfe04de8fab73be0 192.168.56.3:6381
   slots:10923-16383 (5461 slots) master
   1 additional replica(s)
S: ffac2a8cd5c0363bc839508dda36d5f9c51b2a86 192.168.56.4:6382
   slots: (0 slots) slave
   replicates a0106e454e680fe0addd48d6bfe04de8fab73be0
S: 049971455f15199c92972e9f7c545903d488390e 192.168.56.3:6382
   slots: (0 slots) slave
   replicates 20ce6f6eaa252b6420294ca75e9d7073c1989857
M: 20ce6f6eaa252b6420294ca75e9d7073c1989857 192.168.56.4:6380
   slots:5461-10922 (5462 slots) master
   1 additional replica(s)
S: 3e80bcb136c3410a4533e268553f58db57a3e9b7 192.168.56.4:6381
   slots: (0 slots) slave
   replicates e513a0d904717b87e9b9329ecb48c1b821991ca2
[OK] All nodes agree about slots configuration.
>>> Check for open slots...
>>> Check slots coverage...
[OK] All 16384 slots covered.
```
##### 一些命令
```
# 在master节点添加
[root@node2 src]# redis-cli -h 192.168.56.3 -p 6380
192.168.56.3:6380> set hello world
OK

[root@node2 redis-cluster]# redis-cli -h 192.168.56.3 -p 6381
192.168.56.3:6381> get hello
(error) MOVED 866 192.168.56.3:6380
192.168.56.3:6381> exit
[root@node2 redis-cluster]# redis-cli -h 192.168.56.3 -p 6380
192.168.56.3:6380> get hello
"world"

# 在slave节点上添加键值
[root@node2 redis-cluster]# redis-cli -h 192.168.56.3 -p 6382
192.168.56.3:6382> set k1 v1
(error) MOVED 12706 192.168.56.3:6381
192.168.56.3:6382> 
```
查看cluster节点
```
192.168.56.3:6380> CLUSTER NODES
e513a0d904717b87e9b9329ecb48c1b821991ca2 192.168.56.3:6380 myself,master - 0 0 1 connected 0-5460
a0106e454e680fe0addd48d6bfe04de8fab73be0 192.168.56.3:6381 master - 0 1576139309194 2 connected 10923-16383
ffac2a8cd5c0363bc839508dda36d5f9c51b2a86 192.168.56.4:6382 slave a0106e454e680fe0addd48d6bfe04de8fab73be0 0 1576139311228 6 connected
049971455f15199c92972e9f7c545903d488390e 192.168.56.3:6382 slave 20ce6f6eaa252b6420294ca75e9d7073c1989857 0 1576139310201 4 connected
20ce6f6eaa252b6420294ca75e9d7073c1989857 192.168.56.4:6380 master - 0 1576139308191 4 connected 5461-10922
3e80bcb136c3410a4533e268553f58db57a3e9b7 192.168.56.4:6381 slave e513a0d904717b87e9b9329ecb48c1b821991ca2 0 1576139306176 5 connected
```
查看集群信息
```
192.168.56.3:6380> CLUSTER INFO
cluster_state:ok
cluster_slots_assigned:16384
cluster_slots_ok:16384
cluster_slots_pfail:0
cluster_slots_fail:0
cluster_known_nodes:6
cluster_size:3
cluster_current_epoch:6
cluster_my_epoch:1
cluster_stats_messages_sent:3456
cluster_stats_messages_received:3456
```