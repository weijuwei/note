> https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/7/html/high_availability_add-on_reference/index

#### 1、环境

- 操作系统：CentOS7.5
  - node1: 192.168.56.3
  - node2: 192.168.56.4
- 系统设置
  
  - 设置两个节点hosts
  
    ```shell
    [root@node1 ~]# cat /etc/hosts
    192.168.56.3 node1 node1.xl.com
    192.168.56.4 node2 node2.xl.com
    ```
  
  - 时间同步
  
  - 节点间ssh互信
  
  - selinux、firewall禁用
#### 2、安装相关包
两节点一样操作
##### 1、配置yum源
```shell
[root@node1 ~]# cat /etc/yum.repos.d/base.repo 
[base-aliyun]
name=aliyun base
baseurl=https://mirrors.aliyun.com/centos/7/os/x86_64/
gpgcheck=0

[updates]
name=aliyun updates
baseurl=https://mirrors.aliyun.com/centos/7/updates/x86_64/
gpgcheck=0

[extras]
name=aliyun extrax
baseurl=https://mirrors.aliyun.com/centos/7/extras/x86_64/
gpgcheck=0
```
##### 2、安装相关包
```shell
[root@node1 ~]# yum install pcs pacemaker fence-agents-all -y
```
#### 3、设置并启动相关服务
##### 1、设置hacluster用户密码
两节点都设置
```shell
# 123456
[root@node1 ~]# passwd hacluster 
Changing password for user hacluster.
New password: 
BAD PASSWORD: The password is shorter than 8 characters
Retype new password: 
passwd: all authentication tokens updated successfully.
```
##### 2、启动pcsd服务，配置节点间的认证
```shell
# 两节点都要启动服务
[root@node1 ~]# systemctl start pcsd
[root@node1 ~]# systemctl enable pcsd

# 配置节点间认证（其中一台设置即可）
[root@node1 ~]# pcs cluster auth node1 node2
Username: hacluster
Password: 
node1: Authorized
node2: Authorized
```
##### 3、创建集群并启动
**在其中一个节点操作即可**
```shell
# 新建一个名为mycluster的集群，并将node1 node2添加到里面
[root@node1 ~]# pcs cluster setup --name mycluster node1 node2
Destroying cluster on nodes: node1, node2...
node1: Stopping Cluster (pacemaker)...
node2: Stopping Cluster (pacemaker)...
node1: Successfully destroyed cluster
node2: Successfully destroyed cluster

Sending 'pacemaker_remote authkey' to 'node1', 'node2'
node1: successful distribution of the file 'pacemaker_remote authkey'
node2: successful distribution of the file 'pacemaker_remote authkey'
Sending cluster config files to the nodes...
node1: Succeeded
node2: Succeeded

Synchronizing pcsd certificates on nodes node1, node2...
node1: Success
node2: Success
Restarting pcsd on the nodes in order to reload the certificates...
node1: Success
node2: Success

# 启动集群并设置自启动
[root@node1 ~]# pcs cluster start --all
node1: Starting Cluster (corosync)...
node2: Starting Cluster (corosync)...
node1: Starting Cluster (pacemaker)...
node2: Starting Cluster (pacemaker)...
[root@node1 ~]# pcs cluster enable --all

# 禁用stonith和忽略仲裁
[root@node1 ~]# pcs property set stonith-enabled=false
# 否则会报错：WARNING: no stonith devices and stonith-enabled is not false

[root@node1 ~]# pcs property set no-quorum-policy=ignore
```
#### 4、集群资源管理
##### 资源类型

- ocf:  ocf格式的启动脚本在/usr/lib/ocf/resource.d/
- lsb:  lsb的脚本一般在/etc/rc.d/init.d/

查看相关资源配置的参数

```shell
# 查看相关资源配置的参数
[root@node1 ~]# pcs resource describe -h

Usage: pcs resource describe...
    describe [<standard>:[<provider>:]]<type> [--full]
        Show options for the specified resource. If --full is specified, all
        options including advanced ones are shown.
```

##### 1、添加资源

添加一个VirtualIP资源  ocf类型的   （类似keepalived的ip）

```shell
[root@node1 ~]# pcs resource create VirtualIP ocf:heartbeat:IPaddr2 ip=192.168.56.200 cidr_netmask=32 nic=enp0s3 op monitor interval=30s
```
查看资源状况

```shell
[root@node1 ~]# pcs resource 
 VirtualIP	(ocf::heartbeat:IPaddr2):	Started node1
```

##### 2、查看状态

**查看状态,ip在node1上生效**

```shell
[root@node1 ~]# pcs status
Cluster name: mycluster
Stack: corosync
Current DC: node2 (version 1.1.19-8.el7_6.4-c3c624ea3d) - partition with quorum
Last updated: Fri Jul 26 15:49:17 2019
Last change: Fri Jul 26 15:48:15 2019 by root via cibadmin on node1

2 nodes configured
1 resource configured

Online: [ node1 node2 ]

Full list of resources:

 VirtualIP	(ocf::heartbeat:IPaddr2):	Started node1

Daemon Status:
  corosync: active/disabled
  pacemaker: active/disabled
  pcsd: active/disabled
```
**在node1上查看ip**
```shell
[root@node1 ~]# ip a
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 08:00:27:c4:56:a3 brd ff:ff:ff:ff:ff:ff
    inet 192.168.56.3/24 brd 192.168.56.255 scope global noprefixroute enp0s3
       valid_lft forever preferred_lft forever
    inet 192.168.56.200/32 brd 192.168.56.255 scope global enp0s3
       valid_lft forever preferred_lft forever
    inet6 fe80::c97:3269:2649:c9f3/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
```
**在node1上模拟节点故障查看IP是否会漂移**
```shell
# 模拟node1故障
[root@node1 ~]# pcs node standby node1

# 查看集群状态，node1处于standby状态，ip资源在node2上生效
[root@node1 ~]# pcs status
Cluster name: mycluster
Stack: corosync
Current DC: node2 (version 1.1.19-8.el7_6.4-c3c624ea3d) - partition with quorum
Last updated: Fri Jul 26 15:53:28 2019
Last change: Fri Jul 26 15:53:22 2019 by root via cibadmin on node1

2 nodes configured
1 resource configured

Node node1: standby
Online: [ node2 ]

Full list of resources:

 VirtualIP	(ocf::heartbeat:IPaddr2):	Started node2

Daemon Status:
  corosync: active/disabled
  pacemaker: active/disabled
  pcsd: active/disabled

# node2上查看IP
[root@node2 ~]# ip a
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 08:00:27:2e:4e:8c brd ff:ff:ff:ff:ff:ff
    inet 192.168.56.4/24 brd 192.168.56.255 scope global noprefixroute enp0s3
       valid_lft forever preferred_lft forever
    inet 192.168.56.200/32 brd 192.168.56.255 scope global enp0s3
       valid_lft forever preferred_lft forever
    inet6 fe80::667c:84e6:3555:33a5/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
    inet6 fe80::c97:3269:2649:c9f3/64 scope link tentative noprefixroute dadfailed 
       valid_lft forever preferred_lft forever
```
##### 3、定义资源节点优先级
**node1恢复后，查看资源仍在node2上生效**
```shell
[root@node1 ~]# pcs status nodes
Pacemaker Nodes:
 Online: node1 node2
 Standby:
 Maintenance:
 Offline:
Pacemaker Remote Nodes:
 Online:
 Standby:
 Maintenance:
 Offline:
[root@node1 ~]# pcs status resources 
 VirtualIP	(ocf::heartbeat:IPaddr2):	Started node2
```
**定义资源选择节点的优先级**

```shell
# 配置资源VirtualIP的节点倾向性，优先选择node1，如果节点online的情况下
[root@node1 ~]# pcs constraint location VirtualIP prefers node1

# 查看资源的分布情况
[root@node1 ~]# pcs status resources 
 VirtualIP	(ocf::heartbeat:IPaddr2):	Started node1
```

##### 4、多资源“捆绑”

**将多资源进行“捆绑”，使其始终保持在同一个节点生效。**

**1、添加一个nginx的资源**

```shell
[root@node1 ~]# pcs resource create Nginx ocf:heartbeat:nginx op monitor interval=3s timeout=30s op start interval=0 timeout=60s op stop interval=0 timeout=60s
```

**2、查看资源状态，两资源分别在不同的节点**

```shell
# 查看那资源状态，nginx在node2上启动生效
[root@node1 ~]# pcs status resources 
 VirtualIP	(ocf::heartbeat:IPaddr2):	Started node1
 Nginx	(ocf::heartbeat:nginx):	Started node2
```

**3、进行资源捆绑**

###### 方式一：创建资源组

将VirtualIP和Nginx两资源添加到一个组中

```shell
# 将两资源添加的myweb组中
[root@node1 ~]# pcs resource group add myweb VirtualIP
[root@node1 ~]# pcs resource group add myweb Nginx

# 再次查看资源分布情况
[root@node1 ~]# pcs status resources 
 Resource Group: myweb
     VirtualIP	(ocf::heartbeat:IPaddr2):	Started node1
     Nginx	(ocf::heartbeat:nginx):	Started node1
```

###### 方式二：定义资源约束constraint

删除之前的资源组，查看状态，两资源分布在不同节点

```shell
[root@node1 ~]# pcs resource group remove myweb

[root@node1 ~]# pcs status resources 
 VirtualIP	(ocf::heartbeat:IPaddr2):	Started node1
 Nginx	(ocf::heartbeat:nginx):	Started node2
```

**定义资源间constraint，并设置资源的启动顺序**

```shell
[root@node1 ~]# pcs constraint colocation add VirtualIP Nginx INFINITY

# 定义资源的启动顺序
[root@node1 ~]# pcs constraint order start VirtualIP then start Nginx
Adding VirtualIP Nginx (kind: Mandatory) (Options: first-action=start then-action=start)

[root@node1 ~]# pcs status resources 
 VirtualIP	(ocf::heartbeat:IPaddr2):	Started node1
 Nginx	(ocf::heartbeat:nginx):	Started node1
```

**查看整个约束信息**

```shell
[root@node1 ~]# pcs constraint 
Location Constraints:
  Resource: VirtualIP
    Enabled on: node1 (score:INFINITY)
Ordering Constraints:
  start VirtualIP then start Nginx (kind:Mandatory)
Colocation Constraints:
  VirtualIP with Nginx (score:INFINITY)
```