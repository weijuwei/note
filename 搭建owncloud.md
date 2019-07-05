环境
centOS 7.5
nginx 1.12.2
php 7.2
owncloud 10.2.0

1、安装nginx
```shell
[root@lab ~]# yum install nginx -y
[root@lab ~]# systemctl start nginx
[root@lab ~]# systemctl enable nginx
```

2、安装php
```shell
[root@lab ~]# yum install epel-release
[root@lab ~]# rpm -Uvh https://mirror.webtatic.com/yum/el7/webtatic-release.rpm

[root@lab ~]# yum install -y php72w-common php72w-fpm php72w-opcache php72w-gd php72w-mysqlnd php72w-mbstring php72w-pecl-redis php72w-pecl-memcached php72w-devel php72w-intl

# 隐藏php版本号
[root@lab ~]# vim /etc/php.ini
expose_php = Off

# 修改php-fpm的启动用户和用户组
user = nginx
group = nginx


[root@lab ~]# systemctl start php-fpm
[root@lab ~]# systemctl enable php-fpm
```

3、安装owncloud 10.2.0
> https://owncloud.org/download/older-versions/

```shell
[root@lab ~]# wget http://download.owncloud.org/download/repositories/10.2.0/CentOS_7/noarch/owncloud-files-10.2.0-1.1.noarch.rpm

[root@lab ~]# rpm --import https://download.owncloud.org/download/repositories/10.2.0/CentOS_7/repodata/repomd.xml.key

[root@lab ~]# rpm -ivh owncloud-files-10.2.0-1.1.noarch.rpm
# 安装的路径为/var/www/html/owncloud
```

4、配置nginx

```shell
[root@lab ~]# cat /etc/nginx/conf.d/owncloud.conf
# hide nginx version 
server_tokens  off;
upstream php-handler { 
	server 127.0.0.1:9000; 
    #server unix:/var/run/php5-fpm.sock;
} 
server { 
    listen 8888; 
	#server_name www.upload.com;
	server_name 192.168.1.201;
    # Path to the root of your installation 
    root /htdocs; 
    index index.php;

	# set max upload size 
    client_max_body_size 10G; 
    fastcgi_buffers 64 4K; 
    
	# Disable gzip to avoid the removal of the ETag header 
    gzip off; 
    
	# Uncomment if your server is build with the ngx_pagespeed module
    # This module is currently not supported. 
    # pagespeed off; 
    rewrite ^/caldav(.*)$ /remote.php/caldav$1 redirect; 
    rewrite ^/carddav(.*)$ /remote.php/carddav$1 redirect; 
    rewrite ^/webdav(.*)$ /remote.php/webdav$1 redirect; 

    error_page 403 /core/templates/403.php; 
    error_page 404 /core/templates/404.php; 

    location = /robots.txt {
		allow all; 
		log_not_found off; 
		access_log off; 
    } 

    location ~ ^/(?:\.htaccess|data|config|db_structure\.xml|README){ 
		deny all; 
    } 

    location / { 
      # The following 2 rules are only needed with webfinger 
      rewrite ^/.well-known/host-meta /public.php?service=host-meta last;
      rewrite ^/.well-known/host-meta.json /public.php?service=host-meta-json last; 
      rewrite ^/.well-known/carddav /remote.php/carddav/ redirect; 
      rewrite ^/.well-known/caldav /remote.php/caldav/ redirect; 
      rewrite ^(/core/doc/[^\/]+/)$ $1/index.html; 
      try_files $uri $uri/ /index.php; 
    } 

    location ~ \.php(?:$|/) { 
		fastcgi_split_path_info ^(.+\.php)(/.+)$; 
		include fastcgi_params; 
		fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
		fastcgi_param PATH_INFO $fastcgi_path_info; 
		fastcgi_pass php-handler;
	} 
    # Optional: set long EXPIRES header on static assets 
    location ~* \.(?:jpg|jpeg|gif|bmp|ico|png|css|js|swf)$ { 
		expires 30d; 
		# Optional: Don't log access to assets 
		access_log off; 
	}
}
```
