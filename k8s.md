k8s安装部署
centos7.5
master 192.168.47.141
node1  192.168.47.142
node2  192.168.47.143

docker-ce 18.09.3
kubectl-1.13.4-0.x86_64
kubeadm-1.13.4-0.x86_64
kubectl-1.13.4-0.x86_64

#### 一、准备

ssh互信
ntpd时间同步
hosts域名解析
关闭firewall和selinux
禁用swap  临时禁用命令swapoff -a  永久禁用在fstab文件中编辑

配置yum仓库

```shell
aliyun的kubernetes库和docker-ce库
cat base.repo
[base-aliyun]
name=aliyun base
baseurl=https://mirrors.aliyun.com/centos/7/os/x86_64/
gpgcheck=0
[updates]
name=aliyun updates
baseurl=https://mirrors.aliyun.com/centos/7/updates/x86_64/
gpgcheck=0
[extras]
name=aliyun extrax
baseurl=https://mirrors.aliyun.com/centos/7/extras/x86_64/
gpgcheck=0

cat epel.repo
[epel]
name=epel-aliyun
baseurl=https://mirrors.aliyun.com/epel/7/x86_64/
gpgcheck=0
enabled=1

cat docker-ce.repo
[docker-ce]
name=docker-ce
baseurl=https://mirrors.aliyun.com/docker-ce/linux/centos/7/x86_64/stable/
gpgcheck=0
enabled=1

cat kubernetes.repo
[k8s]
name=k8s
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64/
gpgcheck=0
enabled=1
```

#### 二、三节点安装相关程序包

```shell
yum install docker-ce -y
yum install kubelet kubeadm kubectl -y
```

三、在各节点启动docker服务
若要通过默认的k8s.gcr.io镜象获取kubernetes系统组件的相关镜象，需要配置docker.service的Unit file中的Environment变量，为其定义合适的HTTPS_PROXY,格式如下

```shell
	Environment="HTTPS_PROXY=http://www.ik8s.io:10070"
	Environment="NO_PROXY=192.168.0.0/16,127.0.0.0/8"
	ExecStartPost=/usr/sbin/iptables -P FORWARD ACCEPT
```

重载完成后启动docker服务

```shell
systemctl daemon-reload
systemctl start docker
systemctl enable docker
   	
[root@k8s-master ~]# sysctl -a | grep bridge
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1

vim /etc/sysctl.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1

# sysctl -p
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
```

#### 四、初始化主节点master

systemctl enable kubelet
systemctl start kubelet

##### 1、主节点镜像拉取

若未禁用Swap设备，则需要编辑kubelet的配置文件，设置其忽略swap启用的状态错误，内容如下：

```shell
[root@k8s-master ~]# vim /etc/sysconfig/kubelet
KUBELET_EXTRA_ARGS="--fail-swap-on=false"
```

可选步骤：在运行初始化命令之前先运行如下命令单独获取相关镜象文件，而后再运行后面的kubeadm init命令，以便于观察到镜象文件的下载过程
```shell
kubeadm config images pull
```

然后即可进行master节点的初始化操作。

主节点镜像

```shell
[root@k8s-master ~]# kubeadm config images list
k8s.gcr.io/kube-apiserver:v1.13.4
k8s.gcr.io/kube-controller-manager:v1.13.4
k8s.gcr.io/kube-scheduler:v1.13.4
k8s.gcr.io/kube-proxy:v1.13.4
k8s.gcr.io/pause:3.1
k8s.gcr.io/etcd:3.2.24
k8s.gcr.io/coredns:1.2.6
[root@k8s-master ~]# kubeadm config images pull
[config/images] Pulled k8s.gcr.io/kube-apiserver:v1.13.4
[config/images] Pulled k8s.gcr.io/kube-controller-manager:v1.13.4
[config/images] Pulled k8s.gcr.io/kube-scheduler:v1.13.4
[config/images] Pulled k8s.gcr.io/kube-proxy:v1.13.4
[config/images] Pulled k8s.gcr.io/pause:3.1
[config/images] Pulled k8s.gcr.io/etcd:3.2.24
[config/images] Pulled k8s.gcr.io/coredns:1.2.6
[root@k8s-master ~]# docker image ls
REPOSITORY                           TAG                 IMAGE ID            CREATED             SIZE
k8s.gcr.io/kube-proxy                v1.13.4             fadcc5d2b066        8 days ago          80.3MB
k8s.gcr.io/kube-controller-manager   v1.13.4             40a817357014        8 days ago          146MB
k8s.gcr.io/kube-scheduler            v1.13.4             dd862b749309        8 days ago          79.6MB
k8s.gcr.io/kube-apiserver            v1.13.4             fc3801f0fc54        8 days ago          181MB
quay.io/coreos/flannel               v0.11.0-amd64       ff281650a721        5 weeks ago         52.6MB
k8s.gcr.io/coredns                   1.2.6               f59dcacceff4        4 months ago        40MB
k8s.gcr.io/etcd                      3.2.24              3cab8e1b9802        5 months ago        220MB
k8s.gcr.io/pause                     3.1                 da86e6ba6ca1        14 months ago       742kB
```

**kubeadm init命令支持两种初始化方式**： 

1. 通过命令行选项传递关键的部署设定
2. 基于yaml格式的专用配置文件，允许用户自定义各个部署参数

##### 2、主节点初始化

[root@k8s-master ~]# kubeadm init --kubernetes-version="v1.13.4" --pod-network-cidr="10.244.0.0/16"	
Your Kubernetes master has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

You can now join any number of machines by running the following on each node
as root:

  kubeadm join 192.168.47.141:6443 --token 438iqn.hop1pmcwxqfquy23 --discovery-token-ca-cert-hash sha256:a5e085b08c38e1be284ef74c9f734a0af299d36fd5ab65d8e8e43714b55a629b

[root@k8s-master ~]# mkdir .kube
[root@k8s-master ~]# cp /etc/kubernetes/admin.conf .kube/config

查看节点kubectl get node
[root@k8s-master ~]# kubectl get node
NAME         STATUS     ROLES    AGE   VERSION
k8s-master   NotReady   master   26m   v1.13.4

##### 3、安装部署pod网络   flannel

```shell
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
[root@k8s-master ~]# kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
podsecuritypolicy.extensions/psp.flannel.unprivileged created
clusterrole.rbac.authorization.k8s.io/flannel created
clusterrolebinding.rbac.authorization.k8s.io/flannel created
serviceaccount/flannel created
configmap/kube-flannel-cfg created
daemonset.extensions/kube-flannel-ds-amd64 created
daemonset.extensions/kube-flannel-ds-arm64 created
daemonset.extensions/kube-flannel-ds-arm created
daemonset.extensions/kube-flannel-ds-ppc64le created
daemonset.extensions/kube-flannel-ds-s390x created
```

查看节点kubectl get node

```shell
[root@k8s-master ~]# kubectl get node
NAME         STATUS   ROLES    AGE     VERSION
k8s-master   Ready    master   3m53s   v1.13.4
```

查看pods状态

```shell
[root@k8s-master ~]# kubectl get pods -n kube-system
NAME                                 READY   STATUS    RESTARTS   AGE
coredns-86c58d9df4-gmf9n             1/1     Running   0          34m
coredns-86c58d9df4-h9qbx             1/1     Running   0          34m
etcd-k8s-master                      1/1     Running   0          34m
kube-apiserver-k8s-master            1/1     Running   0          34m
kube-controller-manager-k8s-master   1/1     Running   0          34m
kube-flannel-ds-amd64-4qgps          1/1     Running   0          4m32s
kube-proxy-gh2cb                     1/1     Running   0          34m
kube-scheduler-k8s-master            1/1     Running   0          34m

[root@k8s-master ~]# kubectl get nodes
NAME         STATUS   ROLES    AGE   VERSION
k8s-master   Ready    master   36m   v1.13.4
```

**添加节点：**
*在各node节点运行*

```shell
# kubeadm join 192.168.47.141:6443 --token 438iqn.hop1pmcwxqfquy23 --discovery-token-ca-cert-hash sha256:a5e085b08c38e1be284ef74c9f734a0af299d36fd5ab65d8e8e43714b55a629b

没有禁用swap时  kubeadm join 192.168.47.141:6443 --token 438iqn.hop1pmcwxqfquy23 --discovery-token-ca-cert-hash sha256:a5e085b08c38e1be284ef74c9f734a0af299d36fd5ab65d8e8e43714b55a629b --ignore-preflight-errors=swap

输出部分信息如下：
 This node has joined the cluster:

Certificate signing request was sent to apiserver and a response was received.
The Kubelet was informed of the new secure connection details.
Run 'kubectl get nodes' on the master to see this node join the cluster. 
```

node节点docker镜像
```shell
# docker image ls
REPOSITORY               TAG                 IMAGE ID            CREATED             SIZE
k8s.gcr.io/kube-proxy    v1.13.4             fadcc5d2b066        8 days ago          80.3MB
quay.io/coreos/flannel   v0.11.0-amd64       ff281650a721        5 weeks ago         52.6MB
k8s.gcr.io/pause         3.1                 da86e6ba6ca1        14 months ago       742kB

此时在主节点查看node信息
[root@k8s-master ~]# kubectl get nodes
NAME         STATUS   ROLES    AGE     VERSION
k8s-master   Ready    master   56m     v1.13.4
k8s-node1    Ready    <none>   7m56s   v1.13.4
k8s-node2    Ready    <none>   7m42s   v1.13.4

获取节点的详细信息
# kubectl describe node k8s-node1
```

**如何解决从k8s.gcr.io拉取镜像失败问题**

```shell
解决方案
docker.io仓库对google的容器做了镜像，可以通过下列命令下拉取相关镜像：
docker pull mirrorgooglecontainers/kube-apiserver-amd64:v1.11.3
docker pull mirrorgooglecontainers/kube-controller-manager-amd64:v1.11.3
docker pull mirrorgooglecontainers/kube-scheduler-amd64:v1.11.3
docker pull mirrorgooglecontainers/kube-proxy-amd64:v1.11.3
docker pull mirrorgooglecontainers/pause:3.1
docker pull mirrorgooglecontainers/etcd-amd64:3.2.18
docker pull coredns/coredns:1.1.3
版本信息需要根据实际情况进行相应的修改。通过docker tag命令来修改镜像的标签：
docker tag docker.io/mirrorgooglecontainers/kube-proxy-amd64:v1.11.3 k8s.gcr.io/kube-proxy-amd64:v1.11.3
docker tag docker.io/mirrorgooglecontainers/kube-scheduler-amd64:v1.11.3 k8s.gcr.io/kube-scheduler-amd64:v1.11.3
docker tag docker.io/mirrorgooglecontainers/kube-apiserver-amd64:v1.11.3 k8s.gcr.io/kube-apiserver-amd64:v1.11.3
docker tag docker.io/mirrorgooglecontainers/kube-controller-manager-amd64:v1.11.3 k8s.gcr.io/kube-controller-manager-amd64:v1.11.3
docker tag docker.io/mirrorgooglecontainers/etcd-amd64:3.2.18  k8s.gcr.io/etcd-amd64:3.2.18
docker tag docker.io/mirrorgooglecontainers/pause:3.1  k8s.gcr.io/pause:3.1
docker tag docker.io/coredns/coredns:1.1.3  k8s.gcr.io/coredns:1.1.3
使用docker rmi删除不用镜像，通过docker images命令显示，已经有我们需要的镜像文件，可以继续部署工作了：

[root@zookeeper01 jinguang1]# docker images
REPOSITORY                                                               TAG                 IMAGE ID            CREATED             SIZE
k8s.gcr.io/kube-proxy-amd64                                              v1.11.3             be5a6e1ecfa6        10 days ago         97.8 MB
k8s.gcr.io/kube-scheduler-amd64                                          v1.11.3             ca1f38854f74        10 days ago         56.8 MB
k8s.gcr.io/kube-apiserver-amd64                                          v1.11.3             3de571b6587b        10 days ago         187 MB
coredns/coredns                                                          1.1.3               b3b94275d97c        3 months ago        45.6 MB
k8s.gcr.io/coredns                                                       1.1.3               b3b94275d97c        3 months ago        45.6 MB
k8s.gcr.io/etcd-amd64                                                    3.2.18              b8df3b177be2        5 months ago        219 MB

## k8s.gcr.io/pause                                                         3.1                 da86e6ba6ca1        9 months ago        742 kB
```

一些命令

```shell
列出指定命名的pod
kubectl get pods -n kube-system
查看指定pod resource的详细信息
 kubectl describe pod [POD_NAME] -n kube-system 
删除指定pod resource的详细信息
 kubectl delete pod [POD_NAME] -n kube-system  
查看指定pod resource的日志文件
 kubectl logs [POD_NAME] -n kube-system 
kubectl get po # 查看目前所有的pod
kubectl get rs # 查看目前所有的replica set
kubectl get deployment # 查看目前所有的deployment
kubectl label pods myapp-rc-9xmxs -n test-ns newlabel=hello 给指定pod添加label
kubectl label pods myapp-rc-9xmxs -n test-ns newlabel=world --overwrite 更新指定pod的指定label
kubectl label pod myapp-rc-9xmxs -n test-ns newlabel- 删除指定pod的指定label
kubectl get pod -n test-ns --show-labels  获取指定pod信息，以显示label的形式
```

k8s删除资源状态一直是Terminating。此为背景。
解决方法：

```shell
可使用kubectl中的强制删除命令
# 删除POD
kubectl delete pod PODNAME --force --grace-period=0
# 删除NAMESPACE
 kubectl delete namespace NAMESPACENAME --force --grace-period=0
```



#### 安装kubernetes-dashboard	 版本1.10.0
一、
通过官方yaml文件安装kubernetes-dashboard  登陆需要token

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v1.10.1/src/deploy/recommended/kubernetes-dashboard.yaml

# kubectl get svc -n kube-system

NAME                   TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)         AGE
kube-dns               ClusterIP   10.96.0.10       <none>        53/UDP,53/TCP   6h7m
kubernetes-dashboard   ClusterIP   10.103.109.218   <none>        443/TCP         7m26s

# kubectl patch svc kubernetes-dashboard -p '{"spec":{"type":"NodePort"}}' -n kube-system

service/kubernetes-dashboard patched

# kubectl get svc -n kube-system

NAME                   TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)         AGE
kube-dns               ClusterIP   10.96.0.10       <none>        53/UDP,53/TCP   6h13m
kubernetes-dashboard   NodePort    10.103.109.218   <none>        443:32646/TCP   14m

创建管理用户 并获取其token的方法
创建admin-user.yaml文件，内容如下
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: admin

##   namespace: kube-system

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:

- kind: ServiceAccount
  name: admin
  namespace: kube-system
 
 执行：kubectl create -f admin-user.yaml

 kubectl get secret -n kube-system列出账户信息

##  kubectl describe secret admin-token-[xxxxxxxx] -n kube-system取得登陆token
```

二、
修改官方yaml文件配置实现免token登录
修改以下

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: kubernetes-dashboard-minimal
  namespace: kube-system
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: kubernetes-dashboard
  namespace: kube-system
```

========================================================================================================================

部署nginx
cat nginx.yml

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
     app: nginx
spec:
     containers:
        - name: nginx
          image: nginx
          imagePullPolicy: IfNotPresent
          ports:
          - containerPort: 80
          volumeMounts:
          - mountPath: /usr/share/nginx/html/
            name: web-data
     restartPolicy: Always
     volumes:
     - name: web-data
       hostPath:
         path: /data/webdata
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: NodePort
  sessionAffinity: ClientIP
  selector:
    app: nginx
  ports:
    - port: 80
      nodePort: 30080
```

```shell
kubectl apply -f nginx.yml
```


创建了一个名为nginx的pod，把宿主机/data/webdata挂载到容器中/usr/share/nginx/html/下

进入容器的bash

```shell
kubectl exec nginx -it bash
```

获取资源api资源类型

```shell
kubectl api-resources
```

获取资源api版本

```shell
kubectl api-versions
[root@k8s-master ~]# kubectl api-versions
admissionregistration.k8s.io/v1beta1
apiextensions.k8s.io/v1beta1
apiregistration.k8s.io/v1
apiregistration.k8s.io/v1beta1
apps/v1
apps/v1beta1
apps/v1beta2
authentication.k8s.io/v1
authentication.k8s.io/v1beta1
authorization.k8s.io/v1
authorization.k8s.io/v1beta1
autoscaling/v1
autoscaling/v2beta1
autoscaling/v2beta2
batch/v1
batch/v1beta1
certificates.k8s.io/v1beta1
coordination.k8s.io/v1beta1
events.k8s.io/v1beta1
extensions/v1beta1
networking.k8s.io/v1
policy/v1beta1
rbac.authorization.k8s.io/v1
rbac.authorization.k8s.io/v1beta1
scheduling.k8s.io/v1beta1
storage.k8s.io/v1
storage.k8s.io/v1beta1

## v1
```

1、创建一个名为nginx-test的deployment，使用的镜像是nginx:latest

```shell
# kubectl create deployment nginx-test --image=nginx:latest

[root@k8s-master ~]# kubectl get all
NAME                              READY   STATUS    RESTARTS   AGE
pod/nginx-test-6bc94865df-vscnv   1/1     Running   0          2m30s
NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
service/kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   42h
NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/nginx-test   1/1     1            1           2m30s
NAME                                    DESIRED   CURRENT   READY   AGE
replicaset.apps/nginx-test-6bc94865df   1         1         1       2m30s

查看创建的pod的信息
[root@k8s-master ~]# kubectl get pod -o wide
NAME                          READY   STATUS    RESTARTS   AGE     IP           NODE        NOMINATED NODE   READINESS GATES
nginx-test-6bc94865df-vscnv   1/1     Running   0          3m37s   10.244.2.6   k8s-node2   <none>           <none>
通过ip 10.244.2.6 可以访问nginx web资源
```

2、clusterip service 
创建一个cluster service关联nginx-test deployment的clusterip service 并将其80端口和pod的80端口作映射

```shell
# kubectl create service clusterip nginx-test --tcp=80:80

[root@k8s-master ~]# kubectl get svc nginx-test -o wide
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE     SELECTOR
nginx-test   ClusterIP   10.103.214.69   <none>        80/TCP    2m32s   app=nginx-test

yaml格式输出nginx-test service的信息
[root@k8s-master ~]# kubectl get svc nginx-test -o yaml
apiVersion: v1
kind: Service
metadata:
  creationTimestamp: "2019-03-11T11:38:46Z"
  labels:
    app: nginx-test
  name: nginx-test
  namespace: default
  resourceVersion: "93967"
  selfLink: /api/v1/namespaces/default/services/nginx-test
  uid: 3b12817e-43f2-11e9-aa7d-000c299777e4
spec:
  clusterIP: 10.103.214.69
  ports:

- name: 80-80
  port: 80
  protocol: TCP
  targetPort: 80
    selector:
  app: nginx-test
    sessionAffinity: None
    type: ClusterIP
  status:
    loadBalancer: {}

通过describe获取service信息
[root@k8s-master ~]# kubectl describe service nginx-test
Name:              nginx-test
Namespace:         default
Labels:            app=nginx-test
Annotations:       <none>
Selector:          app=nginx-test
Type:              ClusterIP
IP:                10.103.214.69
Port:              80-80  80/TCP
TargetPort:        80/TCP
Endpoints:         10.244.2.6:80
Session Affinity:  None
Events:            <none>

通过10.103.214.69  可以访问nginx web资源
```

3、nodeport service
删除上面创建的名为nginx-test的clusterip service，创建一个名为nginx-test的nodeport service并将其 80端口和pod 80端口作映射关联

```shell
[root@k8s-master ~]# kubectl get svc nginx-test -o wide
NAME         TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE     SELECTOR
nginx-test   NodePort   10.111.66.176   <none>        80:31274/TCP   2m17s   app=nginx-test

[root@k8s-master ~]# kubectl describe svc nginx-test
Name:                     nginx-test
Namespace:                default
Labels:                   app=nginx-test
Annotations:              <none>
Selector:                 app=nginx-test
Type:                     NodePort
IP:                       10.111.66.176
Port:                     80-80  80/TCP
TargetPort:               80/TCP
NodePort:                 80-80  31274/TCP
Endpoints:                10.244.1.12:80,10.244.2.6:80
Session Affinity:         None
External Traffic Policy:  Cluster
Events:                   <none>
通过节点IP:31274可以访问nginx web资源
```

4、
对deployment进行扩容 
```shell
# kubectl scale --replicas=2 deployment nginx-test

扩容至2个
[root@k8s-master ~]# kubectl get pods
NAME                          READY   STATUS    RESTARTS   AGE
nginx-test-6bc94865df-tnz85   1/1     Running   0          74s
nginx-test-6bc94865df-vscnv   1/1     Running   0          32m

查看service信息 
[root@k8s-master ~]# kubectl describe svc nginx-test
Name:              nginx-test
Namespace:         default
Labels:            app=nginx-test
Annotations:       <none>
Selector:          app=nginx-test
Type:              ClusterIP
IP:                10.103.214.69
Port:              80-80  80/TCP
TargetPort:        80/TCP
Endpoints:         10.244.1.12:80,10.244.2.6:80
Session Affinity:  None

## Events:  
```

​    查询资源定义
This command describes the fields associated with each supported API resource

kubectl explain RESOURCE [options]

yaml格式的pod定义文件完整内容：

~~~yml
```

apiVersion: v1        　　#必选，版本号，例如v1
kind: Pod       　　　　　　#必选，Pod
metadata:       　　　　　　#必选，元数据
  name: string        　　#必选，Pod名称
  namespace: string     　　#必选，Pod所属的命名空间
  labels:       　　　　　　#自定义标签

- name: string      　#自定义标签名字
  annotations:        　　#自定义注释列表
  - name: string
    spec:         　　　　　　　#必选，Pod中容器的详细定义
      containers:       　　　　#必选，Pod中容器列表

- name: string      　　#必选，容器名称
  image: string     　　#必选，容器的镜像名称
  imagePullPolicy: [Always | Never | IfNotPresent]  #获取镜像的策略 Alawys表示下载镜像 IfnotPresent表示优先使用本地镜像，否则下载镜像，Nerver表示仅使用本地镜像
  command: [string]     　　#容器的启动命令列表，如不指定，使用打包时使用的启动命令
  args: [string]      　　 #容器的启动命令参数列表
  workingDir: string      #容器的工作目录
  volumeMounts:     　　　　#挂载到容器内部的存储卷配置
  - name: string      　　　#引用pod定义的共享存储卷的名称，需用volumes[]部分定义的的卷名
    mountPath: string     #存储卷在容器内mount的绝对路径，应少于512字符
    readOnly: boolean     #是否为只读模式
    ports:        　　　　　　#需要暴露的端口库号列表
  - name: string      　　　#端口号名称
    containerPort: int    #容器需要监听的端口号
    hostPort: int     　　 #容器所在主机需要监听的端口号，默认与Container相同
    protocol: string      #端口协议，支持TCP和UDP，默认TCP
    env:        　　　　　　#容器运行前需设置的环境变量列表
  - name: string      　　#环境变量名称
    value: string     　　#环境变量的值
    resources:        　　#资源限制和请求的设置
    limits:       　　　　#资源限制的设置
      cpu: string     　　#Cpu的限制，单位为core数，将用于docker run --cpu-shares参数
      memory: string      #内存限制，单位可以为Mib/Gib，将用于docker run --memory参数
    requests:       　　#资源请求的设置
      cpu: string     　　#Cpu请求，容器启动的初始可用数量
      memory: string      #内存清楚，容器启动的初始可用数量
    livenessProbe:      　　#对Pod内个容器健康检查的设置，当探测无响应几次后将自动重启该容器，检查方法有exec、httpGet和tcpSocket，对一个容器只需设置其中一种方法即可
    exec:       　　　　　　#对Pod容器内检查方式设置为exec方式
      command: [string]   #exec方式需要制定的命令或脚本
    httpGet:        　　　　#对Pod内个容器健康检查方法设置为HttpGet，需要制定Path、port
      path: string
      port: number
      host: string
      scheme: string
      HttpHeaders:
    - name: string
      value: string
      tcpSocket:      　　　　　　#对Pod内个容器健康检查方式设置为tcpSocket方式
         port: number
       initialDelaySeconds: 0   #容器启动完成后首次探测的时间，单位为秒
       timeoutSeconds: 0    　　#对容器健康检查探测等待响应的超时时间，单位秒，默认1秒
       periodSeconds: 0     　　#对容器监控检查的定期探测时间设置，单位秒，默认10秒一次
       successThreshold: 0
       failureThreshold: 0
       securityContext:
         privileged: false
      restartPolicy: [Always | Never | OnFailure] #Pod的重启策略，Always表示一旦不管以何种方式终止运行，kubelet都将重启，OnFailure表示只有Pod以非0退出码退出才重启，Nerver表示不再重启该Pod
      nodeSelector: obeject   　　#设置NodeSelector表示将该Pod调度到包含这个label的node上，以key：value的格式指定
      imagePullSecrets:     　　　　#Pull镜像时使用的secret名称，以key：secretkey格式指定
  - name: string
    hostNetwork: false      　　#是否使用主机网络模式，默认为false，如果设置为true，表示使用宿主机网络
    volumes:        　　　　　　#在该pod上定义共享存储卷列表
  - name: string     　　 　　#共享存储卷名称 （volumes类型有很多种）
    emptyDir: {}      　　　　#类型为emtyDir的存储卷，与Pod同生命周期的一个临时目录。为空值
    hostPath: string      　　#类型为hostPath的存储卷，表示挂载Pod所在宿主机的目录
      path: string      　　#Pod所在宿主机的目录，将被用于同期中mount的目录
    secret:       　　　　　　#类型为secret的存储卷，挂载集群与定义的secre对象到容器内部
      scretname: string  
      items:     
    - key: string
      path: string
      configMap:      　　　　#类型为configMap的存储卷，挂载预定义的configMap对象到容器内部
        name: string
        items:
    - key: string
      path: string    
~~~

**example 1：**

cat rc-test.yml

```yaml
apiVersion: v1
kind: ReplicationController
metadata:
  name: myapp-rc
  namespace: test-ns
spec:
  replicas: 2
  selector:
    app: myapp-rc
  template:
    metadata:
      labels:
        app: myapp-rc
    spec:
      containers:
	  - name: myapp-rc
		image: ikubernetes/myapp:v7
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-rc
  namespace: test-ns
spec:
  type: ClusterIP
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: myapp-rc
```


创建ReplicationController和与之关联的service serivce类型是clusterip  namespace:test-ns label:myapp-rc

```shell
kubectl create -f rc-test.yaml
kubectl get pod -n test-ns -o wide
NAME             READY   STATUS    RESTARTS   AGE   IP            NODE        NOMINATED NODE   READINESS GATES
myapp-rc-9xmxs   1/1     Running   0          64m   10.244.2.12   k8s-node2   <none>           <none>
myapp-rc-trnp4   1/1     Running   0          64m   10.244.1.18   k8s-node1   <none>           <none>
```

```shell
# kubectl get svc -n test-ns -o wide
NAME       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE   SELECTOR
myapp-rc   ClusterIP   10.109.183.48   <none>        80/TCP    58m   app=myapp-rc
```

kubectl describe svc myapp-rc -n test-ns

```shell
Name:              myapp-rc
Namespace:         test-ns
Labels:            <none>
Annotations:       kubectl.kubernetes.io/last-applied-configuration:
{"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"name":"myapp-rc","namespace":"test-ns"},"spec":{"ports":[{"port":80,"pro...
Selector:          app=myapp-rc
Type:              ClusterIP
IP:                10.109.183.48
Port:              <unset>  80/TCP
TargetPort:        80/TCP
Endpoints:         10.244.1.18:80,10.244.2.12:80
Session Affinity:  None
Events:            <none>
```



Ingress本质是通过http代理服务器将外部的http请求转发到集群内部的后端服务

Ingress由两部分组成：Ingress Controller 和 Ingress 服务。

Ingress Contronler 通过与 Kubernetes API 交互，动态的去感知集群中 Ingress 规则变化，然后读取它，按照自定义的规则，规则就是写明了哪个域名对应哪个service，生成一段 Nginx 配置，再写到 Nginx-ingress-control的 Pod 里，这个 Ingress Contronler 的pod里面运行着一个nginx服务，控制器会把生成的nginx配置写入/etc/nginx.conf文件中，然后 reload 一下 使用配置生效。以此来达到域名分配置及动态更新的问题。

部署ingress-nginx例子
https://kubernetes.github.io/ingress-nginx/deploy/

1、
创建Nginx-ingress-controller pod

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/mandatory.yaml

kubectl get pod -n ingress-nginx
NAME                                        READY   STATUS    RESTARTS   AGE
nginx-ingress-controller-797b884cbc-6fh2s   1/1     Running   0          6m33s
```

2、
为上面的Nginx-ingress-control创建一个service

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/provider/baremetal/service-nodeport.yaml

cat service-nodeport.yaml

apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
spec:
  type: NodePort
  ports:
    - name: http
      port: 80
      targetPort: 80
      protocol: TCP
      nodePort: 30080
    - name: https
      port: 443
      targetPort: 443
      protocol: TCP
      nodePort: 30443
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx

kubectl get svc -n ingress-nginx

NAME            TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx   NodePort   10.99.107.150   <none>        80:30080/TCP,443:30443/TCP   7s
```

3、
创建后端测试pod

```shell
cat ingress-test.yml
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-myapp
  namespace: test-ns
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path:
        backend:
          serviceName: myapp-rc
          servicePort: 80
[root@k8s-master ingress-nginx]# cat rc-test.yml
apiVersion: v1
kind: Namespace
metadata:
  name: test-ns
spec:
------
apiVersion: v1
kind: ReplicationController
metadata:
  name: myapp-rc
  namespace: test-ns
spec:
  replicas: 2
  selector:
    app: myapp-rc
  template:
    metadata:
      labels:
        app: myapp-rc
    spec:
      containers:
      - name: myapp-rc
        image: ikubernetes/myapp:v7
------
apiVersion: v1
kind: Service
metadata:
  name: myapp-rc
  namespace: test-ns
spec:
  #type: ClusterIP
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: myapp-rc
```

4、
创建一个ingress 并将其和上面创建的myapp-rc service关联

```shell
cat ingress-test.yml
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-myapp
  namespace: test-ns
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path:
        backend:
          serviceName: myapp-rc
          servicePort: 80

# kubectl get ing -n test-ns

NAME            HOSTS               ADDRESS   PORTS   AGE
ingress-myapp   myapp.example.com             80      28s
```

查看详细描述信息

```shell
kubectl describe ing ingress-myapp -n test-ns

Name:             ingress-myapp
Namespace:        test-ns
Address:
Default backend:  default-http-backend:80 (<none>)
Rules:
  Host               Path  Backends

------

  myapp.example.com
                        myapp-rc:80 (<none>)
Annotations:
  kubectl.kubernetes.io/last-applied-configuration:  {"apiVersion":"extensions/v1beta1","kind":"Ingress","metadata":{"annotations":{"kubernetes.io/ingress.class":"nginx"},"name":"ingress-myapp","namespace":"test-ns"},"spec":{"rules":[{"host":"myapp.example.com","http":{"paths":[{"backend":{"serviceName":"myapp-rc","servicePort":80},"pat":null}]}}]}}

  kubernetes.io/ingress.class:  nginx
Events:
  Type    Reason  Age    From                      Message

------

  Normal  CREATE  4m48s  nginx-ingress-controller  Ingress test-ns/ingress-myapp
```

进入ingress-nginx的pod 查看nginx.conf可以看到myapp.example.com的信息
kubectl exec -it -n ingress-nginx nginx-ingress-controller-797b884cbc-6fh2s bash

start server myapp.example.com

	server {
		server_name myapp.example.com ;
	
		listen 80;
	
		set $proxy_upstream_name "-";
	
		location / {
	
			set $namespace      "test-ns";
			set $ingress_name   "ingress-myapp";
			set $service_name   "myapp-rc";
			set $service_port   "80";
			set $location_path  "/";
....

在客户端电脑修改hosts文件，然后浏览器访问http://myapp.example.com:30080

```shell
[root@k8s-master ingress-nginx]# curl myapp.example.com:30080/hostname.html
myapp-rc-vhcjb
[root@k8s-master ingress-nginx]# curl myapp.example.com:30080/hostname.html
myapp-rc-vzwl6
```



+++++++++++++++++++++++++++++++++++++++++++
配置ssl tls访问


生成key
```shell
openssl genrsa -out nginx_ingress.key
```

创建自签证书
```shell
openssl req -new -x509 -key nginx_ingress.key -out nginx_ingress.crt
```

创建secret对象
```shell
# kubectl create secret tls myapp-ingress-secret --cert=nginx_ingress.crt --key=nginx_ingress.key

secret/myapp-ingress-secret created
```

查看创建结果：
```shell
# kubectl get secret

NAME                   TYPE                                  DATA   AGE
default-token-24f2c    kubernetes.io/service-account-token   3      6d16h
myapp-ingress-secret   kubernetes.io/tls                     2      34s
```


测试用例
```yaml
# cat ingress-test-tls.yml
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-myapp-tls
  namespace: test-ns
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  tls: 
  - hosts:
    - myapp.example.com
    secretName: myapp-ingress-secret
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path:
        backend:
          serviceName: myapp-rc
          servicePort: 80

# kubectl apply -f ingress-test-tls.yml
kubectl get ing -n test-ns
NAME                HOSTS               ADDRESS   PORTS     AGE
ingress-myapp       myapp.example.com             80        100m
ingress-myapp-tls   myapp.example.com             80, 443   14s

进入ingress-nginx的pod 查看nginx.conf可以看到myapp.example.com的信息443端口 ssl已经注入进去了
kubectl exec -it -n ingress-nginx nginx-ingress-controller-797b884cbc-6fh2s bash

start server myapp.example.com

​	server {
​		server_name myapp.example.com ;

​	listen 80;

​	set $proxy_upstream_name "-";

​	listen 443  ssl http2;

# PEM sha: cb5ed13051761519240a5abe36b5fa7677b239ca

​	ssl_certificate                         /etc/ingress-controller/ssl/default-fake-certificate.pem;
​	ssl_certificate_key                     /etc/ingress-controller/ssl/default-fake-certificate.pem;
```

浏览器访问https://myapp.example.com:30443



在Docker中就有数据卷的概念，当容器删除时，数据也一起会被删除，想要持久化使用数据，需要把主机上的目录挂载到Docker中去，在K8S中，数据卷是通过Pod实现持久化的，如果Pod删除，数据卷也会一起删除，k8s的数据卷是docker数据卷的扩展，K8S适配各种存储系统，包括本地存储EmptyDir,HostPath,网络存储NFS,GlusterFS,PV/PVC等，下面就详细介绍下K8S的存储如何实现。

一.本地存储
1，EmptyDir
①编辑EmptyDir配置文件

```yaml
# vim emptydir.yaml
apiVersion: v1
kind: Pod        #类型是Pod
metadata:
  labels:
    name: redis
    role: master        #定义为主redis
  name: redis-master
spec:
  containers:
  - name: master
    image: redis:latest
    env:        #定义环境变量
      - name: MASTER
        value: "true"
    ports:        #容器内端口
      - containerPort: 6379
    volumeMounts:        #容器内挂载点
      - mountPath: /data
        name: redis-data        #必须有名称
  volumes:
    - name: redis-data        #跟上面的名称对应
      emptyDir: {}        #宿主机挂载点
```

②创建Pod

```shell
kubectl create -f emptydir.yaml
```

此时Emptydir已经创建成功，在宿主机上的访问路径为/var/lib/kubelet/pods/<pod uid>/volumes/kubernetes.io~empty-dir/redis-data,如果在此目录中创建删除文件，都将对容器中的/data目录有影响，如果删除Pod，文件将全部删除，即使是在宿主机上创建的文件也是如此，在宿主机上删除容器则k8s会再自动创建一个容器，此时文件仍然存在。

2.HostDir
在宿主机上指定一个目录，挂载到Pod的容器中，其实跟上面的写法不尽相同，这里只截取不同的部分，当pod删除时，本地仍然保留文件

```yaml
...
  volumes:
    - name: redis-data        #跟上面的名称对应
      hostPath: 
        path: /data      #宿主机挂载点
```

二.网络数据卷(NFS)
1.NFS
①编辑一个使用NFS的Pod的配置文件

```yaml
# vim nfs.yaml

apiVersion: v1
kind: Pod
metadata:
  name: nfs-web
spec:
  containers:
    - name: web
      image: nginx
      imagePullPolicy: Never        #如果已经有镜像，就不需要再拉取镜像
      ports:
        - name: web
          containerPort: 80
          hostPort: 80        #将容器的80端口映射到宿主机的80端口
      volumeMounts:
        - name : nfs        #指定名称必须与下面一致
          mountPath: "/usr/share/nginx/html"        #容器内的挂载点
  volumes:
    - name: nfs            #指定名称必须与上面一致
      nfs:            #nfs存储
        server: 192.168.66.50        #nfs服务器ip或是域名
        path: "/test"                #nfs服务器共享的目录
```

②创建Pod

```shell
kubectl create -f nfs.yaml
```

在节点端可以用mount命令查询挂载情况

在节点端可以用mount命令查询挂载情况

三.Persistent Volume(PV)和Persistent Volume Claim(PVC)
persistentVolumeClaim类型存储卷将PersistentVolume挂接到Pod中作为存储卷。使用此类型的存储卷，用户并不知道存储卷的详细信息。下面就来实现PV/PVC架构。
1.Persistent Volume(PV)
①编辑PV配置文件
vim persistent-volume.yaml

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv
  labels:
    type: nfs        #指定类型是NFS
spec:
  capacity:            #指定访问空间是15G
    storage: 15Gi
  accessModes:        #指定访问模式是能在多节点上挂载，并且访问权限是读写执行
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Recycle        #指定回收模式是自动回收，当空间被释放时，K8S自动清理，然后可以继续绑定使用
  nfs:
    server: 192.168.66.50
    path: /test
```

②创建PV

```shell
kubectl create -f  persistent-volume.yaml 
```

2.Persistent Volume Claim(PVC)
①编辑PVC配置文件
vim test-pvc.yaml 

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:        #指定请求的资源，存储3G
    requests:
      storage: 3Gi
```

如果当前有两个PV,一个10G，一个2G，请求资源为3G,那么将直接使用10GPV
②创建PVC

```shell
kubectl create -f test-pvc.yaml
```

3.创建Pod以使用PVC

vim pv-pod.yaml

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: redis111
  labels:
    app: redis111
spec:
  containers:
  - name: redis
    image: redis
    imagePullPolicy: Never
	volumeMounts:
    - mountPath: "/data"
      name: data
	ports:
	- containerPort: 6379
volumes:
- name: data
  persistentVolumeClaim:        #指定使用的PVC
  	claimName: test-pvc           #名字一定要正确
```

当前Pod可用空间为3G，如果超过3G，则需要再创建存储来满足需求，因为是网络数据卷，如果需要扩展空间，直接删除Pod再建立一个即可。