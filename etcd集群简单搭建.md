#### 简介

​	etcd 是 CoreOS 团队发起的一个管理配置信息和服务发现（service discovery）的项目，它的目标是构建一个高可用的分布式键值（key-value）数据库，用于配置共享和服务发现

> **A highly-available key value store for shared configuration and service discovery.**

有以下四个特点：

1. 简单：基于HTTP+JSON的API让你用curl就可以轻松使用。
2. 安全：可选SSL客户认证机制。
3. 快速：每个实例每秒支持一千次写操作。
4. 可信：使用Raft算法充分实现了分布式。

github

> https://github.com/etcd-io/etcd

应用场景剖析参见：

> https://www.infoq.cn/article/etcd-interpretation-application-scenario-implement-principle

​	用户使用 etcd 可以在多个节点上启动多个实例，并添加它们为一个集群。同一个集群中的 etcd 实例将会保持彼此信息的一致性。

#### 环境

- CentOS 7.5
- 192.168.1.201 master
- 192.168.56.3 node1
- 192.168.56.4 node2

#### 安装

##### 1、安装，采用yum安装

```shell
# 配置extras yum源
[extras]
name=aliyun extrax
baseurl=https://mirrors.aliyun.com/centos/7/extras/x86_64/
gpgcheck=0

# 3节点安装
yum install etcd -y

# 版本信息
yum info etcd
Name        : etcd
Arch        : x86_64
Version     : 3.3.11
Release     : 2.el7.centos
Size        : 45 M
Repo        : installed
From repo   : extras
Summary     : A highly-available key value store for shared configuration
URL         : https://github.com/etcd-io/etcd
License     : ASL 2.0
Description : A highly-available key value store for shared configuration.
```

##### 2、配置/etc/etcd/etcd.conf

> https://coreos.com/etcd/docs/3.3.1/op-guide/clustering.html

##### master节点

```shell
[root@lab ~]# cat /etc/etcd/etcd.conf
#[Member]
#ETCD_CORS=""
#数据存储位置
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
#ETCD_WAL_DIR=""
#其它节点监听地址
ETCD_LISTEN_PEER_URLS="http://192.168.1.201:2380"
# 2379 用于客户端通信，2380 用于节点通信
ETCD_LISTEN_CLIENT_URLS="http://192.168.1.201:2379,http://127.0.0.1:2379"
#ETCD_MAX_SNAPSHOTS="5"
#ETCD_MAX_WALS="5"
#本节点名字
ETCD_NAME="master"
#ETCD_SNAPSHOT_COUNT="100000"
#ETCD_HEARTBEAT_INTERVAL="100"
#ETCD_ELECTION_TIMEOUT="1000"
#ETCD_QUOTA_BACKEND_BYTES="0"
#ETCD_MAX_REQUEST_BYTES="1572864"
#ETCD_GRPC_KEEPALIVE_MIN_TIME="5s"
#ETCD_GRPC_KEEPALIVE_INTERVAL="2h0m0s"
#ETCD_GRPC_KEEPALIVE_TIMEOUT="20s"
#
#[Clustering]
#表示节点监听其他节点同步信号的地址
ETCD_INITIAL_ADVERTISE_PEER_URLS="http://192.168.1.201:2380"
ETCD_ADVERTISE_CLIENT_URLS="http://192.168.1.201:2379"
#ETCD_DISCOVERY=""
#ETCD_DISCOVERY_FALLBACK="proxy"
#ETCD_DISCOVERY_PROXY=""
#ETCD_DISCOVERY_SRV=""
#集群成员
ETCD_INITIAL_CLUSTER="master=http://192.168.1.201:2380,node1=http://192.168.56.3:2380,node2=http://192.168.56.4:2380"
#token认证
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
# 初始化集群状态，new 表示新建
ETCD_INITIAL_CLUSTER_STATE="new"
#ETCD_STRICT_RECONFIG_CHECK="true"
#ETCD_ENABLE_V2="true"
```

###### node1

```shell
[root@node1 ~]# cat /etc/etcd/etcd.conf
#[Member]
#ETCD_CORS=""
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
#ETCD_WAL_DIR=""
ETCD_LISTEN_PEER_URLS="http://192.168.56.3:2380"
ETCD_LISTEN_CLIENT_URLS="http://192.168.56.3:2379,http://127.0.0.1:2379"
#ETCD_MAX_SNAPSHOTS="5"
#ETCD_MAX_WALS="5"
ETCD_NAME="node1"
#ETCD_SNAPSHOT_COUNT="100000"
#ETCD_HEARTBEAT_INTERVAL="100"
#ETCD_ELECTION_TIMEOUT="1000"
#ETCD_QUOTA_BACKEND_BYTES="0"
#ETCD_MAX_REQUEST_BYTES="1572864"
#ETCD_GRPC_KEEPALIVE_MIN_TIME="5s"
#ETCD_GRPC_KEEPALIVE_INTERVAL="2h0m0s"
#ETCD_GRPC_KEEPALIVE_TIMEOUT="20s"
#
#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="http://192.168.56.3:2380"
ETCD_ADVERTISE_CLIENT_URLS="http://192.168.56.3:2379"
#ETCD_DISCOVERY=""
#ETCD_DISCOVERY_FALLBACK="proxy"
#ETCD_DISCOVERY_PROXY=""
#ETCD_DISCOVERY_SRV=""
ETCD_INITIAL_CLUSTER="master=http://192.168.1.201:2380,node1=http://192.168.56.3:2380,node2=http://192.168.56.4:2380"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
#ETCD_STRICT_RECONFIG_CHECK="true"
#ETCD_ENABLE_V2="true"
```

###### node2

```shell
[root@node2 etcd]# cat etcd.conf
#[Member]
#ETCD_CORS=""
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
#ETCD_WAL_DIR=""
ETCD_LISTEN_PEER_URLS="http://192.168.56.4:2380"
ETCD_LISTEN_CLIENT_URLS="http://192.168.56.4:2379,http://127.0.0.1:2379"
#ETCD_MAX_SNAPSHOTS="5"
#ETCD_MAX_WALS="5"
ETCD_NAME="node2"
#ETCD_SNAPSHOT_COUNT="100000"
#ETCD_HEARTBEAT_INTERVAL="100"
#ETCD_ELECTION_TIMEOUT="1000"
#ETCD_QUOTA_BACKEND_BYTES="0"
#ETCD_MAX_REQUEST_BYTES="1572864"
#ETCD_GRPC_KEEPALIVE_MIN_TIME="5s"
#ETCD_GRPC_KEEPALIVE_INTERVAL="2h0m0s"
#ETCD_GRPC_KEEPALIVE_TIMEOUT="20s"
#
#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="http://192.168.56.4:2380"
ETCD_ADVERTISE_CLIENT_URLS="http://192.168.56.4:2379"
#ETCD_DISCOVERY=""
#ETCD_DISCOVERY_FALLBACK="proxy"
#ETCD_DISCOVERY_PROXY=""
#ETCD_DISCOVERY_SRV=""
ETCD_INITIAL_CLUSTER="master=http://192.168.1.201:2380,node1=http://192.168.56.3:2380,node2=http://192.168.56.4:2380"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
#ETCD_STRICT_RECONFIG_CHECK="true"
#ETCD_ENABLE_V2="true"
```

##### 3、启动，开启服务

```shell
systemctl start etcd

# 查看成员
[root@lab ~]# etcdctl member list
b4b07e4c725567ef: name=master peerURLs=http://192.168.1.201:2380 clientURLs=http://192.168.1.201:2379 isLeader=true
de5365f8233167d3: name=node2 peerURLs=http://192.168.56.4:2380 clientURLs=http://192.168.56.4:2379 isLeader=false
f6e21250ef798b6d: name=node1 peerURLs=http://192.168.56.3:2380 clientURLs=http://192.168.56.3:2379 isLeader=false
```

##### 4、验证

```SHELL
# 在node2节点创建一对键值
[root@node2 ~]# etcdctl set hello "world"
world

# 其它节点查看
[root@lab ~]# etcdctl get hello
world
[root@node1 ~]# etcdctl get hello
world
```

##### 5、其它一些简单操作命令

```shell
# 集群健康状态查看
[root@lab ~]# etcdctl cluster-health
member b4b07e4c725567ef is healthy: got healthy result from http://192.168.1.201:2379
member de5365f8233167d3 is healthy: got healthy result from http://192.168.56.4:2379
member f6e21250ef798b6d is healthy: got healthy result from http://192.168.56.3:2379
cluster is healthy

# 通过curl命令查看指定主机的健康状态信息
[root@lab ~]# curl http://192.168.56.3:2379/health
{"health":"true"}

# 删除键值
etcdctl rm hello

# 创建目录
etcdctl mkdir testdir
# 目录添加数据
[root@lab ~]# etcdctl set testdir/test1 test1
test1
[root@lab ~]# etcdctl set testdir/test2 test2
test2
# 列出目录下条目
[root@node2 ~]# etcdctl ls testdir
/testdir/test2
/testdir/test1
# 删除目录（确保目录下无数据，否则报错）
[root@node2 ~]# etcdctl rmdir testdir

# 检测一对键值的变化，检测到变化 输出并退出检测
[root@node2 ~]# etcdctl watch hello
shijie
# 另一台更新数据
[root@lab ~]# etcdctl update hello "shijie"
shijie

通过curl命令进行键值的增删该查
# 添加
curl http://127.0.0.1:2379/v2/keys/message -XPUT -d value="Hello world"
# 删除
curl http://127.0.0.1:2379/v2/keys/message -XDELETE
# 查询键值是否存在
curl http://127.0.0.1:2379/v2/keys/message
# 更新数据 输出信息会有原来数据
curl http://127.0.0.1:2379/v2/keys/message -XPUT -d value="Hello etcd"
```

