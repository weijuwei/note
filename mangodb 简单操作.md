#### 运行环境

- mongodb 4.4.0
- windows 10

#### 数据CRUD相关

```json
db.inventory.insertMany([
   { item: "journal", qty: 25, size: { h: 14, w: 21, uom: "cm" }, status: "A" },
   { item: "notebook", qty: 50, size: { h: 8.5, w: 11, uom: "in" }, status: "A" },
   { item: "paper", qty: 100, size: { h: 8.5, w: 11, uom: "in" }, status: "D" },
   { item: "planner", qty: 75, size: { h: 22.85, w: 30, uom: "cm" }, status: "D" },
   { item: "postcard", qty: 45, size: { h: 10, w: 15.25, uom: "cm" }, status: "A" }
]);

db.students.insertMany([])


db.inventory.find().pretty()
{
        "_id" : ObjectId("5f3c725391f8e0b585841936"),
        "item" : "canvas",
        "qty" : 100,
        "tags" : [
                "cotton"
        ],
        "size" : {
                "h" : 28,
                "w" : 35.5,
                "uom" : "cm"
        }
}
{
        "_id" : ObjectId("5f3c730b91f8e0b585841937"),
        "item" : "journal",
        "qty" : 25,
        "size" : {
                "h" : 14,
                "w" : 21,
                "uom" : "cm"
        },
        "status" : "A"
}
{
        "_id" : ObjectId("5f3c730b91f8e0b585841938"),
        "item" : "notebook",
        "qty" : 50,
        "size" : {
                "h" : 8.5,
                "w" : 11,
                "uom" : "in"
        },
        "status" : "A"
}
{
        "_id" : ObjectId("5f3c730b91f8e0b585841939"),
        "item" : "paper",
        "qty" : 100,
        "size" : {
                "h" : 8.5,
                "w" : 11,
                "uom" : "in"
        },
        "status" : "D"
}
{
        "_id" : ObjectId("5f3c730b91f8e0b58584193a"),
        "item" : "planner",
        "qty" : 75,
        "size" : {
                "h" : 22.85,
                "w" : 30,
                "uom" : "cm"
        },
        "status" : "D"
}
{
        "_id" : ObjectId("5f3c730b91f8e0b58584193b"),
        "item" : "postcard",
        "qty" : 45,
        "size" : {
                "h" : 10,
                "w" : 15.25,
                "uom" : "cm"
        },
        "status" : "A"
}


db.bios.insertMany([
   {
       "_id" : 1,
       "name" : {
           "first" : "John",
           "last" : "Backus"
       },
       "birth" : ISODate("1924-12-03T05:00:00Z"),
       "death" : ISODate("2007-03-17T04:00:00Z"),
       "contribs" : [
           "Fortran",
           "ALGOL",
           "Backus-Naur Form",
           "FP"
       ],
       "awards" : [
           {
               "award" : "W.W. McDowell Award",
               "year" : 1967,
               "by" : "IEEE Computer Society"
           },
           {
               "award" : "National Medal of Science",
               "year" : 1975,
               "by" : "National Science Foundation"
           },
           {
               "award" : "Turing Award",
               "year" : 1977,
               "by" : "ACM"
           },
           {
               "award" : "Draper Prize",
               "year" : 1993,
               "by" : "National Academy of Engineering"
           }
       ]
   },
   {
       "_id" : ObjectId("51df07b094c6acd67e492f41"),
       "name" : {
           "first" : "John",
           "last" : "McCarthy"
       },
       "birth" : ISODate("1927-09-04T04:00:00Z"),
       "death" : ISODate("2011-12-24T05:00:00Z"),
       "contribs" : [
           "Lisp",
           "Artificial Intelligence",
           "ALGOL"
       ],
       "awards" : [
           {
               "award" : "Turing Award",
               "year" : 1971,
               "by" : "ACM"
           },
           {
               "award" : "Kyoto Prize",
               "year" : 1988,
               "by" : "Inamori Foundation"
           },
           {
               "award" : "National Medal of Science",
               "year" : 1990,
               "by" : "National Science Foundation"
           }
       ]
   },
   {
       "_id" : 3,
       "name" : {
           "first" : "Grace",
           "last" : "Hopper"
       },
       "title" : "Rear Admiral",
       "birth" : ISODate("1906-12-09T05:00:00Z"),
       "death" : ISODate("1992-01-01T05:00:00Z"),
       "contribs" : [
           "UNIVAC",
           "compiler",
           "FLOW-MATIC",
           "COBOL"
       ],
       "awards" : [
           {
               "award" : "Computer Sciences Man of the Year",
               "year" : 1969,
               "by" : "Data Processing Management Association"
           },
           {
               "award" : "Distinguished Fellow",
               "year" : 1973,
               "by" : " British Computer Society"
           },
           {
               "award" : "W. W. McDowell Award",
               "year" : 1976,
               "by" : "IEEE Computer Society"
           },
           {
               "award" : "National Medal of Technology",
               "year" : 1991,
               "by" : "United States"
           }
       ]
   },
   {
       "_id" : 4,
       "name" : {
           "first" : "Kristen",
           "last" : "Nygaard"
       },
       "birth" : ISODate("1926-08-27T04:00:00Z"),
       "death" : ISODate("2002-08-10T04:00:00Z"),
       "contribs" : [
           "OOP",
           "Simula"
       ],
       "awards" : [
           {
               "award" : "Rosing Prize",
               "year" : 1999,
               "by" : "Norwegian Data Association"
           },
           {
               "award" : "Turing Award",
               "year" : 2001,
               "by" : "ACM"
           },
           {
               "award" : "IEEE John von Neumann Medal",
               "year" : 2001,
               "by" : "IEEE"
           }
       ]
   },
   {
       "_id" : 5,
       "name" : {
           "first" : "Ole-Johan",
           "last" : "Dahl"
       },
       "birth" : ISODate("1931-10-12T04:00:00Z"),
       "death" : ISODate("2002-06-29T04:00:00Z"),
       "contribs" : [
           "OOP",
           "Simula"
       ],
       "awards" : [
           {
               "award" : "Rosing Prize",
               "year" : 1999,
               "by" : "Norwegian Data Association"
           },
           {
               "award" : "Turing Award",
               "year" : 2001,
               "by" : "ACM"
           },
           {
               "award" : "IEEE John von Neumann Medal",
               "year" : 2001,
               "by" : "IEEE"
           }
       ]
   },
   {
       "_id" : 6,
       "name" : {
           "first" : "Guido",
           "last" : "van Rossum"
       },
       "birth" : ISODate("1956-01-31T05:00:00Z"),
       "contribs" : [
           "Python"
       ],
       "awards" : [
           {
               "award" : "Award for the Advancement of Free Software",
               "year" : 2001,
               "by" : "Free Software Foundation"
           },
           {
               "award" : "NLUUG Award",
               "year" : 2003,
               "by" : "NLUUG"
           }
       ]
   },
   {
       "_id" : ObjectId("51e062189c6ae665454e301d"),
       "name" : {
           "first" : "Dennis",
           "last" : "Ritchie"
       },
       "birth" : ISODate("1941-09-09T04:00:00Z"),
       "death" : ISODate("2011-10-12T04:00:00Z"),
       "contribs" : [
           "UNIX",
           "C"
       ],
       "awards" : [
           {
               "award" : "Turing Award",
               "year" : 1983,
               "by" : "ACM"
           },
           {
               "award" : "National Medal of Technology",
               "year" : 1998,
               "by" : "United States"
           },
           {
               "award" : "Japan Prize",
               "year" : 2011,
               "by" : "The Japan Prize Foundation"
           }
       ]
   },
   {
       "_id" : 8,
       "name" : {
           "first" : "Yukihiro",
           "aka" : "Matz",
           "last" : "Matsumoto"
       },
       "birth" : ISODate("1965-04-14T04:00:00Z"),
       "contribs" : [
           "Ruby"
       ],
       "awards" : [
           {
               "award" : "Award for the Advancement of Free Software",
               "year" : "2011",
               "by" : "Free Software Foundation"
           }
       ]
   },
   {
       "_id" : 9,
       "name" : {
           "first" : "James",
           "last" : "Gosling"
       },
       "birth" : ISODate("1955-05-19T04:00:00Z"),
       "contribs" : [
           "Java"
       ],
       "awards" : [
           {
               "award" : "The Economist Innovation Award",
               "year" : 2002,
               "by" : "The Economist"
           },
           {
               "award" : "Officer of the Order of Canada",
               "year" : 2007,
               "by" : "Canada"
           }
       ]
   },
   {
       "_id" : 10,
       "name" : {
           "first" : "Martin",
           "last" : "Odersky"
       },
       "contribs" : [
           "Scala"
       ]
   }

] )

mongo "mongodb+srv://cluster0.oayyo.mongodb.net/test" --username weijuwei --password 583112952

> db.inventory.find({tags:{$exists:true}})
> db.inventory.aggregate([{$group:{_id:'$item',counts:{$sum:"$qty"}}}])
> db.inventory.aggregate([{$group:{_id:'$item',counts:{$sum:"$qty"}}},{$match:{_id:"paper"}}])
> db.inventory.aggregate([{$group:{_id:'$item',counts:{$sum:1}}},{$match:{counts:{$lt:2}}}])
> db.inventory.aggregate([{$group:{_id:'$item',counts:{$sum:"$qty"}}}])

------------------------------
db.hhw.insert({
results: [ 
{ item: "a", qty: 26, tags: ["blank", "red"], dim_cm: [ 1, 10 ] },
{ item: "a", qty: 27, tags: ["blank", "red"], dim_cm: [ 15, 30 ] },
{ item: "a", qty: 28, tags: ["blank", "red"], dim_cm: [ 50, 70 ] },
{ item: "b", qty: 27, tags: ["blank", "red"], dim_cm: [ 80, 90 ] }
]
});

> db.hhw.aggregate([{$unwind:"$results"},{$match:{"results.item":"a"}}])
----------------------------------------------------
# https://github.com/tapdata/geektime-mongodb-course
> db.orders.aggregate([
    {$match:{
        status: "completed", orderDate: {
          $gte: ISODate("2019-01-01"),
          $lt: ISODate("2019-04-01")}}},
    {$group: { 
        _id: null,
        total: {$sum:"$total"},
        shippingFee:{$sum: "$shippingFee"},
        count:{$sum:1}}}
])
result:
{
        "_id" : null,
        "total" : NumberDecimal("2592322"),
        "shippingFee" : NumberDecimal("44054.00"),
        "count" : 5875
}

# unwind 打散数组字段
> db.orders.aggregate([{$unwind:"$orderLines"},{$group:{_id:null,total_price:{$sum:"$orderLines.price"} ,total_cost:{$sum:"$orderLines.cost"}}}]).pretty()
{
        "_id" : null,
        "total_price" : NumberDecimal("44019609.00"),
        "total_cost" : NumberDecimal("39617836.47")
}

--------------------------------------------------------------------

> db.contents.insertOne({"name":"Tom","company":"xl","group_ids":[1,2,3]})
> db.groups.insertMany([{group_id:1,name:"Friends"},{group_id:2,name:"IT"},{group_id:3,name:"OPS"}])
> db.contents.aggregate([{$lookup:{from:"groups",localField:"group_ids",foreignField:"group_id",as:"group"}}]).pretty()
{
        "_id" : ObjectId("5f44e2e918a9c0bb7b89ee88"),
        "name" : "Tom",
        "company" : "xl",
        "group_ids" : [
                1,
                2,
                3
        ],
        "group" : [
                {
                        "_id" : ObjectId("5f44e37818a9c0bb7b89ee89"),
                        "group_id" : 1,
                        "name" : "Friends"
                },
                {
                        "_id" : ObjectId("5f44e37818a9c0bb7b89ee8a"),
                        "group_id" : 2,
                        "name" : "IT"
                },
                {
                        "_id" : ObjectId("5f44e37818a9c0bb7b89ee8b"),
                        "group_id" : 3,
                        "name" : "OPS"
                }
        ]
}
> db.contents.updateOne({name:"Tom"},{$pull:{group_ids:1}}) #删除数组的一个元素
```
#### 复制集

一主二从
node1  28017
node2  28018
node3  28019

```shell
node1 :mongodb.conf 配置文件
systemLog:
  destination: file
  path: d:\Desktop\mongodb\db1\mongod.log
  logAppend: true
storage:
  dbPath: d:\Desktop\mongodb\db1
net:
  bindIp: 0.0.0.0
  port: 28017
replication:
  replSetName: rs0

node1:
> rs.initiate()
rs0:PRIMARY> rs.add("node2:28018")
rs0:PRIMARY> rs.add("node2:28019")

# 查看集群成员
rs0:PRIMARY> rs.status().members
[
        {
                "_id" : 0,
                "name" : "DESKTOP-FA6MB81:28017",
                "health" : 1,
                "state" : 1,
                "stateStr" : "PRIMARY",
                "uptime" : 1181,
                "optime" : {
                        "ts" : Timestamp(1598440518, 1),
                        "t" : NumberLong(2)
                },
                "optimeDate" : ISODate("2020-08-26T11:15:18Z"),
                "syncSourceHost" : "",
                "syncSourceId" : -1,
                "infoMessage" : "",
                "electionTime" : Timestamp(1598439357, 1),
                "electionDate" : ISODate("2020-08-26T10:55:57Z"),
                "configVersion" : 4,
                "configTerm" : 2,
                "self" : true,
                "lastHeartbeatMessage" : ""
        },
        {
                "_id" : 1,
                "name" : "DESKTOP-FA6MB81:28018",
                "health" : 1,
                "state" : 2,
                "stateStr" : "SECONDARY",
                "uptime" : 1172,
                "optime" : {
                        "ts" : Timestamp(1598440518, 1),
                        "t" : NumberLong(2)
                },
                "optimeDurable" : {
                        "ts" : Timestamp(1598440518, 1),
                        "t" : NumberLong(2)
                },
                "optimeDate" : ISODate("2020-08-26T11:15:18Z"),
                "optimeDurableDate" : ISODate("2020-08-26T11:15:18Z"),
                "lastHeartbeat" : ISODate("2020-08-26T11:15:21.271Z"),
                "lastHeartbeatRecv" : ISODate("2020-08-26T11:15:21.259Z"),
                "pingMs" : NumberLong(0),
                "lastHeartbeatMessage" : "",
                "syncSourceHost" : "DESKTOP-FA6MB81:28017",
                "syncSourceId" : 0,
                "infoMessage" : "",
                "configVersion" : 4,
                "configTerm" : 2
        },
        {
                "_id" : 2,
                "name" : "DESKTOP-FA6MB81:28019",
                "health" : 1,
                "state" : 2,
                "stateStr" : "SECONDARY",
                "uptime" : 1170,
                "optime" : {
                        "ts" : Timestamp(1598440508, 1),
                        "t" : NumberLong(2)
                },
                "optimeDurable" : {
                        "ts" : Timestamp(1598440508, 1),
                        "t" : NumberLong(2)
                },
                "optimeDate" : ISODate("2020-08-26T11:15:08Z"),
                "optimeDurableDate" : ISODate("2020-08-26T11:15:08Z"),
                "lastHeartbeat" : ISODate("2020-08-26T11:15:21.271Z"),
                "lastHeartbeatRecv" : ISODate("2020-08-26T11:15:21.285Z"),
                "pingMs" : NumberLong(0),
                "lastHeartbeatMessage" : "",
                "syncSourceHost" : "DESKTOP-FA6MB81:28018",
                "syncSourceId" : 1,
                "infoMessage" : "",
                "configVersion" : 4,
                "configTerm" : 2
        }
]
rs0:PRIMARY>


#修改集群配置
cnf = rs.conf()
cnf.members[2].priority = 0
cnf.members[2].slaveDelay = 10  # 修改从节点延迟写入时间

rs.reconfig(cfg)

# 等待10秒写入成功
rs0:PRIMARY> db.test.insert({count:1},{writeConcern:{w:3}})  # {w:"majority"}
WriteResult({ "nInserted" : 1 })
rs0:PRIMARY>

# 从库查询报错
rs0:SECONDARY> db.test.find()
Error: error: {
        "topologyVersion" : {
                "processId" : ObjectId("5f463fad7995b68d170a0306"),
                "counter" : NumberLong(10)
        },
        "operationTime" : Timestamp(1598488651, 1),
        "ok" : 0,
        "errmsg" : "not master and slaveOk=false",
        "code" : 13435,
        "codeName" : "NotMasterNoSlaveOk",
        "$clusterTime" : {
                "clusterTime" : Timestamp(1598488651, 1),
                "signature" : {
                        "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
                        "keyId" : NumberLong(0)
                }
        }
}

#解决
rs0:SECONDARY> db.setSlaveOk()
rs0:SECONDARY> db.test.find()
{ "_id" : ObjectId("5f46408f079259edc4a06291"), "count" : 1 }
{ "_id" : ObjectId("5f4640bc079259edc4a06292"), "count" : 1 }
{ "_id" : ObjectId("5f4640bf079259edc4a06293"), "count" : 1 }
{ "_id" : ObjectId("5f46415f079259edc4a06294"), "count" : 1 }
{ "_id" : ObjectId("5f464248079259edc4a06295"), "count" : 1 }
```
#### 分片
> https://docs.mongodb.com/manual/tutorial/deploy-shard-cluster/


Shard:
用于存储实际的数据块，实际生产环境中一个shard server角色可由几台机器组个一个replica set承担，防止主机单点故障
shardserver配置文件
```yaml
systemLog: # 日志
  destination: file
  path: d:\Desktop\mongodb\shard\logs\s1.log
  logAppend: true
storage:  # 数据存储
  dbPath: d:\Desktop\mongodb\shard\s1
net:
  bindIp: 0.0.0.0
  port: 28017   # 端口
#replication:
#  replSetName: rs0
sharding:  # shard role
  clusterRole: shardsvr
```

Config Server:
mongod实例，存储了整个 ClusterMetadata，其中包括 chunk信息。
config server配置文件
```yaml
systemLog: # 日志
  destination: file
  path: d:\Desktop\mongodb\shard\logs\c0.log
  logAppend: true
storage:  # 数据存储
  dbPath: d:\Desktop\mongodb\shard\config\c0
net:
  bindIp: 0.0.0.0
  port: 28010   # 端口
replication:
  replSetName: rs0
sharding:  # shard role
  clusterRole: configsvr
```

Query Routers:
前端路由，客户端由此接入，且让整个集群看上去像单一数据库，前端应用可以透明使用。
```shell
 ..\bin\mongos.exe --port 40000 --configdb "rs0/localhost:28010,localhost:28011,localhost:28012" --logpath="d:\Desktop\mongodb\shard\logs\route.log" --logappend --noauth
```
查看状态信息

连接mongos查看
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
        {  "_id" : "shard0000",  "host" : "localhost:28017",  "state" : 1 }
        {  "_id" : "shard0001",  "host" : "localhost:28018",  "state" : 1 }
        {  "_id" : "shard0002",  "host" : "localhost:28019",  "state" : 1 }

```

在config server上查看信息

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
rs0:PRIMARY> db.shards.find()
{ "_id" : "shard0000", "host" : "localhost:28017", "state" : 1 }
{ "_id" : "shard0001", "host" : "localhost:28018", "state" : 1 }
{ "_id" : "shard0002", "host" : "localhost:28019", "state" : 1 }
rs0:PRIMARY> db.mongos.find()
{ "_id" : "DESKTOP-FA6MB81:40000", "advisoryHostFQDNs" : [ ], "mongoVersion" : "4.4.0", "ping" : ISODate("2020-08-27T23:57:15.545Z"), "up" : NumberLong(605), "waiting" : true }
```

插入数据测试
在mongos上设置需要sharding的数据库，并指定shard key及shard算法
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
#设置shard key及算法
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

插入1000条数据
```
mongos> for(i=1;i<1000;i++){db.user.insert({id:i,name:"Tom"})}
```

在3个shard server上分别查看数据分布情况
```shell
> use test
switched to db test

> db.user.find().count()
310

> db.user.find().count()
345

> db.user.find().count()
344
```