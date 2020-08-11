>https://ceph.readthedocs.io/en/latest/install/ceph-deploy/quick-ceph-deploy/

#### 环境

**节点**

- admin 192.168.20.101 管理节点

- node1 192.168.20.102  +5g磁盘

- node2 192.168.20.103  +5g磁盘

- node3 192.168.20.104  +5g磁盘

ceph-deploy:luminous

#### 准备

时间同步ntp

创建普通用户 加入sudo免密

```shell
useradd cephu
echo 1 | passwd --stdin cephu

[root@admin ~]# visudo 
cephu   ALL=(root)      NOPASSWD: ALL
```

在cephu用户配置访问互信

```shell
[cephu@admin my-cluster]$ ssh-keygen 
[cephu@admin my-cluster]$ ssh-copy-id cephu@node1
[cephu@admin my-cluster]$ ssh-copy-id cephu@node2
[cephu@admin my-cluster]$ ssh-copy-id cephu@node3

[cephu@admin .ssh]$ cat ~/.ssh/config 
Host node1
   Hostname node1
   User cephu
Host node2
   Hostname node2
   User cephu
Host node3
   Hostname node3
   User cephu
```

epel源

ceph-deply源和ceph源

```shell
[root@node1 yum.repos.d]# cat ceph.repo 
[ceph-deploy]
name=ceph_deploy
baseurl=https://mirrors.aliyun.com/ceph/rpm-luminous/el7/noarch/
enabled=1
gpgcheck=0

[ceph]
name=ceph_x86_64
baseurl=https://mirrors.aliyun.com/ceph/rpm-luminous/el7/x86_64/
enabled=1
gpgcheck=0
```

python-setuptools

```shell
sudo yum install python-setuptools -y
```

更新并在admin节点安装ceph-deploy

```shell
sudo yum update
sudo yum install ceph-deploy -y
```

#### 创建集群

在admin节点创建一个目录用来维护集群配置文件

```shell
[root@admin ~]# su - cephu
[cephu@admin ~]$ mkdir my-cluster
[cephu@admin ~]$ cd my-cluster/
```

```shell
[cephu@admin my-cluster]$ ceph-deploy new node1
[cephu@admin my-cluster]$ ls
ceph.conf  ceph-deploy-ceph.log  ceph.mon.keyrin
# 修改ceph.conf文件追加以下信息
[cephu@admin my-cluster]$ vim ceph.conf 
public network = 192.168.20.0/24
```

安装ceph包

```shell
# 使用ceph-deploy安装，容易超时，建议手动安装
[cephu@admin my-cluster]$ ceph-deploy install node1 node2 node3

#在各个主机上执行，手动安装相关包
[cephu@admin my-cluster]$ yum install ceph ceph-radosgw -y
```

初始化monitor

```shell
[cephu@admin my-cluster]$ ceph-deploy mon create-initial
```

拷贝相关配置文件和key到admin节点和ceph节点，以便免密使用CLI命令

```shell
[cephu@admin my-cluster]$ ceph-deploy admin node1 node2 node3
```

部署管理守护进程

```shell
[cephu@admin my-cluster]$ceph-deploy mgr create node1
```

添加三块OSDs(node1 node2 node3)

```shell
ceph-deploy osd create --data /dev/sdb node1
ceph-deploy osd create --data /dev/sdb node2
ceph-deploy osd create --data /dev/sdb node3
```

查看集群健康状况

```shell
[cephu@admin my-cluster]$ ssh node1 sudo ceph -s
  cluster:
    id:     f34701ec-789e-4406-9147-9ff7c543ac93
    health: HEALTH_OK
 
  services:
    mon: 1 daemons, quorum node1
    mgr: node1(active)
    osd: 3 osds: 3 up, 3 in
 
  data:
    pools:   0 pools, 0 pgs
    objects: 0  objects, 0 B
    usage:   3.0 GiB used, 12 GiB / 15 GiB avail
    pgs:     
```

**配置dashboard**

node1节点上使用cephu用户

创建密钥

```shell
[cephu@node1 ~]$ sudo ceph auth get-or-create mgr.node1 mon 'allow profile mgr' osd 'allow *' mds 'allow *'
[mgr.node1]
	key = AQD88wtfUWYjLxAADTIJr2OtvgPxXvTL0tejMA==
```

开启ceph-mgr管理域????

```shell
[cephu@node1 ~]$ sudo ceph-mgr -i node1
```

启用dashboard模块

```shell
[cephu@node1 ~]$ sudo ceph mgr module enable dashboard
```

绑定节点IP地址

```shell
[cephu@node1 ~]$ sudo ceph config-key set mgr/dashboard/node1/server_addr 192.168.20.102
set mgr/dashboard/node1/server_addr
[cephu@node1 ~]$

???
# 指定ip和端口
ceph config-key put mgr/dashboard/server_addr 192.168.20.102
ceph config-key put mgr/dashboard/server_port 7000    
```

追加/etc/ceph/ceph.conf

```shell
[mgr]
magr modules = dashboard
```

重启服务

```shell
systemctl restart ceph-mgr@node1.service
```

浏览器访问192.168.20.102:7000

#### RBD

```shell
# 创建pool
ceph osd pool create mytest 128 128

# 获取pool一些value
ceph osd pool get {pool_name} {key}
[root@node1 my-ceph]# ceph osd pool get mytest pg_num
pg_num: 128

# 获取object的replicas数量
[root@node1 my-ceph]# ceph osd dump | grep 'replicated size'
pool 2 'mytest' replicated size 3 min_size 2 crush_rule 0 object_hash rjenkins pg_num 128 pgp_num 128 last_change 32 flags hashpspool stripe_width 0

# 修改object replicas数量
ceph osd pool set mytest size 2

# 创建块设备image，并指定pool
rbd create -p pool_demo --image rbd-demo.img --size 5G

# 查看rbd image信息
[root@node1 my-ceph]# rbd info mytest/rbd_test.img
rbd image 'rbd_test.img':
	size 5GiB in 1280 objects
	order 22 (4MiB objects)
	block_name_prefix: rbd_data.85aa6b8b4567
	format: 2
	features: layering, exclusive-lock, object-map, fast-diff, deep-flatten
	flags: 
	create_timestamp: Thu Jul 16 16:59:33 2020

# rbd image扩容
[root@node1 my-ceph]# rbd resize -p mytest --image rbd_test.img --size 10G
Resizing image: 100% complete...done.
[root@node1 my-ceph]# rbd info mytest/rbd_test.img
rbd image 'rbd_test.img':
	size 10GiB in 2560 objects
	order 22 (4MiB objects)
	block_name_prefix: rbd_data.85aa6b8b4567
# 扩容后，已格式化的rbd image不会立即生效
resize2fs /dev/rbd0

# 创建rbd image map，之后可进行格式化和挂载操作
[root@node1 my-ceph]# rbd map rbd_test.img -p mytest
/dev/rbd0

# 取消image map
[root@node1 ceph]# rbd unmap /dev/rbd0


# 查看map
[root@node1 my-ceph]# rbd showmapped
id pool   image        snap device    
0  mytest rbd_test.img -    /dev/rbd0 

# 格式化rbd image并挂载
[root@node1 my-ceph]# mkfs.ext4 /dev/rbd0
mke2fs 1.42.9 (28-Dec-2013)
Discarding device blocks: done                            
Filesystem label=
OS type: Linux
Block size=4096 (log=2)
Fragment size=4096 (log=2)
Stride=1024 blocks, Stripe width=1024 blocks
655360 inodes, 2621440 blocks
131072 blocks (5.00%) reserved for the super user
First data block=0
Maximum filesystem blocks=2151677952
80 block groups
32768 blocks per group, 32768 fragments per group
8192 inodes per group
Superblock backups stored on blocks: 
	32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632

Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (32768 blocks): done
Writing superblocks and filesystem accounting information: done 

[root@node1 my-ceph]# mount /dev/rbd0 /mnt
[root@node1 my-ceph]# ls /mnt
lost+found

# 文件自动挂载设置 修改/etc/ceph/rbdmap，/etc.fstab
[root@node1 my-ceph]# vim /etc/ceph/rbdmap 
mytest/rbd_test.img id=admin.keyring=/etc/ceph/ceph.client.admin.keyring

[root@node1 my-ceph]# systemctl enable rbdmap.service

# 查看map
[root@node1 my-ceph]# rbd showmapped
id pool   image        snap device    
0  mytest rbd_test.img -    /dev/rbd0 


# 取消rbd map
rbd unmap /dev/rbd0
```

```shell
[root@node1 my-ceph]# rbd map rbd_test.img -p mytest
rbd: sysfs write failed
RBD image feature set mismatch. You can disable features unsupported by the kernel with "rbd feature disable mytest/rbd_test.img object-map fast-diff deep-flatten".
In some cases useful info is found in syslog - try "dmesg | tail".
rbd: map failed: (6) No such device or address
[root@node1 my-ceph]# rbd feature disable mytest/rbd_test.img deep-flatten
[root@node1 my-ceph]# rbd feature disable mytest/rbd_test.img fast-diff
[root@node1 my-ceph]# rbd feature disable mytest/rbd_test.img object-map
[root@node1 my-ceph]# rbd feature disable mytest/rbd_test.img exclusive-lock
[root@node1 my-ceph]# rbd map rbd_test.img -p mytest
/dev/rbd0
```

#### 扩展集群

再node2和node3上增加ceph monitor和ceph manager

```shell
ceph-deploy mon add node2
ceph-deploy mon add node3
ceph-deploy mgr create node2 node3
```

查看ceph基本状态

```shell
# ceph -s
  cluster:
    id:     f34701ec-789e-4406-9147-9ff7c543ac93
    health: HEALTH_OK
 
  services:
    mon: 3 daemons, quorum node1,node2,node3
    mgr: node1(active), standbys: node2, node3
    osd: 3 osds: 3 up, 3 in
 
  data:
    pools:   0 pools, 0 pgs
    objects: 0 objects, 0B
    usage:   3.01GiB used, 12.0GiB / 15.0GiB avail
    pgs: 
```

**mon相关一些操作**

```shell
# 查看mon的状态
[root@node1 ~]# ceph mon stat
e3: 3 mons at {node1=192.168.20.102:6789/0,node2=192.168.20.103:6789/0,node3=192.168.20.104:6789/0}, election epoch 62, leader 0 node1, quorum 0,1,2 node1,node2,node3

# 查看mon选举状态
[root@node1 ~]# ceph quorum_status | jq .
{
  "election_epoch": 62,
  "quorum": [
    0,
    1,
    2
  ],
  "quorum_names": [
    "node1",
    "node2",
    "node3"
  ],
  "quorum_leader_name": "node1",
  "monmap": {
    "epoch": 3,
    "fsid": "f34701ec-789e-4406-9147-9ff7c543ac93",
    "modified": "2020-07-14 09:37:36.994523",
    "created": "2020-07-14 08:51:07.572101",
    "features": {
      "persistent": [
        "kraken",
        "luminous"
      ],
      "optional": []
    },
    "mons": [
      {
        "rank": 0,
        "name": "node1",
        "addr": "192.168.20.102:6789/0",
        "public_addr": "192.168.20.102:6789/0"
      },
      {
        "rank": 1,
        "name": "node2",
        "addr": "192.168.20.103:6789/0",
        "public_addr": "192.168.20.103:6789/0"
      },
      {
        "rank": 2,
        "name": "node3",
        "addr": "192.168.20.104:6789/0",
        "public_addr": "192.168.20.104:6789/0"
      }
    ]
  }
}

# 查看mon的信息
[root@node1 ~]# ceph mon dump
dumped monmap epoch 3
epoch 3
fsid f34701ec-789e-4406-9147-9ff7c543ac93
last_changed 2020-07-14 09:37:36.994523
created 2020-07-14 08:51:07.572101
0: 192.168.20.102:6789/0 mon.node1
1: 192.168.20.103:6789/0 mon.node2
2: 192.168.20.104:6789/0 mon.node3

# 查看指定mon节点详细信息
[root@node1 ~]# ceph daemon mon.node1 mon_status
{
    "name": "node1",
    "rank": 0,
    "state": "leader",
    "election_epoch": 62,
    "quorum": [
        0,
        1,
        2
    ],
    "features": {
        "required_con": "153140804152475648",
        "required_mon": [
            "kraken",
            "luminous"
        ],
        "quorum_con": "4611087853746454523",
        "quorum_mon": [
            "kraken",
            "luminous"
        ]
    },
    "outside_quorum": [],
    "extra_probe_peers": [],
    "sync_provider": [],
    "monmap": {
        "epoch": 3,
        "fsid": "f34701ec-789e-4406-9147-9ff7c543ac93",
        "modified": "2020-07-14 09:37:36.994523",
        "created": "2020-07-14 08:51:07.572101",
        "features": {
            "persistent": [
                "kraken",
                "luminous"
            ],
            "optional": []
        },
        "mons": [
            {
                "rank": 0,
                "name": "node1",
                "addr": "192.168.20.102:6789/0",
                "public_addr": "192.168.20.102:6789/0"
            },
            {
                "rank": 1,
                "name": "node2",
                "addr": "192.168.20.103:6789/0",
                "public_addr": "192.168.20.103:6789/0"
            },
            {
                "rank": 2,
                "name": "node3",
                "addr": "192.168.20.104:6789/0",
                "public_addr": "192.168.20.104:6789/0"
            }
        ]
    },
    "feature_map": {
        "mon": {
            "group": {
                "features": "0x3ffddff8eeacfffb",
                "release": "luminous",
                "num": 1
            }
        },
        "osd": {
            "group": {
                "features": "0x3ffddff8eeacfffb",
                "release": "luminous",
                "num": 3
            }
        },
        "client": {
            "group": {
                "features": "0x3ffddff8eeacfffb",
                "release": "luminous",
                "num": 3
            }
        }
    }
}

# 删除一个mon节点
ceph mon remove [nodexxxx]

# 获取mon map
[root@node1 ~]# ceph mon getmap -o xx.txt
got monmap epoch 3
[root@node1 ~]# monmaptool --print xx.txt
monmaptool: monmap file xx.txt
epoch 3
fsid f34701ec-789e-4406-9147-9ff7c543ac93
last_changed 2020-07-14 09:37:36.994523
created 2020-07-14 08:51:07.572101
0: 192.168.20.102:6789/0 mon.node1
1: 192.168.20.103:6789/0 mon.node2
2: 192.168.20.104:6789/0 mon.node3

```

**osd的相关操作**

```shell
# 查看osd信息
[root@node1 ~]# ceph osd dump

# 磁盘对应的OSD ID
[root@node1 ~]# ceph osd tree
ID CLASS WEIGHT  TYPE NAME      STATUS REWEIGHT PRI-AFF 
-1       0.01469 root default                           
-3       0.00490     host node1                         
 0   hdd 0.00490         osd.0      up  1.00000 1.00000 
-5       0.00490     host node2                         
 1   hdd 0.00490         osd.1      up  1.00000 1.00000 
-7       0.00490     host node3                         
 2   hdd 0.00490         osd.2      up  1.00000 1.00000 

# 踢出指定osd
ceph osd out osd.[num]

# 删除 CRUSH 图的对应 OSD 
ceph osd crush remove osd[num]

# 删除指定osd
ceph osd rm osd.[num]

# 查看指定pool的objects
[root@node1 ~]# rados -p mytest ls | grep rbd_data.85aa6b8b4567
rbd_data.85aa6b8b4567.0000000000000433
rbd_data.85aa6b8b4567.0000000000000421
rbd_data.85aa6b8b4567.0000000000000021
rbd_data.85aa6b8b4567.0000000000000000
rbd_data.85aa6b8b4567.0000000000000431
rbd_data.85aa6b8b4567.0000000000000600
...

# 查看osd指定object的map信息 对应pg 主osd
[root@node1 ~]# ceph osd map mytest rbd_data.85aa6b8b4567.0000000000000400
osdmap e67 pool 'mytest' (2) object 'rbd_data.85aa6b8b4567.0000000000000400' -> pg 2.ca586edf (2.5f) -> up ([1,2,0], p1) acting ([1,2,0], p1)

# 查看指定块object的信息
[root@node1 ~]# rados -p mytest stat rbd_data.85aa6b8b4567.0000000000000400
mytest/rbd_data.85aa6b8b4567.0000000000000400 mtime 2020-07-28 16:55:49.000000, size 8192
```



**报错**

1、

```
[cephu@admin my-cluster]$ ceph-deploy new node1
Traceback (most recent call last):
  File "/bin/ceph-deploy", line 18, in <module>
    from ceph_deploy.cli import main
  File "/usr/lib/python2.7/site-packages/ceph_deploy/cli.py", line 1, in <module>
    import pkg_resources
ImportError: No module named pkg_resources
```

解决： yum install python-pip

2、

```shell
[ceph_deploy][ERROR ] RuntimeError: NoSectionError: No section: 'ceph'
```

解决：  yum remove ceph-release

3、

```shell
# 扩展添加mon时报错
[node2][DEBUG ] write cluster configuration to /etc/ceph/{cluster}.conf
[ceph_deploy.admin][ERROR ] RuntimeError: config file /etc/ceph/ceph.conf exists with different content; use --overwrite-conf to overwrite
[ceph_deploy][ERROR ] GenericError: Failed to configure 1 admin hosts
```

解决： 修改ceph.conf文件 添加集群所在网段,然后将conf文件推送所有主机

```shell
[root@node1 my-ceph]# cat ceph.conf 
[global]
fsid = f34701ec-789e-4406-9147-9ff7c543ac93
mon_initial_members = node1
mon_host = 192.168.20.102
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
public network = 192.168.20.0/24

[root@node1 my-ceph]# ceph-deploy --overwrite-conf config push node1 node2 node3
```

4、

```shell
[root@node1 my-ceph]# ceph -s
  cluster:
    id:     f34701ec-789e-4406-9147-9ff7c543ac93
    health: HEALTH_WARN
            application not enabled on 1 pool(s)
```

解决:指定相应的pool name

```shell
[root@node1 my-ceph]# ceph osd pool application enable pool_demo rbd
enabled application 'rbd' on pool 'pool_demo'
```

5、

```shell
[root@node1 my-ceph]# ceph osd pool delete pool_demo pool_demo --yes-i-really-really-mean-it
Error EPERM: pool deletion is disabled; you must first set the mon_allow_pool_delete config option to true before you can destroy a pool
```

解决：修改ceph.conf,[global]追加内容

```shell
[root@node1 my-ceph]# vim /etc/ceph/ceph.conf 
mon allow pool delete = true

[root@node1 my-ceph]# systemctl restart ceph-mon.target 
[root@node1 my-ceph]# ceph osd pool delete pool_demo pool_demo --yes-i-really-really-mean-it
pool 'pool_demo' removed
```

