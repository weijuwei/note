FROM busybox:latest
ENV SPATH /data/html/
RUN /bin/mkdir $SPATH -pv
WORKDIR $SPATH
COPY index.html .
WORKDIR /
EXPOSE 80/tcp
HEALTHCHECK --start-period=3s CMD wget -O - -q http://localhost
CMD ["/bin/httpd","-f","-h","/data/html"]
