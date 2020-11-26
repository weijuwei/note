FROM weijuwei/alpine:3.12.0
LABEL maintainer="weijuwei<583112952@qq.com>"
RUN mkdir /apps
# wget https://download.java.net/openjdk/jdk8u41/ri/openjdk-8u41-b04-linux-x64-14_jan_2020.tar.gz
ADD openjdk-8u41-b04-linux-x64-14_jan_2020.tar.gz /apps
# wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.29-r0/glibc-2.29-r0.apk
COPY glibc-2.29-r0.apk /apps/
# wget https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub
ADD sgerrand.rsa.pub /etc/apk/keys/sgerrand.rsa.pub
RUN ln -s /apps/java-se-8u41-ri /apps/jdk1.8 && cd /apps && apk add glibc-2.29-r0.apk && rm -f /apps/*.gz /apps/*.apk
ENV JAVA_HOME /apps/jdk1.8
ENV CLASSPATH $JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
ENV PATH $PATH:$JAVA_HOME/bin
