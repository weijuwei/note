FROM weijuwei/alpine-base:3.12.0
MAINTAINER "weijuwei<583112952@qq.com>"
ARG VER=1.19.3.1
#RUN mkdir /apps && yum install -y gcc make net-tools vim iproute  openssl-devel zlib-devel pcre-devel
RUN mkdir /apps && apk add perl-dev perl
ADD openresty-$VER.tar.gz /apps
RUN cd /apps/openresty-$VER && ./configure --prefix=/apps/openresty --with-luajit  && make && make install
WORKDIR /apps/openresty
RUN echo "my openresty docker image" > /apps/openresty/nginx/html/index.html
RUN rm -rf /apps/openresty-$VER /apps/openresty-$VER.tar.gz  && ln -s /apps/openresty/nginx/sbin/nginx /usr/sbin/
EXPOSE 80
ENTRYPOINT ["nginx","-g","daemon off;"]
