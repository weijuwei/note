192.168.47.120  master k8s-master
192.168.47.121  node1  k8s-node1
192.168.47.122  node2  k8s-node2

配置ssh互信

关闭防火墙和selinux关闭Swap
swapoff -a && sysctl -w vm.swappiness=0


#### master节点
##### 1、安装ectd
```shell
[root@k8s-master ~]# yum install etcd -y

# 配置文件
[root@k8s-master ~]# vim /etc/etcd/etcd.conf
ETCD_DATA_DIR="/var/lib/etcd/"
ETCD_LISTEN_CLIENT_URLS="http://0.0.0.0:2379"
ETCD_NAME="k8s-master"
#[Clustering]
ETCD_ADVERTISE_CLIENT_URLS="http://192.168.47.120:2379"

# 配置开机启动并运行
[root@k8s-master ~]# systemctl enable etcd.service
[root@k8s-master ~]# systemctl start etcd

# 检查是否安装成功
[root@k8s-master ~]# etcdctl cluster-health
member 8e9e05c52164694d is healthy: got healthy result from http://192.168.47.120:2379
cluster is healthy
```
##### 2、相关组件安装
###### 2.1、拷贝相关二进制文件到/usr/bin目录
```shell
wget  https://dl.k8s.io/v1.13.4/kubernetes-server-linux-amd64.tar.gz
tar xf kubernetes-server-linux-amd64.tar.gz
[root@k8s-master bin]# cp kube-apiserver /usr/bin/
[root@k8s-master bin]# cp kube-controller-manager /usr/bin/
[root@k8s-master bin]# cp kube-scheduler /usr/bin/
[root@k8s-master bin]# cp kubectl /usr/bin/
```
###### 2.2、建立systemd文件和相应配置文件，并启动
*kube-apiserver*
```shell
[root@k8s-master ~]# vim /usr/lib/systemd/system/kube-apiserver.service
[Unit]
Description=Kubernetes API Server
After=etcd.service
Wants=etcd.service

[Service]
EnvironmentFile=/etc/kubernetes/apiserver
ExecStart=/usr/bin/kube-apiserver  \
        $KUBE_ETCD_SERVERS \
        $KUBE_API_ADDRESS \
        $KUBE_API_PORT \
        $KUBE_SERVICE_ADDRESSES \
        $KUBE_ADMISSION_CONTROL \
        $KUBE_API_LOG \
        $KUBE_API_ARGS 
Restart=on-failure
Type=notify
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target

# EnvironmentFile为kube-apiserver的配置文件
[root@k8s-master ~]# vim /etc/kubernetes/apiserver
KUBE_API_ADDRESS="--insecure-bind-address=0.0.0.0"
KUBE_API_PORT="--insecure-port=8080"
KUBE_ETCD_SERVERS="--etcd-servers=http://192.168.47.120:2379"
KUBE_SERVICE_ADDRESSES="--service-cluster-ip-range=192.168.0.0/16"
KUBE_ADMISSION_CONTROL="--admission-control=NamespaceLifecycle,LimitRanger,SecurityContextDeny,ServiceAccount,ResourceQuota"
KUBE_API_LOG="--logtostderr=false --log-dir=/var/log/kubernets/apiserver --v=2"
KUBE_API_ARGS=" "
```
*kube-controller-manager*
```shell
[root@k8s-master bin]# vim /usr/lib/systemd/system/kube-controller-manager.service
[Unit]
Description=Kubernetes Scheduler
After=kube-apiserver.service 
Requires=kube-apiserver.service

[Service]
EnvironmentFile=-/etc/kubernetes/controller-manager
ExecStart=/usr/bin/kube-controller-manager \
        $KUBE_MASTER \
        $KUBE_CONTROLLER_MANAGER_ARGS
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target

# 配置文件
[root@k8s-master ~]# vim /etc/kubernetes/controller-manager
KUBE_MASTER="--master=http://192.168.47.120:8080"
KUBE_CONTROLLER_MANAGER_ARGS=" "
```
*kube-scheduler*
```shell
[root@k8s-master ~]# vim /usr/lib/systemd/system/kube-scheduler.service
[Unit]
Description=Kubernetes Scheduler
After=kube-apiserver.service 
Requires=kube-apiserver.service

[Service]
User=root
EnvironmentFile=-/etc/kubernetes/scheduler
ExecStart=/usr/bin/kube-scheduler \
        $KUBE_MASTER \
        $KUBE_SCHEDULER_ARGS
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target

# 配置文件
[root@k8s-master ~]# vim /etc/kubernetes/scheduler
KUBE_MASTER="--master=http://192.168.47.120:8080"
KUBE_SCHEDULER_ARGS="--logtostderr=true --log-dir=/var/log/kubernetes/scheduler --v=2"
```
启动
```shell
systemctl daemon-reload 
systemctl enable kube-apiserver.service
systemctl start kube-apiserver.service
systemctl enable kube-controller-manager.service
systemctl start kube-controller-manager.service
systemctl enable kube-scheduler.service
systemctl start kube-scheduler.service
```
###### 2.3、检验是否正确
```shell
[root@k8s-master bin]# kubectl get cs
NAME                 STATUS    MESSAGE             ERROR
etcd-0               Healthy   {"health":"true"}
scheduler            Healthy   ok
controller-manager   Healthy   ok
```

#### node 节点

*Node节点上安装组件有*:
- docker
- kube-proxy
- kubelet


##### 1、安装docker-ce
```shell
[root@k8s-node1 ~]# yum install docker-ce -y
```
##### 2、相关组件安装
复制相关组件到/usr/bin下 kube-proxy kubelet

```shell
[root@k8s-master bin]# scp kubelet node1:/usr/bin
kubelet                                                         100%  108MB   5.3MB/s   00:20
[root@k8s-master bin]# scp kubelet node2:/usr/bin
kubelet                                                         100%  108MB  26.9MB/s   00:04
[root@k8s-master bin]# scp kube-proxy node1:/usr/bin/
kube-proxy                                                      100%   33MB  38.7MB/s   00:00
[root@k8s-master bin]# scp kube-proxy node2:/usr/bin/
kube-proxy
```
##### 3、相关组件systemd文件建立和启动
*kube-proxy*
```shell
[root@k8s-node1 ~]# vim /usr/lib/systemd/system/kube-proxy.service
[Unit]
Description=Kubernetes Kube-Proxy Server
Documentation=https://github.com/GoogleCloudPlatform/kubernetes
After=network.target

[Service]
EnvironmentFile=/etc/kubernetes/config
EnvironmentFile=/etc/kubernetes/proxy
ExecStart=/usr/bin/kube-proxy \
            $KUBE_LOGTOSTDERR \
            $KUBE_LOG_LEVEL \
            $KUBE_MASTER \
            $KUBE_PROXY_ARGS
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target


# 配置文件
# mkdir -p /etc/kubernetes
# vim /etc/kubernetes/proxy
KUBE_PROXY_ARGS=""
# vim /etc/kubernetes/config
KUBE_LOGTOSTDERR="--logtostderr=true"
KUBE_LOG_LEVEL="--v=0"
KUBE_ALLOW_PRIV="--allow_privileged=false"
KUBE_MASTER="--master=http://192.168.47.120:8080"

# 启动服务
# systemctl daemon-reload
# systemctl start kube-proxy
```
*kubelet*
```shell
# vim /usr/lib/systemd/system/kubelet.service
[Unit]
Description=Kubernetes Kubelet Server
Documentation=https://github.com/GoogleCloudPlatform/kubernetes
After=docker.service
Requires=docker.service
 
[Service]
WorkingDirectory=/var/lib/kubelet
EnvironmentFile=/etc/kubernetes/kubelet
ExecStart=/usr/bin/kubelet $KUBELET_ARGS
Restart=on-failure
KillMode=process
 
[Install]
WantedBy=multi-user.target

配置文件
# mkdir -p /var/lib/kubelet
# vim /etc/kubernetes/kubelet
KUBELET_ADDRESS="--address=0.0.0.0"
KUBELET_HOSTNAME="--hostname-override=192.168.47.121"
KUBELET_API_SERVER="--api-servers=http://192.168.47.120:8080" ###当前节点地址
KUBELET_POD_INFRA_CONTAINER="--pod-infra-container-image=reg.docker.tb/harbor/pod-infrastructure:latest"
KUBELET_ARGS="--enable-server=true --enable-debugging-handlers=true --fail-swap-on=false --kubeconfig=/var/lib/kubelet/kubeconfig"

# 向master注册
[root@k8s-node1 kubernetes]# vim /var/lib/kubelet/kubeconfig
apiVersion: v1
kind: Config
users:
- name: kubelet
clusters:
- name: kubernetes
  cluster:
    server: http://192.168.47.120:8080
contexts:
- context:
    cluster: kubernetes
    user: kubelet
  name: service-account-context
current-context: service-account-context

启动
# systemctl daemon-reload
# systemctl start kubelet.service
[root@k8s-node2 kubernetes]# ss -tlnp| grep kubelet
LISTEN     0      128    127.0.0.1:44323                    *:*                   users:(("kubelet",pid=5572,fd=9))
LISTEN     0      128    127.0.0.1:10248                    *:*                   users:(("kubelet",pid=5572,fd=22))
LISTEN     0      128         :::10250                   :::*                   users:(("kubelet",pid=5572,fd=23))
LISTEN     0      128         :::10255                   :::*                   users:(("kubelet",pid=5572,fd=21))
```

##### 4、验证
在master节点执行
```shell
[root@k8s-master bin]# kubectl get node
NAME        STATUS   ROLES    AGE   VERSION
k8s-node1   Ready    <none>   39s   v1.13.4
k8s-node2   Ready    <none>   13s   v1.13.4
```