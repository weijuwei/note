FROM centos:latest
MAINTAINER "weijuwei<583112952@qq.com>"
ARG VER=1.18.0
RUN mkdir /apps && yum install -y gcc make net-tools vim iproute  openssl-devel zlib-devel pcre-devel
ADD nginx-$VER.tar.gz /apps
RUN cd /apps/nginx-$VER && ./configure --prefix=/apps/nginx --with-openssl=/usr/lib64/openssl && make && make install
WORKDIR /apps/nginx
RUN echo "my nginx docker image" > /apps/nginx/html/index.html
RUN rm -rf /apps/nginx-$VER /apps/nginx-$VER.tar.gz  && ln -s /apps/nginx/sbin/nginx /usr/sbin/ &&  yum clean all
EXPOSE 80
ENTRYPOINT ["nginx","-g","daemon off;"]
