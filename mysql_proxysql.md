#### 通过proxysql的cli配置mysql读写分离

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

# 添加后端mysql主机 指定hostgroup_id 主节点是100 从节点是1000
insert into mysql_servers(hostgroup_id,hostname,port,weight,max_connections,max_replication_lag,comment) values(100,'192.168.56.3',3306,1,1000,10,'test my proxysql');

insert into mysql_servers(hostgroup_id,hostname,port,weight,max_connections,max_replication_lag,comment) values(1000,'192.168.56.4',3306,1,1000,10,'test my proxysql');

insert into mysql_servers(hostgroup_id,hostname,port,weight,max_connections,max_replication_lag,comment) values(1000,'192.168.56.100',3306,1,1000,10,'test my proxysql');

select * from mysql_servers;

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
```

