#### 通过proxysql的cli配置mysql读写分离

前提是主从已经配置完成，此实验紧接着mha-mysql实验（mha-mysql.md）

- 192.168.56.3 master
- 192.168.56.4 slave （mha中的备用主）
- 192.168.56.100 slave

```shell
# 安装生成的文件
[root@lab ~]# rpm -ql proxysql
/etc/init.d/proxysql
/etc/logrotate.d/proxysql
/etc/proxysql.cnf
/usr/bin/proxysql
/usr/share/proxysql/tools/proxysql_galera_checker.sh
/usr/share/proxysql/tools/proxysql_galera_writer.pl

# 启动服务
service proxysql start

# 查看端口 6032管理端口 6033与后端相关
ss -tln
LISTEN      0      128                                   *:6032                           
LISTEN      0      128                                   *:80                             
LISTEN      0      128                                   *:6033                           
LISTEN      0      128                                   *:6033                            

# 进入proxysql管理端
mysql -u admin -padmin -h 127.0.0.1 -P6032
Server version: 5.5.30 (ProxySQL Admin Module)
MySQL [(none)]> show databases;
+-----+---------------+-------------------------------------+
| seq | name          | file                                |
+-----+---------------+-------------------------------------+
| 0   | main          |                                     |
| 2   | disk          | /var/lib/proxysql/proxysql.db       |
| 3   | stats         |                                     |
| 4   | monitor       |                                     |
| 5   | stats_history | /var/lib/proxysql/proxysql_stats.db |
+-----+---------------+-------------------------------------+
# main 内存配置数据库，表里存放后端db实例、用户验证、路由规则等信息。表名以runtime_开头的表示proxysql当前运行的配置内容，不能通过dml语句修改，只能修改对应的不以 runtime_开头的（在内存）里的表，然后LOAD 使其生效， SAVE 使其存到硬盘以供下次重启加载。
# disk 是持久化到硬盘的配置，sqlite数据文件。
# stats 是proxysql运行抓取的统计信息，包括到后端各命令的执行次数、流量、processlist、查询种类汇总/执行时间等等。
# monitor 库存储 monitor模块收集的信息，主要是对后端db的健康/延迟检查。

# 查看main中表
MySQL [(none)]> show tables from main;
+--------------------------------------------+
| tables                                     |
+--------------------------------------------+
| global_variables                           |
| mysql_collations                           |
| mysql_galera_hostgroups                    |
| mysql_group_replication_hostgroups         |
| mysql_query_rules                          |
| mysql_query_rules_fast_routing             |
| mysql_replication_hostgroups               |
| mysql_servers                              |
| mysql_users                                |
| proxysql_servers                           |
| runtime_checksums_values                   |
| runtime_global_variables                   |
| runtime_mysql_galera_hostgroups            |
| runtime_mysql_group_replication_hostgroups |
| runtime_mysql_query_rules                  |
| runtime_mysql_query_rules_fast_routing     |
| runtime_mysql_replication_hostgroups       |
| runtime_mysql_servers                      |
| runtime_mysql_users                        |
| runtime_proxysql_servers                   |
| runtime_scheduler                          |
| scheduler                                  |
+--------------------------------------------+

# 添加后端mysql主机 指定hostgroup_id 主节点是100 从节点是1000
insert into mysql_servers(hostgroup_id,hostname,port,weight,max_connections,max_replication_lag,comment) values(100,'192.168.56.3',3306,1,1000,10,'test my proxysql');

insert into mysql_servers(hostgroup_id,hostname,port,weight,max_connections,max_replication_lag,comment) values(1000,'192.168.56.4',3306,1,1000,10,'test my proxysql');

insert into mysql_servers(hostgroup_id,hostname,port,weight,max_connections,max_replication_lag,comment) values(1000,'192.168.56.100',3306,1,1000,10,'test my proxysql');

# 查询后端主机
select * from mysql_servers;
MySQL [(none)]> select hostgroup_id,hostname,status,weight from mysql_servers;
+--------------+----------------+--------+--------+
| hostgroup_id | hostname       | status | weight |
+--------------+----------------+--------+--------+
| 100          | 192.168.56.3   | ONLINE | 1      |
| 1000         | 192.168.56.4   | ONLINE | 1      |
| 1000         | 192.168.56.100 | ONLINE | 1      |
+--------------+----------------+--------+--------+

# 添加可以访问后端主机的账号
insert into mysql_users(username,password,active,default_hostgroup,transaction_persistent) values('proxysql','proxysql',1,100,1);

# 设置健康监测账号密码
set mysql-monitor_username='proxysql';
set mysql-monitor_password='proxysql';

# 修改的数据加载至RUNTIME中 save保存到本地持久化操作
load mysql servers to runtime;
load mysql users to runtime;
load mysql variables to runtime;

save mysql servers to disk;
save mysql users to disk;
save mysql variables to disk;

# 查看各类SQL的执行情况
select * from stats_mysql_query_digest;

# 添加读写分离的路由规则
INSERT INTO mysql_query_rules(active,match_pattern,destination_hostgroup,apply) VALUES(1,'^SELECT.*FOR UPDATE$',100,1);
INSERT INTO mysql_query_rules(active,match_pattern,destination_hostgroup,apply) VALUES(1,'^SELECT',1000,1);

load mysql query rules to runtime;
save mysql query rules to disk;

# 查询规则
select rule_id,active,match_pattern,destination_hostgroup,apply from runtime_mysql_query_rules;
+---------+--------+----------------------+-----------------------+-------+
| rule_id | active | match_pattern        | destination_hostgroup | apply |
+---------+--------+----------------------+-----------------------+-------+
| 1       | 1      | ^SELECT.*FOR UPDATE$ | 100                   | 1     |
| 2       | 1      | ^SELECT              | 1000                  | 1     |
+---------+--------+----------------------+-----------------------+-------+

# 查看统计信息 观察读操作调度到HG1000 写操作调度到HG100
MySQL [(none)]> select hostgroup,schemaname,username,substr(digest_text,120,-120) from stats_mysql_query_digest;
+-----------+--------------------+----------+--------------------------------+
| hostgroup | schemaname         | username | substr(digest_text,120,-120)   |
+-----------+--------------------+----------+--------------------------------+
| 1000      | information_schema | proxysql | select * from hellodb.students |
| 1000      | information_schema | proxysql | SELECT DATABASE()              |
| 100       | information_schema | proxysql | drop database proxysql         |
+-----------+--------------------+----------+--------------------------------+
```

