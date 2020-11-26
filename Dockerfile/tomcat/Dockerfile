FROM weijuwei/centos:7.5
LABEL maintainer="weijuwei<583112952@qq.com>"
RUN mkdir /apps
# wget https://downloads.apache.org/tomcat/tomcat-9/v9.0.36/bin/apache-tomcat-9.0.36.tar.gz
ADD apache-tomcat-9.0.36.tar.gz /apps
# wget https://download.java.net/openjdk/jdk8u41/ri/openjdk-8u41-b04-linux-x64-14_jan_2020.tar.gz
ADD openjdk-8u41-b04-linux-x64-14_jan_2020.tar.gz /apps
RUN ln -s /apps/apache-tomcat-9.0.36 /apps/tomcat && ln -s /apps/java-se-8u41-ri /apps/jdk1.8 && rm -f /apps/*.gz
RUN mkdir /apps/tomcat/webapps_bak && cp -R /apps/tomcat/webapps/* /apps/tomcat/webapps_bak
ENV CATALINA_HOME /apps/tomcat
ENV CATALINA_BASE /apps/tomcat
ENV JAVA_HOME /apps/jdk1.8
ENV CLASSPATH $JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
ENV PATH $PATH:$CATALINA_HOME/bin:$CATALINA_HOME/lib:$JAVA_HOME/bin
EXPOSE 8080
#catalina.sh
#ENTRYPOINT /apps/tomcat/bin/startup.sh && tail -F /apps/tomcat/logs/catalina.out
CMD /apps/tomcat/bin/startup.sh && tail -F /apps/tomcat/logs/catalina.out
