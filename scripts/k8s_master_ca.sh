#!/bin/bash

if [ $# -eq 0 ];
then
    echo "usage: $0 [host|ip] "
    exit
fi

for HOST in $*
do
	#ssh $HOST "mkdir /tmp/testest"

	ssh $HOST "mkdir -p /etc/kubernetes/pki/etcd/"
	scp /etc/kubernetes/pki/{ca.*,sa.*,front-proxy-ca.*} $HOST:/etc/kubernetes/pki/
	scp /etc/kubernetes/admin.conf $HOST:/etc/kubernetes/
	scp /etc/kubernetes/pki/etcd/ca.* $HOST:/etc/kubernetes/pki/etcd/

	echo "$HOST transport OK......"
	echo "---------------------"
done
