#### 简介
  通过xtrabackup备份（增量备份实验），做主从同步复制实验
#### 环境
- 系统 CentOS 7.5
- node1 192.168.56.3 主
- node2 192.168.56.4 从

#### 一、数据备份还原阶段
##### 增量备份还原
###### 1、备份 主库 node1
```shell
# 全备份
# xtrabackup --defaults-file=/etc/my.cnf \
             --user=root \ 
             --password=123456 \
             --backup \
             --target-dir=/data/mysql/base/full
生成 /data/mysql/base/full

# 修改数据库1

# 第一次增量备份
# xtrabackup --defaults-file=/etc/my.cnf \
             --user=root --password=123456 \
             --backup \
             --target-dir=/data/mysql/inc/inc1 \
             --incremental-basedir=/data/mysql/base/full
# 生成 /data/mysql/inc/inc1

# 修改数据库2

# 第二次增量备份 在inc1的基础上
# xtrabackup --defaults-file=/etc/my.cnf \
             --user=root \
             --password=123456 \
             --backup \
             --target-dir=/data/mysql/inc/inc2 \
             --incremental-basedir=/data/mysql/inc/inc1
# 生成 /data/mysql/inc/inc2
```
###### 2、还原准备
```shell
# 还原准备阶段
# xtrabackup --prepare --apply-log-only \
             --target-dir=/data/mysql/base/full
# xtrabackup --prepare --apply-log-only \
             --target-dir=/data/mysql/base/full \
             --incremental-dir=/data/mysql/inc/inc1
# xtrabackup --prepare --apply-log-only \
             --target-dir=/data/mysql/base/full \
             --incremental-dir=/data/mysql/inc/inc2
```
###### 3、打包数据,并复制到从节点
```shell
# tar cvf xtrabackup_base.tar /data/mysql/base/full
# scp xtrabackup_base.tar node2:/data/mysql/
```
###### 4、还原数据 从库node2
**notice ： 数据库服务保证关闭，/var/lib/mysql目录为空**
```shell
# 还原数据
# tar xf xtrabackup_base.tar
# xtrabackup --user=root --password=123456 --copy-back --target-dir=/data/mysql/full

# 修改权限
# chown -R mysql.mysql /var/lib/mysql/

# 启动服务
# systemctl start mariadb

# 记录日志点，后面做主从使用
# cat xtrabackup_binlog_pos_innodb 
./mysql-bin.000002	761
```
#### 二、主从同步复制阶段
##### 1、主从库配置文件
```shell
# 主库配置文件
# cat /etc/my.cnf
[mysqld]
datadir=/var/lib/mysql
socket=/var/lib/mysql/mysql.sock
innodb_file_per_table=on
skip_name_resolve=on
log-bin=mysql-bin
binlog_format=mixed
server-id       = 1

# 从库配置文件
# cat /etc/my.cnf
[mysqld]
datadir=/var/lib/mysql
socket=/var/lib/mysql/mysql.sock
symbolic-links=0
innodb_file_per_table=on
skip_name_resolve=on
log-bin=mysql-bin
binlog_format=mixed
server-id       = 2
```
##### 2、主库创建slave同步user  node1
```shell
mysql> grant replication slave,reload,super on *.* to repluser@192.168.56.* identified by 'centos';
mysql> FLUSH PRIVILEGES;
```
##### 3、从库启动slave
```shell
# 日志记录位置
# cat xtrabackup_binlog_pos_innodb 
./mysql-bin.000002	761

# 执行slave
mysql> change master to master_host='192.168.56.3',\
                        master_user='repluser',\
                        master_password='centos',\
                        master_log_file='mysql-bin.000002',\
                        master_log_pos=761;
mysql> start slave;

# 查看
mysql> show slave status\G
*************************** 1. row ***************************
               Slave_IO_State: Waiting for master to send event
                  Master_Host: 192.168.56.3
                  Master_User: repluser
                  Master_Port: 3306
                Connect_Retry: 60
              Master_Log_File: mysql-bin.000002
          Read_Master_Log_Pos: 761
               Relay_Log_File: mariadb-relay-bin.000002
                Relay_Log_Pos: 529
        Relay_Master_Log_File: mysql-bin.000002
             Slave_IO_Running: Yes
            Slave_SQL_Running: Yes
```
#### 三、半同步复制

```shell
# ON MASTER
mysql> INSTALL SONAME 'semisync_master';
msyql> SET GLOBAL rpl_semi_sync_master_enabled=1;

# ON SLAVE
mysql> INSTALL SONAME 'semisync_slave';
mysql> SET GLOBAL rpl_semi_sync_slave_enabled=1; 

mysql> STOP SLAVE IO_THREAD;
mysql> START SLAVE IO_THREAD;

# 卸载
# ON MASTER
mysql> UNINSTALL SONAME 'semisync_master';
# ON SLAVE
mysql> UNINSTALL SONAME 'semisync_slave';
# 重启slave IO_THREAD线程

```
