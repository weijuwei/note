# 单机shards配置

mongoDB版本为4.4.0
操作系统为Windows10

mongodb目录
```powershell
PS D:\Desktop\mongodb> dir
  目录: D:\Desktop\mongodb
Mode        LastWriteTime     Length Name
----        -------------     ------ ----
d-----    2020/8/28   8:14        bin
d-----    2020/8/28   8:14        db
d-----    2020/8/27   18:24        db1
d-----    2020/8/27   18:24        db2
d-----    2020/8/27   18:24        db3
d-----    2020/8/27   18:38        shard
------    2020/7/25   14:59     30608 LICENSE-Community.txt
-a----    2020/8/24   8:09       0 mongod.lock
------    2020/7/25   14:59     16726 MPL-2
------    2020/7/25   14:59      1977 README
shard目录
PS D:\Desktop\mongodb\shard> dir
  目录: D:\Desktop\mongodb\shard
Mode        LastWriteTime     Length Name
----        -------------     ------ ----
d-----    2020/8/27   18:57        config
d-----    2020/8/28   7:47        logs
d-----    2020/8/28   8:13        s1
d-----    2020/8/28   8:00        s2
d-----    2020/8/28   8:00        s3
```
## shard servers

单机实验 每个shard没有配置repl集

###  配置文件模板

```shell
systemLog: # 日志
 destination: file
 path: d:\Desktop\mongodb\shard\logs\s1.log
 logAppend: true
storage: # 数据存储
 dbPath: d:\Desktop\mongodb\shard\s1
net:
 bindIp: 0.0.0.0
 port: xxxxx  # 修改端口
#replication:
# replSetName: rs0
sharding: # shard role
 clusterRole: configsvr
```
### 28017

```shell
..\bin\mongod.exe --port 28017 --dbpath="d:\Desktop\mongodb\shard\s1" --logpath="d:\Desktop\mongodb\shard\logs\s1.log"  --logappend --shardsvr
```
### 28018
```shell
..\bin\mongod.exe --port 28018 --dbpath="d:\Desktop\mongodb\shard\s2" --logpath="d:\Desktop\mongodb\shard\logs\s2.log" --logappend --shardsvr
```
### 28019
```shell
..\bin\mongod.exe --port 28019 --dbpath="d:\Desktop\mongodb\shard\s3" --logpath="d:\Desktop\mongodb\shard\logs\s3.log" --logappend --shardsvr
```
## config servers
mongod实例，存储了整个 ClusterMetadata，其中包括 chunk信息。

配置config server复制集

### 配置文件模板

```yaml
systemLog: # 日志
 destination: file
 path: d:\Desktop\mongodb\shard\logs\c0.log
 logAppend: true
storage: # 数据存储
 dbPath: d:\Desktop\mongodb\shard\config\c0
net:
 bindIp: 0.0.0.0
 port: 28010  # 端口
replication:
 replSetName: rs0
sharding: # shard role
 clusterRole: configsvr
```
### 28010
```powershell
..\bin\mongod.exe --port 28010 --dbpath="d:\Desktop\mongodb\shard\config\c0" --logpath="d:\Desktop\mongodb\shard\logs\config_28010.log" --logappend  --replSet rs0 --configsvr
```
### 28011
```powershell
..\bin\mongod.exe --port 28011 --dbpath="d:\Desktop\mongodb\shard\config\c1" --logpath="d:\Desktop\mongodb\shard\logs\config_28011.log" --logappend  --replSet rs0 --configsvr
```
### 28012
```powershell
..\bin\mongod.exe --port 28012 --dbpath="d:\Desktop\mongodb\shard\config\c2" --logpath="d:\Desktop\mongodb\shard\logs\config_28012.log" --logappend  --replSet rs0 --configsvr
```
### 查看config repl集状态
```shell
rs0:PRIMARY> rs.status().members
[
    {
        "_id" : 0,
        "name" : "localhost:28010",
        "health" : 1,
        "state" : 1,
        "stateStr" : "PRIMARY",
        "uptime" : 671,
        "optime" : {
            "ts" : Timestamp(1598572513, 8),
            "t" : NumberLong(1)
        },
        "optimeDate" : ISODate("2020-08-27T23:55:13Z"),
        "syncSourceHost" : "",
        "syncSourceId" : -1,
        "infoMessage" : "",
        "electionTime" : Timestamp(1598571921, 2),
        "electionDate" : ISODate("2020-08-27T23:45:21Z"),
        "configVersion" : 3,
        "configTerm" : 1,
        "self" : true,
        "lastHeartbeatMessage" : ""
    },
    {
        "_id" : 1,
        "name" : "localhost:28011",
        "health" : 1,
        "state" : 2,
        "stateStr" : "SECONDARY",
        "uptime" : 565,
        "optime" : {
            "ts" : Timestamp(1598572510, 1),
            "t" : NumberLong(1)
        },
        "optimeDurable" : {
            "ts" : Timestamp(1598572510, 1),
            "t" : NumberLong(1)
        },
        "optimeDate" : ISODate("2020-08-27T23:55:10Z"),
        "optimeDurableDate" : ISODate("2020-08-27T23:55:10Z"),
        "lastHeartbeat" : ISODate("2020-08-27T23:55:11.875Z"),
        "lastHeartbeatRecv" : ISODate("2020-08-27T23:55:11.866Z"),
        "pingMs" : NumberLong(5),
        "lastHeartbeatMessage" : "",
        "syncSourceHost" : "localhost:28010",
        "syncSourceId" : 0,
        "infoMessage" : "",
        "configVersion" : 3,
        "configTerm" : 1
    },
    {
        "_id" : 2,
        "name" : "localhost:28012",
        "health" : 1,
        "state" : 2,
        "stateStr" : "SECONDARY",
        "uptime" : 557,
        "optime" : {
            "ts" : Timestamp(1598572510, 1),
            "t" : NumberLong(1)
        },
        "optimeDurable" : {
            "ts" : Timestamp(1598572510, 1),
            "t" : NumberLong(1)
        },
        "optimeDate" : ISODate("2020-08-27T23:55:10Z"),
        "optimeDurableDate" : ISODate("2020-08-27T23:55:10Z"),
        "lastHeartbeat" : ISODate("2020-08-27T23:55:11.875Z"),
        "lastHeartbeatRecv" : ISODate("2020-08-27T23:55:11.879Z"),
        "pingMs" : NumberLong(5),
        "lastHeartbeatMessage" : "",
        "syncSourceHost" : "localhost:28011",
        "syncSourceId" : 1,
        "infoMessage" : "",
        "configVersion" : 3,
        "configTerm" : 1
    }
]
```
### 配置完mongos后查看信息
```shell
rs0:PRIMARY> use config
switched to db config
rs0:PRIMARY> show tables
actionlog
changelog
chunks
collections
lockpings
locks
migrations
mongos
shards
system.indexBuilds
tags
transactions
version

#查看shards信息
rs0:PRIMARY> db.shards.find()
{ "_id" : "shard0000", "host" : "localhost:28017", "state" : 1 }
{ "_id" : "shard0001", "host" : "localhost:28018", "state" : 1 }
{ "_id" : "shard0002", "host" : "localhost:28019", "state" : 1 }

# 查看mongos信息
rs0:PRIMARY> db.mongos.find().pretty()
{
    "_id" : "DESKTOP-FA6MB81:40000",
    "advisoryHostFQDNs" : [ ],
    "mongoVersion" : "4.4.0",
    "ping" : ISODate("2020-08-27T23:57:36.866Z"),
    "up" : NumberLong(627),
    "waiting" : true
}

# 查看chunks信息
rs0:PRIMARY> db.chunks.find()
{ "_id" : ObjectId("5f48479bd7764e17ceb0e3c7"), "lastmod" : Timestamp(2, 1), "lastmodEpoch" : ObjectId("5f48479b20f2305e5f3a3291"), "ns" : "config.system.sessions", "min" : { "_id" : { "$minKey" : 1 } }, "max" : { "_id" : { "id" : UUID("00400000-0000-0000-0000-000000000000") } }, "shard" : "shard0000", "history" : [ { "validAfter" : Timestamp(1598572443, 3), "shard" : "shard0000" } ] }
。。。。。
```
## Router mongos
```powershell
..\bin\mongos.exe --port 40000 --configdb "rs0/localhost:28010,localhost:28011,localhost:28012" --logpath="d:\Desktop\mongodb\shard\logs\route.log" --logappend --noauth
```
连接控制台设置
```shell
 ..\bin\mongo.exe --port 40000 admin
mongos> db.runCommand({addshard:"localhost:28017"})
mongos> db.runCommand({addshard:"localhost:28018"})
mongos> db.runCommand({addshard:"localhost:28019"})
```
### addshard 1
```shell
mongos> db.runCommand({addshard:"localhost:28017"})
{
    "shardAdded" : "shard0000",
    "ok" : 1,
    "operationTime" : Timestamp(1598572274, 4),
    "$clusterTime" : {
        "clusterTime" : Timestamp(1598572274, 4),
        "signature" : {
            "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
            "keyId" : NumberLong(0)
        }
    }
}
```
### addshard 2
```shell
mongos> db.runCommand({addshard:"localhost:28018"})
{
    "shardAdded" : "shard0001",
    "ok" : 1,
    "operationTime" : Timestamp(1598572282, 3),
    "$clusterTime" : {
        "clusterTime" : Timestamp(1598572282, 3),
        "signature" : {
            "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
            "keyId" : NumberLong(0)
        }
    }
}
```
### addshard3
```shell
mongos> db.runCommand({addshard:"localhost:28019"})
{
    "shardAdded" : "shard0002",
    "ok" : 1,
    "operationTime" : Timestamp(1598572285, 3),
    "$clusterTime" : {
        "clusterTime" : Timestamp(1598572285, 3),
        "signature" : {
            "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
            "keyId" : NumberLong(0)
        }
    }
}
```
### 查看状态
```shell
mongos> sh.status()
--- Sharding Status ---
 sharding version: {
    "_id" : 1,
    "minCompatibleVersion" : 5,
    "currentVersion" : 6,
    "clusterId" : ObjectId("5f484591d7764e17ceb0d272")
 }
 shards:
    { "_id" : "shard0000", "host" : "localhost:28017", "state" : 1 }
    { "_id" : "shard0001", "host" : "localhost:28018", "state" : 1 }
    { "_id" : "shard0002", "host" : "localhost:28019", "state" : 1 }
 active mongoses:
    "4.4.0" : 1
 autosplit:
    Currently enabled: yes
 balancer:
    Currently enabled: yes
    Currently running: no
    Failed balancer rounds in last 5 attempts: 0
    Migration Results for the last 24 hours:
        No recent migrations
 databases:
    { "_id" : "config", "primary" : "config", "partitioned" : true }
mongos>
```
## 数据测试操作

### 为指定数据库配置sharding
```shell
mongos> sh.enableSharding("test")
{
    "ok" : 1,
    "operationTime" : Timestamp(1598574262, 5),
    "$clusterTime" : {
        "clusterTime" : Timestamp(1598574262, 5),
        "signature" : {
            "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
            "keyId" : NumberLong(0)
        }
    }
}
```
### 指定shard key，并设置分片计算方式
```shell
mongos> sh.shardCollection("test.user",{id:"hashed"})
{
    "collectionsharded" : "test.user",
    "collectionUUID" : UUID("429f2c18-d43d-45db-a45f-365973e63d51"),
    "ok" : 1,
    "operationTime" : Timestamp(1598574462, 13),
    "$clusterTime" : {
        "clusterTime" : Timestamp(1598574462, 13),
        "signature" : {
            "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
            "keyId" : NumberLong(0)
        }
    }
}
```
### 插入数据测试
```shell
mongos> for(i=1;i<1000;i++){db.user.insert({id:i,name:"Tom"})};
```
### 连接shard server进行查看

- 28017
```shell
  > use test
  switched to db test
  > db.user.find()
  { "_id" : ObjectId("5f4850849c81caff99d8f787"), "id" : 6, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f789"), "id" : 8, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f78d"), "id" : 12, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f795"), "id" : 20, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f796"), "id" : 21, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f79b"), "id" : 26, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f79c"), "id" : 27, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7a1"), "id" : 32, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7a2"), "id" : 33, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7a9"), "id" : 40, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7ad"), "id" : 44, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7b5"), "id" : 52, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7bd"), "id" : 60, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7c8"), "id" : 71, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7ca"), "id" : 73, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7cb"), "id" : 74, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7cc"), "id" : 75, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7cd"), "id" : 76, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7ce"), "id" : 77, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7cf"), "id" : 78, "name" : "Tom" }
  Type "it" for more
  > db.user.find().count()
  310
```
- 28018
```shell
  > use test
  switched to db test
  > db.user.find()
  { "_id" : ObjectId("5f4850849c81caff99d8f783"), "id" : 2, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f784"), "id" : 3, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f785"), "id" : 4, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f78c"), "id" : 11, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f791"), "id" : 16, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f798"), "id" : 23, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f799"), "id" : 24, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f79a"), "id" : 25, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f79e"), "id" : 29, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f79f"), "id" : 30, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7a6"), "id" : 37, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7a7"), "id" : 38, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7aa"), "id" : 41, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7ab"), "id" : 42, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7b0"), "id" : 47, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7b1"), "id" : 48, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7b3"), "id" : 50, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7b7"), "id" : 54, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7b8"), "id" : 55, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7bb"), "id" : 58, "name" : "Tom" }
  Type "it" for more
  > db.user.find().count()
  345
```
- 28019
```shell
  > use test
  switched to db test
  > db.user.find()
  { "_id" : ObjectId("5f4850849c81caff99d8f782"), "id" : 1, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f786"), "id" : 5, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f788"), "id" : 7, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f78a"), "id" : 9, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f78b"), "id" : 10, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f78e"), "id" : 13, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f78f"), "id" : 14, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f790"), "id" : 15, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f792"), "id" : 17, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f793"), "id" : 18, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f794"), "id" : 19, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f797"), "id" : 22, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f79d"), "id" : 28, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7a0"), "id" : 31, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7a3"), "id" : 34, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7a4"), "id" : 35, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7a5"), "id" : 36, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7a8"), "id" : 39, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7ac"), "id" : 43, "name" : "Tom" }
  { "_id" : ObjectId("5f4850849c81caff99d8f7ae"), "id" : 45, "name" : "Tom" }
  Type "it" for more
  > db.user.find().count()
  344
```