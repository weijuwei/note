#### k8s安装部署
##### 一、版本信息

centos7.5
master 192.168.47.141
node1  192.168.47.142
node2  192.168.47.143

docker-ce 18.09.3
kubectl-1.13.4-0.x86_64
kubeadm-1.13.4-0.x86_64
kubectl-1.13.4-0.x86_64

##### 二、准备

ssh互信
ntpd时间同步
hosts域名解析
关闭firewall和selinux
禁用swap  临时禁用命令swapoff -a  永久禁用在fstab文件中编辑

加载ipvs内核模块
modprobe br_netfilter
或
```shell
#!/bin/bash
ipvs_mods_dir="/usr/lib/modules/$(uname -r)/kernel/net/netfilter/ipvs"
for i in $(ls $ipvs_mods_dir | grep -o "^[^.]*"); do
    /sbin/modinfo -F filename $i  &> /dev/null
    if [ $? -eq 0 ]; then
        /sbin/modprobe $i
    fi
done
```

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

##### 三、三节点安装相关程序包

```shell
yum install docker-ce -y
yum install kubelet kubeadm kubectl -y
```

在各节点启动docker服务
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

##### 四、初始化主节点master

systemctl enable kubelet
systemctl start kubelet

###### 1、主节点镜像拉取

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

###### 2、主节点初始化

```shell
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

# 查看join信息
[root@k8s-master ~]# kubeadm token create --print-join-command
kubeadm join 192.168.47.141:6443 --token ij2pbh.vrl8jk7o2pm588xh --discovery-token-ca-cert-hash sha256:a5e085b08c38e1be284ef74c9f734a0af299d36fd5ab65d8e8e43714b55a629b

[root@k8s-master ~]# mkdir .kube
[root@k8s-master ~]# cp /etc/kubernetes/admin.conf .kube/config

查看节点kubectl get node
[root@k8s-master ~]# kubectl get node
NAME         STATUS     ROLES    AGE   VERSION
k8s-master   NotReady   master   26m   v1.13.4
```

###### 3、安装部署pod网络   flannel

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

k8s.gcr.io/pause                                                         3.1                 da86e6ba6ca1        9 months ago        742 kB
```

###### 4、一些命令

```shell
# kubectl命令行自动补全
source <(kubectl completion bash)
echo "source <(kubectl completion bash)" >> ~/.bashrc
#列出指定命名的pod
kubectl get pods -n kube-system
#查看指定pod resource的详细信息
kubectl describe pod [POD_NAME] -n kube-system 
#删除指定pod resource的详细信息
kubectl delete pod [POD_NAME] -n kube-system  
#查看指定pod resource的日志文件
kubectl logs [POD_NAME] -n kube-system 
kubectl get po # 查看目前所有的pod
kubectl get rs # 查看目前所有的replica set
kubectl get deployment # 查看目前所有的deployment
kubectl label pods myapp-rc-9xmxs -n test-ns newlabel=hello # 给指定pod添加label
kubectl label pods myapp-rc-9xmxs -n test-ns newlabel=world --overwrite #更新指定pod的指定label
kubectl label pod myapp-rc-9xmxs -n test-ns newlabel #删除指定pod的指定label
kubectl get pod -n test-ns --show-labels  #获取指定pod信息，以显示label的形式
kubectl get pods --show-labels  # 显示对象的标签信息
kubectl get pods -l test  # 显示带有test标签的对象
#当 Pod 中有多个容器时打开一个 shell
#如果 Pod 中有多个容器，使用 --container 或 -c 在 kubectl exec 命令中指定一个容器。例如，假设你有一个 Pod 叫 my-pod ，并且这个 Pod 中有两个容器，分别叫做 main-app 和 helper-app 。下面的命令将会打开 main-app 容器的 shell 。
kubectl exec -it my-pod --container main-app -- /bin/bash
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

###### 5、安装kubernetes-dashboard	 版本1.10.0
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

#创建管理用户 并获取其token的方法
#创建admin-user.yaml文件，内容如下
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: admin
  namespace: kube-system

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
 
 # 执行：kubectl create -f admin-user.yaml

 kubectl get secret -n kube-system #列出账户信息

kubectl describe secret admin-token-[xxxxxxxx] -n kube-system #取得登陆token
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

=======================================================================================

#### yaml文件定义

查询资源定义
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

当用户同时在kubernetes中的yaml文件中写了command和args的时候自然是可以覆盖DockerFile中ENTRYPOINT的命令行和参数,完整的情况分类如下：

- 如果command和args均没有写，那么用Docker默认的配置。
- 如果command写了，但args没有写，那么Docker默认的配置会被忽略而且仅仅执行.yaml文件的command（不带任何参数的）。
- 如果command没写，但args写了，那么Docker默认配置的ENTRYPOINT的命令行会被执行，但是调用的参数是.yaml中的args。
- 如果如果command和args都写了，那么Docker默认的配置被忽略，使用.yaml的配置。

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


#### 数据卷Volume

Volume隶属于Pod资源，共享于Pod内的所有容器，可用于在容器的文件系统之外存储应用程序的相关数据，甚至可以独立于Pod的生命周期之外实现数据持久化。

在Docker中就有数据卷的概念，当容器删除时，数据也一起会被删除，想要持久化使用数据，需要把主机上的目录挂载到Docker中去，在K8S中，数据卷是通过Pod实现持久化的，如果Pod删除，数据卷也会一起删除，k8s的数据卷是docker数据卷的扩展，K8S适配各种存储系统，包括本地存储EmptyDir,HostPath,网络存储NFS,GlusterFS,PV/PVC等，下面就详细介绍下K8S的存储如何实现。

在Pod中定义使用存储卷的配置由两部分组成：

- 通过spec.volumes字段定义在Pod之上的存储卷列表
- 通过spec.containers.volumeMounts字段在容器上定义的存储卷挂载列表，它只能挂载当前Pod资源中定义的具体存储卷。

##### 一.本地存储
1，EmptyDir

emptyDir存储卷的生命周期与其所属的Pod对象相同，它无法脱离Pod对象的生命周期提供数据存储功能，通常用于数据缓存或临时存储。

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

2.HostPath

hostPath类型的存储卷是指将工作节点上某文件系统的目录或文件挂载于Pod中的一种存储卷，它可独立于Pod资源的生命周期，因而具有持久性。

在宿主机上指定一个目录，挂载到Pod的容器中，其实跟上面的写法不尽相同，这里只截取不同的部分，当pod删除时，本地仍然保留文件

```yaml
...
  volumes:
    - name: redis-data        #跟上面的名称对应
      hostPath: 
        path: /data      #宿主机挂载点
```

##### 二.网络数据卷(NFS)
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

##### 三.Persistent Volume(PV)和Persistent Volume Claim(PVC)
PersistentVolume(PV)是指由集群管理员配置提供的某存储系统上的一段存储空间，它是对底层共享存储的抽象，将共享存储作为一种可由用户申请使用的资源，实现了“存储消费”机制。

PV是集群级别的资源，不属于任何名称空间

用户对PV资源的使用需要通过PersistentVolumeClaim(PVC)提出使用申请来完成绑定，PVC是PV资源的消费者，它向PV申请特定大小的空间及访问模式，从而创建出PVC存储卷，而后再由Pod资源通过PersistentVolumeClaim存储卷关联使用。

PVC是存储类型的资源，它通过申请占用某个PV而创建，它与PV是一对一的关系，用户无须关心其底层实现细节，申请时，用户只需要指定目标空间的大小、访问模式、PV标签选择器和StorageClass等相关信息即可。

persistentVolumeClaim类型存储卷将PersistentVolume挂接到Pod中作为存储卷。使用此类型的存储卷，用户并不知道存储卷的详细信息。下面就来实现PV/PVC架构。
1.Persistent Volume(PV)  
①编辑PV配置文件
vim pv-demo.yaml

```yaml
# cat pv-demo.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-nfs-demo
  labels:
    release: stable
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem  # 卷模型，裸设备的块设备或文件系统（Filesystem），默认是Filesystem
  accessModes:  #指定访问模式是能在多节点上挂载，并且访问权限是读写执行
  - ReadWriteMany
  persistentVolumeReclaimPolicy: Recycle  #指定回收模式是自动回收，当空间被释放时，K8S自动清理，然后可以继续绑定使用
  storageClassName: slow
  mountOptions:
  - hard
  - nfsvers=4.1
  nfs:
    path: "/data/webdata"
    server: master
```

accessModes访问模式：

- ReadWriteOnce：仅可被单个节点读写挂载；命令行可简写RWO
- ReadOnlyMany：可被多个节点同时只读挂载；ROX
- ReadWriteMany：可被多个节点同时读写挂载；RWX

空间释放处理persistentVolumeReclaimPolicy：

- Retain：保持不动，由管理员手动处理
- Recycle：空间回收，即删除存储卷目录下的所有文件，目前仅NFS和hostPath支持此操作
- Delete：删除存储卷

②创建PV  

```shell
kubectl create -f  pv-demo.yaml 
```

查看信息

```shell
[root@k8s-master volume]# kubectl get pv
NAME          CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM              STORAGECLASS   REASON   AGE
pv-nfs-demo   5Gi        RWX            Recycle          Bound    default/pvc-demo   slow                    35m
```

PV状态

- Available：可用状态的自由资源，尚未被PVC绑定
- Bound：已经绑定至PVC
- Released：绑定的PVC已经被删除，但资源尚未被回收
- Failed：因自动回收资源失败处于的故障状态

2.Persistent Volume Claim(PVC)  
①编辑PVC配置文件
vim pvc-demo.yaml 

```yaml
# cat pvc-demo.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-demo
  labels:
   release: stable
spec:
  accessModes:
  - ReadWriteMany
  selector:   # 匹配PV标签
    matchLabels:
      release: stable
  volumeMode: Filesystem
  resources:
    requests:
      storage: 2Gi
  storageClassName: slow
```


②创建PVC

```shell
kubectl create -f pvc-demo.yaml
```

3.创建Pod以使用PVC

vim pv-pod.yaml

```yaml
# cat pod-pvc-demo.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-pvc-demo
spec:
  containers:
  - name: myapp-pvc
    image: ikubernetes/myapp:v6
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
      name: myapp-http
    volumeMounts:
    - name: pvc-vol
      mountPath: /usr/share/nginx/html/
  volumes:
  - name: pvc-vol
    persistentVolumeClaim:
      claimName: pvc-demo
```

##### 四、DownwardAPI

Downward API 可以通过以下两种方式将Pod信息注入容器内部。
 1.环境变量：用于单个变量，可以将Pod信息和Container信息注入容器内部。

```yaml
# cat downwardAPI-env.yaml
apiVersion: v1
kind: Pod
metadata:
  name: env-test-pod
  labels:
    app: env-test-pod
spec:
  containers:
  - name: env-test-container
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command: ["/bin/sh","-c","env"]
    resources:
      limits:
        memory: 64Mi
        cpu: 250m
    env:
    - name: MY_POD_NAME
      valueFrom:
        fieldRef:
          fieldPath: metadata.name
    - name: MY_POD_NAMESPACE
      valueFrom:
        fieldRef:
          fieldPath: metadata.namespace
    - name: MY_POD_LABEL
      valueFrom:
        fieldRef:
          fieldPath: metadata.labels['app']
    - name: MY_CPU_LIMIT
      valueFrom:
        resourceFieldRef:
          resource: limits.cpu
    - name: MY_MEM_REQUEST
      valueFrom:
        resourceFieldRef:
          resource: requests.memory
          divisor: 1Mi
  restartPolicy: Never
```

 2.Volume挂载： 将数组类信息生成文件，挂载到容器内部。

```yaml
# cat downwardAPI-env2.yaml
apiVersion: v1
kind: Pod
metadata:
  name: env-test-pod
  labels:
    app: env-test-pod
spec:
  containers:
  - name: env-test-container
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command: ["/bin/sh","-c","sleep 600"]
    resources:
      limits:
        memory: 64Mi
        cpu: 250m
    volumeMounts:
    - name: podinfo
      mountPath: /podinfo
      readOnly: false
  volumes:
  - name: podinfo
    downwardAPI:
      defaultMode: 420
      items:
      - fieldRef:
          fieldPath: metadata.name
        path: pod_name
      - fieldRef:
          fieldPath: metadata.namespace
        path: pod_namespace
      - fieldRef:
          fieldPath: metadata.labels
        path: pod_labels
      - resourceFieldRef:
          containerName: env-test-container
          resource: limits.cpu
        path: pod_cpu
      - resourceFieldRef:
          containerName: env-test-container
          resource: limits.memory
          divisor: 1Mi
        path: pod_mem
  restartPolicy: Never
```

查看

```shell
[root@k8s-master volume]# kubectl exec env-test-pod -- ls /podinfo
pod_cpu
pod_labels
pod_mem
pod_name
pod_namespace

[root@k8s-master volume]# kubectl exec env-test-pod -- cat /podinfo/pod_name
env-test-pod
```

##### 六、configMap作为volumes

创建一个configmap

```shell
[root@k8s-master ~]# kubectl create configmap cm-demo --from-literal=user=admin --from-literal=password=123456
```

创建一个pod，并将configmap作为volumes挂载到容器的的目录

```yaml
[root@k8s-master volume]# cat pod-configmap-volume-demo.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-cm-vol-demo
spec:
  containers:
  - name: pod-cm-vol
    image: ikubernetes/myapp:v6
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
      name: http
    volumeMounts:
    - name: user
      mountPath: /user/
  volumes:
  - name: user
    configMap:
      name: cm-demo
```

查看

```shell
[root@k8s-master volume]# kubectl exec pod-cm-vol-demo -- ls /user
password
user

[root@k8s-master volume]# kubectl exec pod-cm-vol-demo -- cat /user/password
123456

[root@k8s-master volume]# kubectl exec pod-cm-vol-demo -- cat /user/user
admin
```

挂载多个中部分key   定义spec.volumes.configMap.items

```yaml
  volumes:
  - name: user
    configMap:
      name: cm-demo
      items:
      - key: user
        path: ./user
```

#### Pod生命周期中的一些行为

##### 1、初始化容器

 应用程序的主容器启动之前要运行的容器，常用于为主容器执行一些预置操作

Pod资源的spec.initContainers字段以列表的形式定义可用的初始容器

```shell
# cat pod-initcontainer.yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod-init
  labels:
    app: myapp-init
spec:
  containers:
  - name: myapp-container
    image: ikubernetes/myapp:v7
    imagePullPolicy: IfNotPresent
  initContainers:
  - name: init-something
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command: ["sh","-c","sleep 15"]
# 观察容器状态
[root@k8s-master manifests]# kubectl get pod
NAME                  READY   STATUS     RESTARTS   AGE
myapp-pod-init        0/1     Init:0/1   0          5s
[root@k8s-master manifests]# kubectl get pod
NAME                  READY   STATUS     RESTARTS   AGE
myapp-pod-init        1/1     Running   0          17s
```

##### 2、生命周期的钩子函数

k8s为容器提供两种生命周期钩子

- **postStart**:容器创建完成之后立即运行
- **preStop**:容器终止操作之前立即运行，同步的方式调用

spec.lifecycle字段中定义

##### 3、容器探测

###### 1、Pod存活性探测

1、ExecAction

exec类型的探针通过在目标容器中执行由用户自定义的命令来判定容器的健康状态，若命令状态返回值为0则表示“成功”通过检测，其他值为“失败”状态。

spec.containers.livenessProbe.exec定义

```yaml
# cat live-exec.yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    test: liveness-exec
  name: liveness-exec
spec:
  containers:
  - name: liveness-exec-demo
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    args: ["/bin/sh","-c"," touch /tmp/healthy; sleep 60;rm -rf /tmp/healthy; sleep 600"]
    livenessProbe:
      exec:
        command: ["test","-e","/tmp/healthy"]
```

2、HTTPGetAction

基于HTTP的探测向目标容器发起一个HTTP请求，根据其响应码进行结果判定，响应码形如2XX或3XX时表示检测通过。

spec.containers.livenessProbe.httpGet字段来定义

```yaml
# cat live-http.yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    test: liveness
  name: liveness-http
spec:
  containers:
  - name: liveness-http-demo
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    ports:
    - name: http
      containerPort: 80
    lifecycle:
      postStart:
        exec:
          command: ["/bin/sh","-c"," echo Healthy > /usr/share/nginx/html/healthz"]
    livenessProbe:
      httpGet:
        path: /healthz
        port: http
        scheme: HTTP
```

删除测试页面/healthz，查看状态信息

```shell
[root@k8s-master livenessprobe]# kubectl exec liveness-http rm /usr/share/nginx/html/healthz
[root@k8s-master livenessprobe]# kubectl describe pods/liveness-http
...
    Ready:          True
    Restart Count:  1
    Liveness:       http-get http://:http/healthz delay=0s timeout=1s period=10s #success=1 #failure=3
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-n8tvj (ro)
Conditions:
  Type              Status
  Initialized       True
  Ready             True
  ContainersReady   True
  PodScheduled      True
Volumes:
  default-token-n8tvj:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  default-token-n8tvj
    Optional:    false
QoS Class:       BestEffort
Node-Selectors:  <none>
Tolerations:     node.kubernetes.io/not-ready:NoExecute for 300s
                 node.kubernetes.io/unreachable:NoExecute for 300s
Events:
  Type     Reason     Age                  From                Message
  ----     ------     ----                 ----                -------
  Normal   Scheduled  33m                  default-scheduler   Successfully assigned default/liveness-http to k8s-node1
  Normal   Pulled     107s (x2 over 33m)   kubelet, k8s-node1  Container image "nginx:latest" already present on machine
  Normal   Created    107s (x2 over 33m)   kubelet, k8s-node1  Created container
  Normal   Started    107s (x2 over 33m)   kubelet, k8s-node1  Started container
  Warning  Unhealthy  107s (x3 over 2m7s)  kubelet, k8s-node1  Liveness probe failed: HTTP probe failed with statuscode: 404
  Normal   Killing    107s                 kubelet, k8s-node1  Killing container with id docker://liveness-http-demo:Container failed liveness probe.. Container will be killed and recreated.
```

3、TCPSocketAction

基于TCP的存活性探测用于向容器的特定端口发起TCP请求并尝试建立连接进行结果判定，连接建立成功即为通过检测。

spec.containers.livenessProbe.tcpSocket字段定义

```yaml
# cat live-tcp.yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-tcp
  labels:
    test: liveness
spec:
  containers:
  - name: liveness-tcp-demo
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    ports:
    - name: http
      containerPort: 80
    livenessProbe:
      tcpSocket:
        port: http
```

###### 2、Pod就序性探测

用于探测容器是否已经初始化完成并可服务于客户端请求，探测操作返回“success”转台时，即传递容器已经“就绪”的信号，探测失败时，就绪性探测不会杀死或重启容器以保证其健康性，而是通知其尚未就绪

spec.containers.readinessProbe.exec字段来定义

```yaml
# cat readiness-exec.yaml
apiVersion: v1
kind: Pod
metadata:
  name: readiness-exec
  labels:
    test: readiness
spec:
  containers:
  - name: readiness-demo
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    args: ["/bin/sh","-c","while true; do rm -f /tmp/ready; sleep 30; touch /tmp/ready; sleep 300; done"]
    readinessProbe:
      exec:
        command: ["test","-e","/tmp/ready"]
      initialDelaySeconds: 5
      periodSeconds: 5
# 观察状态变化信息
[root@k8s-master probe]# kubectl get pod -l test=readiness -w
NAME             READY   STATUS    RESTARTS   AGE
readiness-exec   0/1     Running   0          7s
readiness-exec   1/1   Running   0     36s
# kubectl describe pods/readiness-exec
State:          Running
      Started:      Wed, 29 May 2019 09:37:48 +0800
    Ready:          True
    Restart Count:  0
    Readiness:      exec [test -e /tmp/ready] delay=5s timeout=1s period=5s #success=1 #failure=3
```

#### Pod控制器

实现对Pod对象的管理，包括创建、删除及重新调度等操作。

Pod控制器资源通过持续性监控集群中运行着的符合其标签选择器的Pod资源对象来确保它们严格符合用户期望的状态，包含三个基本的组成部分：

标签选择器：匹配并关联Pod资源对象

期望的副本数：期望在集群中精确运行着的Pod资源的对象数量

Pod模板：用于新建Pod资源对象的Pod模板资源

##### 1、ReplicaSet控制器

用于确保由其管控的Pod对象副本数在任意时刻都能精确满足期望的数量

```shell
# cat replicaset-demo.yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: rs-example
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rs-demo
  template:
    metadata:
      labels:
        app: rs-demo
    spec:
      containers:
      - name: myapp
        image: ikubernetes/myapp:v6
        ports:
        - name: http
          containerPort: 80
[root@k8s-master manifests]# kubectl get pod -l app=rs-demo
NAME               READY   STATUS    RESTARTS   AGE
rs-example-rs7r6   1/1     Running   0          3h24m
rs-example-x6qpt   1/1     Running   0          3h24m   
```

删除一个pod

```shell
[root@k8s-master probe]# kubectl delete pods/rs-example-rs7r6
pod "rs-example-rs7r6" deleted
```

查看pod对象的信息，观察到删除一个Pod对象后，自动创建了一个，以确保Pod的数量

```shell
[root@k8s-master manifests]# kubectl get pod -l app=rs-demo -w
NAME               READY   STATUS    RESTARTS   AGE
rs-example-rs7r6   1/1     Running   0          3h26m
rs-example-x6qpt   1/1     Running   0          3h26m
rs-example-rs7r6   1/1   Terminating   0     3h26m
rs-example-5skxx   0/1   Pending   0     0s
rs-example-5skxx   0/1   Pending   0     0s
rs-example-5skxx   0/1   ContainerCreating   0     0s
rs-example-rs7r6   0/1   Terminating   0     3h26m
rs-example-5skxx   1/1   Running   0     2s
rs-example-rs7r6   0/1   Terminating   0     3h26m
rs-example-rs7r6   0/1   Terminating   0     3h26m

[root@k8s-master manifests]# kubectl get pod -l app=rs-demo
NAME               READY   STATUS    RESTARTS   AGE
rs-example-5skxx   1/1     Running   0          2m24s
rs-example-x6qpt   1/1     Running   0          3h29m
```

ReplicaSet控制器能对Pod对象数目的异常及时做出响应，是因为它向APIServer注册监听（watch）了相关资源及其列表的变动信息，于是API Server会在变动发生时立即通知给相关的监听客户端。

**更新ReplicaSet控制器**

1、更改模板：升级应用

**仅影响更改之后由其新建的Pod对象，对已有的副本不会产生作用**，可以手动删除相应的Pod，完成一次更改

接着上面的例子，修改模板中镜像文件的的版本

```yaml
      containers:
      - name: myapp
        image: ikubernetes/myapp:v7
        ports:
```

执行修改操作

```shell
[root@k8s-master manifests]# kubectl apply -f replicaset-demo.yaml
replicaset.apps/rs-example configured
# 查看对现有副本没有影响
[root@k8s-master manifests]# kubectl get pod -l app=rs-demo -o \
 custom-columns=Name:metadata.name,Image:spec.containers[0].image
Name               Image
rs-example-5skxx   ikubernetes/myapp:v6
rs-example-x6qpt   ikubernetes/myapp:v6
# 手动删除一个
[root@k8s-master probe]# kubectl delete pods/rs-example-5skxx
pod "rs-example-5skxx" deleted
# 查看新生成的版本已更新为新的
[root@k8s-master manifests]# kubectl get pod -l app=rs-demo -o custom-columns=Name:metadata.name,Image:spec.containers[0].image
Name               Image
rs-example-wv67g   ikubernetes/myapp:v7
rs-example-x6qpt   ikubernetes/myapp:v6
# 一次性删除所有控制器相关的Pod副本或修改标签，以完成更新升级（不建议使用）
[root@k8s-master manifests]# kubectl delete pods -l app=rs-demo
pod "rs-example-wv67g" deleted
pod "rs-example-x6qpt" deleted
[root@k8s-master manifests]# kubectl get pod -l app=rs-demo -o custom-columns=Name:metadata.name,Image:spec.containers[0].image
Name               Image
rs-example-28mbs   ikubernetes/myapp:v7
rs-example-lrxdf   ikubernetes/myapp:v7
```

2、扩容和缩容

改变Pod副本数量，**控制会做出实时响应**

可以通过修改yaml清单文件方式，也可命令行“--replicas”选项进行

```shell
[root@k8s-master manifests]# kubectl get replicasets rs-example
NAME         DESIRED   CURRENT   READY   AGE
rs-example   2         2         2       5h35m
[root@k8s-master manifests]# kubectl scale replicasets rs-example --replicas=3
replicaset.extensions/rs-example scaled
[root@k8s-master manifests]# kubectl get pod -l app=rs-demo
NAME               READY   STATUS    RESTARTS   AGE
rs-example-28mbs   1/1     Running   0          5m32s
rs-example-586p4   1/1     Running   0          13s
rs-example-lrxdf   1/1     Running   0          5m32s
[root@k8s-master manifests]# kubectl get replicasets rs-example
NAME         DESIRED   CURRENT   READY   AGE
rs-example   3         3         3       5h36m
```

3、删除ReplicaSet控制器资源

使用kubectl delete命令删除ReplicaSet对象时*默认会一并删除其管控的各Pod对象*，可以通过“–-cascade=false”选项，取消级联，Pod对象不会被删除，仍处于活动状态，由用户自行管理

```shell
[root@k8s-master manifests]# kubectl delete replicasets rs-example --cascade=false
replicaset.extensions "rs-example" deleted
[root@k8s-master manifests]# kubectl get pod -l app=rs-demo
NAME               READY   STATUS    RESTARTS   AGE
rs-example-28mbs   1/1     Running   0          10m
rs-example-586p4   1/1     Running   0          4m46s
rs-example-lrxdf   1/1     Running   0          10m
```

##### 2、Deployment控制器

构建于ReplicaSet控制器之上，可为Pod和ReplicaSet资源提供声明式更新

相对于ReplicaSet增加了部分特性：

- 事件和状态查看
- 回滚
- 版本记录：对Deployment对象的每一次操作都保存，为后续回滚操使用
- 暂停和启动：对每次升级，都能随时暂停和启动
- 多种自动更新方案：一是Recreate，即重建更新机制，全面停止、删除旧有的Pod后用新版本替代；另一个是Rolling Update，即滚动升级机制，逐步替换旧有的Pod至新的版本

**创建**

```yaml
# cat deployment-demo.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deploy
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp-deploy-demo
        image: ikubernetes/myapp:v6
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
          name: http
```

```shell
[root@k8s-master manifests]# kubectl apply -f deployment-demo.yaml
deployment.apps/myapp-deploy created

[root@k8s-master manifests]# kubectl get deployments myapp-deploy
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
myapp-deploy   2/2     2            2           96s

[root@k8s-master manifests]# kubectl get pod -l app=myapp
NAME                           READY   STATUS    RESTARTS   AGE
myapp-deploy-8bcf678d7-hxfk7   1/1     Running   0          2m8s
myapp-deploy-8bcf678d7-mt59x   1/1     Running   0          2m8s
```

**更新策略**

Deployment控制器详细信息中包含了其更新策略的相关配置信息

```shell
[root@k8s-master manifests]# kubectl describe deployments myapp-deploy
Name:                   myapp-deploy
Namespace:              default
....
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
...
OldReplicaSets:  <none>
NewReplicaSet:   myapp-deploy-8bcf678d7 (2/2 replicas created)
```

Deployment控制器支持两种更新策略：

- 滚动更新（rolling update）

  在删除一部分旧版本Pod资源的同时，补充创建一部分新版本的Pod对象进行升级，优势是升级期间，服务不会中断，但不同客户端得到的响应内容版本不同

- 重新创建（recreate）

  首先删除现有的Pod对象，而后由控制器基于新模板重新创建出新版本资源对象

**升级和回滚Deployment**

修改Pod模板相关的配置参数就可以完成资源的更新，可以使用apply和patch命令来进行

为了便于观测升级过程，事先修改下等待时长

```shell
# -p 后跟json格式的参数
[root@k8s-master manifests]# kubectl patch deployments myapp-deploy -p '{"spec": {"minReadySeconds": 5}}'
deployment.extensions/myapp-deploy patched
```

更新Pod模板中的镜像版本

```shell
[root@k8s-master manifests]# kubectl set image deployments myapp-deploy myapp-deploy-demo=ikubernetes/myapp:v7
deployment.extensions/myapp-deploy image updated
```

观测其升级过程

```shell
[root@k8s-master manifests]# kubectl get deployments myapp-deploy -w
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
myapp-deploy   2/2     2            2           33m
myapp-deploy   2/2   2     2     33m
myapp-deploy   2/2   2     2     33m
myapp-deploy   2/2   0     2     33m
myapp-deploy   2/2   1     2     33m
myapp-deploy   3/2   1     2     33m
myapp-deploy   3/2   1     3     33m
myapp-deploy   2/2   1     2     33m
myapp-deploy   2/2   2     2     33m
myapp-deploy   3/2   2     2     33m
myapp-deploy   3/2   2     3     33m
myapp-deploy   2/2   2     2     33m

# 升级完成
[root@k8s-master probe]# kubectl get pod -l app=myapp -o custom-columns=Name:metadata.name,Image:spec.containers[0].image
Name                            Image
myapp-deploy-7fb759dbf8-49dsn   ikubernetes/myapp:v7
myapp-deploy-7fb759dbf8-6nvcq   ikubernetes/myapp:v7
```

回滚操作

```shell
[root@k8s-master probe]# kubectl rollout undo deployments myapp-deploy
deployment.extensions/myapp-deploy rolled back

[root@k8s-master probe]# kubectl get pod -l app=myapp -o custom-columns=Name:metadata.name,Image:spec.containers[0].image
Name                           Image
myapp-deploy-8bcf678d7-bv9lm   ikubernetes/myapp:v6
myapp-deploy-8bcf678d7-w8942   ikubernetes/myapp:v6

# 查看回滚历史记录
[root@k8s-master probe]# kubectl rollout history deployments myapp-deploy
deployment.extensions/myapp-deploy

```

**扩容和缩容**

通过修改yaml文件中的spec.replicas即可修改副本数量，也可以通过kubectl edit修改

##### 3、DaemonSet控制器

用于在集群中的全部节点上同时运行一份指定的Pod资源副本，后续加入集群的工作节点也会自动创建一个相关的Pod对象，当从集群中移除节点时，此类Pod对象也将被自动回收而无须重建。

集群中有多少个node节点，就建立多少个pod对象

```yaml
# cat daemonset-demo.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: myapp-ds
  labels:
    app: myapp-ds
spec:
  selector:
    matchLabels:
      app: myapp-ds
  template:
    metadata:
      labels:
        app: myapp-ds
      name: myapp-ds
    spec:
      containers:
      - name: myapp
        image: ikubernetes/myapp:v6
        imagePullPolicy: IfNotPresent
        env:
        - name: DAEMONSET
          value: myapp-daemonset
          
[root@k8s-master manifests]# kubectl get pod -l app=myapp-ds
NAME             READY   STATUS    RESTARTS   AGE
myapp-ds-67zlj   1/1     Running   0          110s
myapp-ds-tvgfr   1/1     Running   0          110s
```

查看资源描述

```shell
# kubectl describe ds
Name:           myapp-ds
Selector:       app=myapp-ds
Node-Selector:  <none>
Labels:         app=myapp-ds
Annotations:    deprecated.daemonset.template.generation: 1
                kubectl.kubernetes.io/last-applied-configuration:
                  {"apiVersion":"apps/v1","kind":"DaemonSet","metadata":{"annotations":{},"labels":{"app":"myapp-ds"},"name":"myapp-ds","namespace":"default...
Desired Number of Nodes Scheduled: 2
Current Number of Nodes Scheduled: 2
Number of Nodes Scheduled with Up-to-date Pods: 2
Number of Nodes Scheduled with Available Pods: 2
Number of Nodes Misscheduled: 0
Pods Status:  2 Running / 0 Waiting / 0 Succeeded / 0 Failed
Pod Template:
  Labels:  app=myapp-ds
  Containers:
   myapp:
    Image:      ikubernetes/myapp:v6
    Port:       <none>
    Host Port:  <none>
    Environment:
      DAEMONSET:  myapp-daemonset
    Mounts:       <none>
  Volumes:        <none>
```

更新对象

支持RollingUpdate（滚动更新）和OnDelete（删除时更新）两种更新策略

```shell
[root@k8s-master ~]# kubectl set image daemonsets myapp-ds myapp=ikubernetes/myapp:v7
daemonset.extensions/myapp-ds image updated
[root@k8s-master manifests]# kubectl get pod -l app=myapp-ds -w
NAME             READY   STATUS    RESTARTS   AGE
myapp-ds-67zlj   1/1     Running   0          2m48s
myapp-ds-tvgfr   1/1     Running   0          2m48s
myapp-ds-67zlj   1/1   Terminating   0     3m6s
myapp-ds-67zlj   0/1   Terminating   0     3m7s
myapp-ds-67zlj   0/1   Terminating   0     3m8s
myapp-ds-67zlj   0/1   Terminating   0     3m8s
myapp-ds-fnfdz   0/1   Pending   0     0s
myapp-ds-fnfdz   0/1   Pending   0     0s
myapp-ds-fnfdz   0/1   ContainerCreating   0     0s
myapp-ds-fnfdz   1/1   Running   0     2s
myapp-ds-tvgfr   1/1   Terminating   0     3m10s
myapp-ds-tvgfr   0/1   Terminating   0     3m11s
myapp-ds-tvgfr   0/1   Terminating   0     3m12s
myapp-ds-tvgfr   0/1   Terminating   0     3m12s
myapp-ds-8j7v6   0/1   Pending   0     0s
myapp-ds-8j7v6   0/1   Pending   0     0s
myapp-ds-8j7v6   0/1   ContainerCreating   0     0s
myapp-ds-8j7v6   1/1   Running   0     3s
```
#### Service资源

用于为受控于控制器资源的Pod对象提供一个固定、统一的访问接口及负载均衡的能力

通过规则定义出多个Pod对象组合而成的逻辑集合，以及访问这组Pod的策略，Service关联Pod资源的规则要借助于标签选择器来完成

基于标签选择器将一组Pod定义成一个逻辑组合，并通过自己的IP地址和端口调度代理请求至组内的Pod对象之上，向客户端隐藏了真实的、处理用户请求的Pod资源，使得客户端的请求看上去就像是由Service直接处理并进行响应的一样。

工作模式：

- userspace
- iptables
- ipvs

*创建实例*

```yaml
# cat service-demo.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-svc-demo
spec:
  selector:
    app: myapp
  ports:
  - name: http
    port: 80
    targetPort: 80
    protocol: TCP
```

关联集群中存在标签为app=myapp的Pod资源，将其作为此Service对象的后端Endpoint对象，并负责接收响应的请求流量。

*查看*

```shell
# 查看创建的Service，类型为默认的ClusterIP
[root@k8s-master manifests]# kubectl get svc/myapp-svc-demo
NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
myapp-svc-demo   ClusterIP   10.101.220.50   <none>        80/TCP    10m

# 查看endpoints
[root@k8s-master manifests]# kubectl get endpoints myapp-svc-demo
NAME             ENDPOINTS                         AGE
myapp-svc-demo   10.244.1.126:80,10.244.2.123:80   15m

# 关联的pod
[root@k8s-master manifests]# kubectl get pods -o wide
NAME                            READY   STATUS    RESTARTS   AGE     IP             NODE        NOMINATED NODE   READINESS GATES
myapp-deploy-7fb759dbf8-b9ptc   1/1     Running   3          2d18h   10.244.1.126   k8s-node1   <none>           <none>
myapp-deploy-7fb759dbf8-s7tlq   1/1     Running   3          2d18h   10.244.2.123   k8s-node2   <none>           <none>
```

*向Service对象发起请求*

```shell
[root@k8s-master manifests]# for i in {1..10};do curl 10.101.220.50/hostname.html;sleep 0.5;done
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-s7tlq
myapp-deploy-7fb759dbf8-s7tlq
myapp-deploy-7fb759dbf8-s7tlq
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-s7tlq
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-b9ptc
```

*设置Serivce会话粘性SessionAffinity*

**格式**：

```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: <integer>
```

命令行

```shell
[root@k8s-master ~]# kubectl patch services myapp-svc-demo -p '{"spec": {"sessionAffinity": "ClientIP"}}'
service/myapp-svc-demo patched
```

查看效果：

```shell
[root@k8s-master manifests]# for i in {1..20};do curl 10.101.220.50/hostname.html;sleep 1;done
myapp-deploy-7fb759dbf8-s7tlq
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-s7tlq
myapp-deploy-7fb759dbf8-s7tlq
myapp-deploy-7fb759dbf8-s7tlq
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-s7tlq
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-s7tlq
myapp-deploy-7fb759dbf8-s7tlq
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-b9ptc
myapp-deploy-7fb759dbf8-b9ptc
```

##### Service类型

###### 1、ClusterIP

默认类型，通过集群内部IP地址暴露服务，此地址仅在集群内部可达，而无法被集群外部的客户端访问

###### 2、NodePort

这种类型建立在ClusterIP类型之上，其在每个节点的IP地址的某静态端口(NodePort)暴露服务，会为Service分配集群IP地址，并将此作为NodePort的路由目标。

NodePort类型在工作节点的IP地址上选择一个端口用于将集群外部的用户请求转发至目标Service的ClusterIP和Port。

```yaml
# cat service-nodeport.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-svc-nodeport
spec:
  type: NodePort
  selector:
    app: myapp
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 80
    nodePort: 32080
```

```shell
[root@k8s-master manifests]# kubectl get svc myapp-svc-nodeport
NAME                 TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
myapp-svc-nodeport   NodePort   10.108.229.37   <none>        80:32080/TCP   25s
```

可以通过节点IP:nodePort访问服务

```shell
[root@k8s-master manifests]# curl 192.168.47.141:32080/hostname.html
myapp-deploy-7fb759dbf8-b9ptc
[root@k8s-master manifests]# curl 192.168.47.141:32080/hostname.html
myapp-deploy-7fb759dbf8-s7tlq
```

###### 3、LoadBalancer

建构在NodePort类型之上，其通过cloud provider提供的负载均衡器将服务暴露到集群外部

###### 4、ExternalName

通过将Service映射至由externalName字段的内容指定的主机名来暴露服务，此主机名需被DNS服务解析至CNAME类型的记录。

##### Headless类型

headless对象没有ClusterIP

- 具有标签选择器

  端点控制器会在API中为其创建Endpoints记录，并将ClusterDNS服务中的A记录直接解析到此Service后端的各Pod对象的IP地址上。

- 没有标签选择器

  端点控制器不会在API中为其创建Endpoints记录

```yaml
# 拥有标签选择器
# cat service-headless.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-svc-headless
spec:
  clusterIP: None
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 80
    name: http
```

```shell
[root@k8s-master manifests]# kubectl get svc myapp-svc-headless
NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
myapp-svc-headless   ClusterIP   None         <none>        80/TCP    12s

[root@k8s-master manifests]# kubectl describe svc myapp-svc-headless
Name:              myapp-svc-headless
Namespace:         default
Labels:            <none>
Annotations:       kubectl.kubernetes.io/last-applied-configuration:
                     {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"name":"myapp-svc-headless","namespace":"default"},"spec":{"clusterIP":"N...
Selector:          app=myapp
Type:              ClusterIP
IP:                None
Port:              http  80/TCP
TargetPort:        80/TCP
Endpoints:         10.244.1.126:80,10.244.2.123:80
Session Affinity:  None
Events:            <none>
```

资源发现

DNS解析记录

```shell
[root@k8s-master ~]# kubectl exec -it myapp-deploy-7fb759dbf8-b9ptc -- /bin/sh
/ # nslookup myapp-svc-headless
nslookup: can't resolve '(null)': Name does not resolve

Name:      myapp-svc-headless
Address 1: 10.244.1.126 myapp-deploy-7fb759dbf8-b9ptc
Address 2: 10.244.2.123 10-244-2-123.myapp-svc.default.svc.cluster.local
```

##### 实例

**通过配置清单文件创建**

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

**通过命令行进行创建**

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
```

##### 部署Ingress

Ingress本质是通过http代理服务器将外部的http请求转发到集群内部的后端服务

Ingress由两部分组成：Ingress Controller 和 Ingress 服务。

Ingress Contronler 通过与 Kubernetes API 交互，动态的去感知集群中 Ingress 规则变化，然后读取它，按照自定义的规则，规则就是写明了哪个域名对应哪个service，生成一段 Nginx 配置，再写到 Nginx-ingress-control的 Pod 里，这个 Ingress Contronler 的pod里面运行着一个nginx服务，控制器会把生成的nginx配置写入/etc/nginx.conf文件中，然后 reload 一下 使用配置生效。以此来达到域名分配置及动态更新的问题。

ingress，基于DNS名称或URL路径把请求转发至指定的Service资源的规则，用于将集群外部的请求流量转发至集群内部完成服务发布。ingress规则需要由一个Service资源对象辅助识别相关的所有Pod对象，规则生成后，ingress-nginx控制器可经由规则的定义，直接将请求流量调度至相关Pod，无须经由Service对象API的再次转发。

**参考**

> https://kubernetes.github.io/ingress-nginx/deploy/
>
> https://github.com/kubernetes/ingress-nginx/tree/master/deploy

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

```yaml
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

```yaml
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
```
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

	server {
		server_name myapp.example.com ;

	listen 80;

	set $proxy_upstream_name "-";

	listen 443  ssl http2;

# PEM sha: cb5ed13051761519240a5abe36b5fa7677b239ca

	ssl_certificate                         /etc/ingress-controller/ssl/default-fake-certificate.pem;
	ssl_certificate_key                     /etc/ingress-controller/ssl/default-fake-certificate.pem;
```

浏览器访问https://myapp.example.com:30443

##### 使用Ingress发布Tomcat

1、创建名称空间

```shell
[root@k8s-master tomcat]# kubectl create namespace test
```

2、创建部署tomcat实例的deployment控制器

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tomcat-deploy
  namespace: test
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tomcat
  template:
    metadata:
      labels:
        app: tomcat
    spec:
      containers:
      - name: tomcat
        image: tomcat:9.0.20-jre8-alpine
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
          name: httpport
        - containerPort: 8009
          name: aipport
```

运行创建命令并查看

```shell
[root@k8s-master tomcat]# kubectl apply -f tomcat-deploy.yaml

[root@k8s-master tomcat]# kubectl get pod -n test
NAME                            READY   STATUS    RESTARTS   AGE
tomcat-deploy-d4b654786-bwc7n   1/1     Running   1          24h
tomcat-deploy-d4b654786-qnfc8   1/1     Running   1          24h
```

3、创建后端Pod的service资源

```yaml
apiVersion: v1
kind: Service
metadata:
  namespace: test
  name: tomcat-svc
  labels:
    app: tomcat-svc
spec:
  selector:
    app: tomcat
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  - name: ajp
    port: 89
    targetPort: 8009
    protocol: TCP
```

运行创建命令并查看

```shell
[root@k8s-master tomcat]# kubectl apply -f tomcat-deploy-svc.yaml

[root@k8s-master tomcat]# kubectl get svc -n test
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)         AGE
tomcat-svc   ClusterIP   10.100.125.53   <none>        80/TCP,89/TCP   24h
```

4、创建Ingress资源

```yaml
[root@k8s-master tomcat]# cat tomcat-ingress.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  namespace: test
  name: tomcat-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  backend:
    serviceName: default-svc
    servicePort: 80
  rules:
  - host: tomcat.example.io
    http:
      paths:
      - backend:
          serviceName: tomcat-svc
          servicePort: 80
```

运行创建命令并查看

```shell
[root@k8s-master tomcat]# kubectl apply -f tomcat-ingress.yaml

[root@k8s-master tomcat]# kubectl get ingress -n test
NAME                HOSTS               ADDRESS   PORTS   AGE
tomcat-ingress      tomcat.example.io             80      23h
```

浏览器访问[tomcat.example.io:30080]()可以访问

5、配置TLS Ingress资源，实现https

生成测试用的私钥和自签证书

```shell
[root@k8s-master tomcat]# openssl genrsa -out tls.key 2048
Generating RSA private key, 2048 bit long modulus
......................................+++
..............+++
e is 65537 (0x10001)

[root@k8s-master tomcat]# openssl req -new -x509 -key tls.key -out tls.crt -days 3650
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [XX]:CN
State or Province Name (full name) []:GD
Locality Name (eg, city) [Default City]:DG
Organization Name (eg, company) [Default Company Ltd]:XL
Organizational Unit Name (eg, section) []:
Common Name (eg, your name or your server's hostname) []:tomcat.example.io
Email Address []:admin@admin.io
```

创建Secret资源

```shell
[root@k8s-master tomcat]# kubectl create secret tls tomcat-ingress-secret --cert=tls.crt --key=tls.key -n test
secret/tomcat-ingress-secret created

[root@k8s-master tomcat]# kubectl get secret -n test
NAME                    TYPE                                  DATA   AGE
tomcat-ingress-secret   kubernetes.io/tls                     2      13s

[root@k8s-master tomcat]# kubectl describe secrets tomcat-ingress-secret -n test
Name:         tomcat-ingress-secret
Namespace:    test
Labels:       <none>
Annotations:  <none>

Type:  kubernetes.io/tls

Data
====
tls.crt:  1342 bytes
tls.key:  1679 bytes
```

在ingress资源清单中使用secret资源

```shell
[root@k8s-master tomcat]# cat tomcat-ingress-tls.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  namespace: test
  name: tomcat-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  tls:
  - hosts:
    - tomcat.example.io
    secretName: tomcat-ingress-secret
  rules:
  - host: tomcat.example.io
    http:
      paths:
      - backend:
          serviceName: tomcat-svc
          servicePort: 80

# 运行资源创建命令
[root@k8s-master tomcat]# kubectl apply -f tomcat-ingress-tls.yaml
```

可以通过https://tomcat.example.io:30443/访问tomcat应用

#### 访问控制

APIServer作为Kubernetes集群系统的网关，是访问及管理资源对象的唯一入口，其它所有需要访问集群资源的组件及使用的kubectl命令等都要经由此网关进行集群访问和管理。这些客户端均要经由API Server访问或改变集群状态并完成数据存储，并由它对每一次的访问请求进行合法性检验，包括用户身份鉴别、操作权限验证以及操作是否符合全局规范的约束。所有检查均正常完成且对象配置信息合法性检验无误之后才能访问或存入数据于后端存储系统etcd中。

API Server处理请求的过程中，认证插件负责鉴定用户身份，授权插件用于操作权限许可鉴别，准入控制则用于在资源对象的创建、删除、更新或连接操作时实现更精细的许可检查。

##### 通过URL访问系统资源对象

启动proxy

```shell
[root@k8s-master ~]# kubectl proxy --port=8080
Starting to serve on 127.0.0.1:8080
```

通过URL访问

查看链接

```shell
[root@k8s-master ~]# kubectl get deploy -o yaml | grep selfLink
    selfLink: /apis/extensions/v1beta1/namespaces/default/deployments/myapp-deploy
```

```shell
[root@k8s-master ~]# curl localhost:8080/api/v1/namespaces
{
  "kind": "NamespaceList",
  "apiVersion": "v1",
  "metadata": {
    "selfLink": "/api/v1/namespaces",
    "resourceVersion": "516313"
  },
  "items": [
    {
      "metadata": {
        "name": "default",
        "selfLink": "/api/v1/namespaces/default",
        "uid": "3d0aa41c-4be3-11e9-b569-000c299777e4",
        "resourceVersion": "11",
        "creationTimestamp": "2019-03-21T14:11:36Z"
      },
      "spec": {
        "finalizers": [
          "kubernetes"
        ]
      },
      "status": {
        "phase": "Active"
      }
    },
    {
      "metadata": {
        "name": "ingress-nginx",
        "selfLink": "/api/v1/namespaces/ingress-nginx",
        "uid": "14ee50e2-8792-11e9-af58-000c299777e4",
        "resourceVersion": "29223",
        "creationTimestamp": "2019-06-05T13:01:49Z",
        "labels": {
          "app.kubernetes.io/name": "ingress-nginx",
          "app.kubernetes.io/part-of": "ingress-nginx"
        },
        "annotations": {
          "kubectl.kubernetes.io/last-applied-configuration": "{\"apiVersion\":\"v1\",\"kind\":\"Namespace\",\"metadata\":{\"annotations\":{},\"labels\":{\"app.kubernetes.io/name\":\"ingress-nginx\",\"app.kubernetes.io/part-of\":\"ingress-nginx\"},\"name\":\"ingress-nginx\"}}\n"
        }
      },
      "spec": {
        "finalizers": [
          "kubernetes"
        ]
      },
      "status": {
        "phase": "Active"
      }
    },
    {
      "metadata": {
        "name": "kube-public",
        "selfLink": "/api/v1/namespaces/kube-public",
        "uid": "3d269f0c-4be3-11e9-b569-000c299777e4",
        "resourceVersion": "46",
        "creationTimestamp": "2019-03-21T14:11:36Z"
      },
      "spec": {
        "finalizers": [
          "kubernetes"
        ]
      },
      "status": {
        "phase": "Active"
      }
    },
    {
      "metadata": {
        "name": "kube-system",
        "selfLink": "/api/v1/namespaces/kube-system",
        "uid": "3d24e967-4be3-11e9-b569-000c299777e4",
        "resourceVersion": "43",
        "creationTimestamp": "2019-03-21T14:11:36Z"
      },
      "spec": {
        "finalizers": [
          "kubernetes"
        ]
      },
      "status": {
        "phase": "Active"
      }
    },
    {
      "metadata": {
        "name": "test",
        "selfLink": "/api/v1/namespaces/test",
        "uid": "bd68601c-8a58-11e9-94f9-000c299777e4",
        "resourceVersion": "129031",
        "creationTimestamp": "2019-06-09T01:48:55Z"
      },
      "spec": {
        "finalizers": [
          "kubernetes"
        ]
      },
      "status": {
        "phase": "Active"
      }
    }
  ]
}
```

查看指定名称空间的deployments控制器

```shell
[root@k8s-master ~]# curl localhost:8080/apis/apps/v1/namespaces/default/deployments
{
  "kind": "DeploymentList",
  "apiVersion": "apps/v1",
  "metadata": {
    "selfLink": "/apis/apps/v1/namespaces/default/deployments",
    "resourceVersion": "516712"
  },
  "items": [
    {
      "metadata": {
        "name": "myapp-deploy",
        "namespace": "default",
        "selfLink": "/apis/apps/v1/namespaces/default/deployments/myapp-deploy",
        "uid": "f71800e4-8788-11e9-a2ff-000c299777e4",
        "resourceVersion": "515429",
        "generation": 5,
        "creationTimestamp": "2019-06-05T11:56:34Z",
        "labels": {
          "app": "myapp"
        },
        "annotations": {
          "deployment.kubernetes.io/revision": "3",
          "kubectl.kubernetes.io/last-applied-configuration": "{\"apiVersion\":\"apps/v1\",\"kind\":\"Deployment\",\"metadata\":{\"annotations\":{},\"name\":\"myapp-deploy\",\"namespace\":\"default\"},\"spec\":{\"replicas\":2,\"selector\":{\"matchLabels\":{\"app\":\"myapp\"}},\"template\":{\"metadata\":{\"labels\":{\"app\":\"myapp\"}},\"spec\":{\"containers\":[{\"image\":\"ikubernetes/myapp:v6\",\"imagePullPolicy\":\"IfNotPresent\",\"name\":\"myapp-deploy-demo\",\"ports\":[{\"containerPort\":80,\"name\":\"http\"}]}]}}}}\n"
        }
      },
      "spec": {
        "replicas": 2,
        "selector": {
          "matchLabels": {
            "app": "myapp"
          }
        },
        "template": {
          "metadata": {
            "creationTimestamp": null,
            "labels": {
              "app": "myapp"
            }
          },
          "spec": {
            "containers": [
              {
                "name": "myapp-deploy-demo",
                "image": "ikubernetes/myapp:v6",
                "ports": [
                  {
                    "name": "http",
                    "containerPort": 80,
                    "protocol": "TCP"
                  }
                ],
                "resources": {

                },
                "terminationMessagePath": "/dev/termination-log",
                "terminationMessagePolicy": "File",
                "imagePullPolicy": "IfNotPresent"
              }
            ],
            "restartPolicy": "Always",
            "terminationGracePeriodSeconds": 30,
            "dnsPolicy": "ClusterFirst",
            "securityContext": {

            },
            "schedulerName": "default-scheduler"
          }
        },
        "strategy": {
          "type": "RollingUpdate",
          "rollingUpdate": {
            "maxUnavailable": "25%",
            "maxSurge": "25%"
          }
        },
        "revisionHistoryLimit": 10,
        "progressDeadlineSeconds": 600
      },
      "status": {
        "observedGeneration": 5,
        "replicas": 2,
        "updatedReplicas": 2,
        "readyReplicas": 2,
        "availableReplicas": 2,
        "conditions": [
          {
            "type": "Progressing",
            "status": "True",
            "lastUpdateTime": "2019-06-09T01:36:32Z",
            "lastTransitionTime": "2019-06-05T11:57:08Z",
            "reason": "NewReplicaSetAvailable",
            "message": "ReplicaSet \"myapp-deploy-8bcf678d7\" has successfully progressed."
          },
          {
            "type": "Available",
            "status": "True",
            "lastUpdateTime": "2019-06-16T02:10:45Z",
            "lastTransitionTime": "2019-06-16T02:10:45Z",
            "reason": "MinimumReplicasAvailable",
            "message": "Deployment has minimum availability."
          }
        ]
      }
    }
  ]
}
```

http request verb:  get post put delete

api requests verb:  get list create update patch watch proxy redirect delete deletecollection

resourse: 

subresource

namespace

api group

##### 服务账户

服务账户是用于让Pod对象内的容器进程访问其它服务时提供身份认证信息的账户，一个Service Account资源一般由用户名及相关的secret对象组成。

创建的每个容器中都自动关联了一个存储卷，并由其容器挂载至/var/run/secrets/kubernetes.io/serviceaccount目录下

```shell
/run/secrets/kubernetes.io/serviceaccount # pwd
/var/run/secrets/kubernetes.io/serviceaccount
/run/secrets/kubernetes.io/serviceaccount # ls
ca.crt     namespace  token
```

挂载点目录中通常存在三个文件：ca.crt、namespace、token，其中token文件保存快乐Service Account的认证token，容器中的进程使用它向API Server发起连接请求，进而由认证插件完成用户认证并将其用户名传递给授权插件。

每个Pod对象都只有一个服务账户，若创建Pod资源时未予以明确指定，则名为ServiceAccount的准入控制器会为其自动附加当前名称空间默认的服务账户，其名称为default。

```shell
[root@k8s-master manifests]# kubectl describe serviceaccounts default
Name:                default
Namespace:           default
Labels:              <none>
Annotations:         <none>
Image pull secrets:  <none>
Mountable secrets:   default-token-n8tvj
Tokens:              default-token-n8tvj
Events:              <none>
```

kubernetes系统通过三个独立的组件的相互协作来实现服务账户的自动化，三个组件为：Service Account准入控制器、令牌控制器（token controller）和Service Account账户控制器

- Service Account控制器负责为名称空间管理相应的资源，并确保每个名称空间中都存在一个名为“default”的Service Account对象
- Service Account准入控制器是API Server的一部分，负责在创建或更新Pod时对其按需进行Service Account对象相关信息的修改
- 令牌控制器是controller-manager的子组件，工作于异步模式。负责监控Service Acount的相关操作，监控Secret对象的添加和删除操作

###### 1、创建服务账户

```shell
[root@k8s-master ~]# kubectl create serviceaccount admin
serviceaccount/admin created

[root@k8s-master ~]# kubectl get sa  admin -o yaml
apiVersion: v1
kind: ServiceAccount
metadata:
...
  name: admin
  namespace: default
  resourceVersion: "518757"
  selfLink: /api/v1/namespaces/default/serviceaccounts/admin
...
secrets:
- name: admin-token-qgrgq
```

通过资源配置文件创建

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin
  namespace: default
```

自动生成一个token

```shell
[root@k8s-master ~]# kubectl get secret
NAME                  TYPE                                  DATA   AGE
default-token-n8tvj   kubernetes.io/service-account-token   3      88d
sa-demo-token-52rw6   kubernetes.io/service-account-token   3      18h

```

###### **2、pod资源引用服务账户**

pod.spec.serviceAccountName中指定

```yaml
# cat pod-serviceaccount-demo.yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-serviceaccount
spec:
  serviceAccountName: admin
  containers:
  - name: myapp-sa
    image: ikubernetes/myapp:v6
    imagePullPolicy: IfNotPresent
    ports:
    - name: httpport
      containerPort: 80

```

##### kubeconfig

客户端配置文件

主要组成：

- clusters：集群列表，包含访问API Server的URL和所属集群的名称等
- users：用户列表，包含访问API Server时的用户名和认证信息
- contexts：kubelet的可用上下文列表，由用户列表中的某特定用户名称和集群列表中的某特定集群名称组合而成
- current-context：kubelet当前使用的上下文名称，即上下文列表中的某个特定项。

```yaml
# kubectl config view
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: DATA+OMITTED
    server: https://192.168.47.141:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: kubernetes-admin
  name: kubernetes-admin@kubernetes
current-context: kubernetes-admin@kubernetes
kind: Config
preferences: {}
users:
- name: kubernetes-admin
  user:
    client-certificate-data: REDACTED
    client-key-data: REDACTED

```

kubeadm部署的kubernetes集群默认提供了拥有集群管理权限的kubeconfig配置文件/etc/kubernetes/admin.conf，可以copy到任何拥有kubelet的主机上用于管理整个集群。

自定义用户账号，以授予非管理员级的集群资源使用权限：一是为用户创建专用私钥及证书文件，

二是将其配置于某kubeconfig文件中。

**实现过程**：

一、为目标用户创建私钥及证书文件，保存在/etc/kubernetes/pki目录中

1、生成私钥文件

```shell
[root@k8s-master pki]# pwd
/etc/kubernetes/pki
[root@k8s-master pki]# (umask 077;openssl genrsa -out kube-user1.key 2048)
Generating RSA private key, 2048 bit long modulus
...............................................+++
......+++
e is 65537 (0x10001

```

2、创建证书签署请求，-subj选项中CN的值将被kubeconfig作为用户名使用，O的值将被识别为用户组

```shell
[root@k8s-master pki]# openssl req -new -key kube-user1.key -out kube-user1.csr -subj "/CN=kube-user1/O=kubernetes"

```

3、使用部署kubernetes集群生成的CA签署证书

```shell
[root@k8s-master pki]# openssl x509 -req -in kube-user1.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out kube-user1.crt -days 3650
Signature ok
subject=/CN=kube-user1/O=kubernetes
Getting CA Private Key

```

查看证书信息

```shell
[root@k8s-master pki]# openssl x509 -in kube-user1.crt -noout -text
Certificate:
    Data:
        Version: 1 (0x0)
        Serial Number:
            b6:d4:98:23:d6:d6:91:3a
    Signature Algorithm: sha256WithRSAEncryption
        Issuer: CN=kubernetes
        Validity
            Not Before: Jun 16 07:24:16 2019 GMT
            Not After : Jun 13 07:24:16 2029 GMT
        Subject: CN=kube-user1, O=kubernetes
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                Public-Key: (2048 bit)
                Modulus:
                    00:a8:97:37:eb:24:5a:58:86:f0:ce:e4:67:f5:e6:
                    ...

```

二、为kube-user1生成设定kubeconfig配置文件。

1、配置集群信息，抱哈集群名称、APIServerURL和CA证书，部署集群时已生成，可跳过此步

2、配置客户端证书及密钥，用户名通过证书中Subject的CN值中自动提取。

```shell
[root@k8s-master pki]# kubectl config set-credentials kube-user1 --embed-certs=true --client-certificate=/etc/kubernetes/pki/kube-user1.crt --client-key=/etc/kubernetes/pki/kube-user1.key
User "kube-user1" set.

```

3、配置context，用来组合cluster和credentials，即访问的集群的上下文，多个环境上下文，可用use-context来进行切换

```shell
[root@k8s-master pki]# kubectl config set-context kube-user1@kubernetes --cluster=kubernetes --user=kube-user1
Context "kube-user1@kubernetes" created.

```

4、指定要使用的上下文context，切换为以kube-user1访问集群

```shell
[root@k8s-master pki]# kubectl config use-context kube-user1@kubernetes
Switched to context "kube-user1@kubernetes".

```

5、测试

访问集群资源

```shell
[root@k8s-master pki]# kubectl get pod
Error from server (Forbidden): pods is forbidden: User "kube-user1" cannot list resource "pods" in API group "" in the namespace "default"

```

报错，因为并未获得集群资源的访问权限。

切换回管理员账户

```shell
[root@k8s-master pki]# kubectl config use-context kubernetes-admin@kubernetes
Switched to context "kubernetes-admin@kubernetes".

```



##### RBAC基于角色的访问控制

Role-Based Access Control

User是一个独立访问计算机系统中的数据或者用数据表示的其它资源的主体（Subject）.Role是指一个组织或任务中的工作或者位置，它代表了一种权利、资格和责任.Permission（许可）是允许对一个或多个 客体(Object)执行的操作。一个用户可经授权而拥有多个角色，一个角色可由多个用户构成；每个角色可拥有多种许可，每个许可也可授权给多个不同的角色。每个操作可施加于多个客体，每个客体也可以接受多个操作

RBAC的基于“角色”（Role）这一核心组件实现了权限指派，具体实现中，它为账号赋予一到多个角色从而让其具有角色之上的权限，其中账号可以是用户账号、用户组、服务账号及其相关的组等，而同时关联至多个角色的账号所拥有的权限是多个角色之上的权限集合。

RBAC是一种操作授权机制，用于界定subject能够或不能够verb哪个或哪类object。动作的发出者即subject，通常以账号为载体，既可以是user account，也可以是service account。verb用于表明要执行的具体操作，包括创建、删除、修改和查看等，而object则是指操作施加于的目标实体，对kerbernetes API来说主要是指各类的资源对象以及非资源型URL

RBAC授权插件支持Role和ClusterRole两类角色，其中Role作用于名称空间级别，用于定义名称空间内的资源权限集合，ClusterRole则用于组织集群级别的资源权限集合，它们都是标准的API资源类型。

###### Role和RoleBinding

Role是一组许可（Permission）权限集合，它描述了对哪些资源可执行何种操作，资源配置清单中使用rules字段嵌套授权规则。

```yaml
# cat role-demo.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: role-pod-reader
  namespace: default
rules:
- resources: ["pods"]
  verbs: ["get","list","watch"]
  apiGroups: [""]

```

RoleBinding用于将Role中定义的权限赋予一个或一组用户，它由一组主体，以及一个要引用来赋予这组主体的Role或ClusterRole组成。RoleBinding仅能够引用同一名称空间的Role对象完成授权。

```yaml
# cat rolebinding-demo.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: resources-reader
  namespace: default
subjects:
- kind: User
  name: kube-user1
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: role-pod-reader
  apiGroup: rbac.authorization.k8s.io

```

执行完上述两个清单

```shell
[root@k8s-master RABC]# kubectl get role
NAME              AGE
role-pod-reader   13m
[root@k8s-master RABC]# kubectl get rolebinding
NAME               AGE
resources-reader   8m47s

```

kube-user1用户便具有了读取default空间中pods资源的权限

切换配置上下文到kube-user1用户进行测试

```shell
[root@k8s-master RABC]# kubectl config use-context kube
kubernetes-admin@kubernetes  kube-user1@kubernetes
[root@k8s-master RABC]# kubectl config use-context kube-user1@kubernetes
Switched to context "kube-user1@kubernetes".
[root@k8s-master RABC]# kubectl get pods -n default
NAME                           READY   STATUS    RESTARTS   AGE
myapp-deploy-8bcf678d7-8qxt4   1/1     Running   9          9d
myapp-deploy-8bcf678d7-xz5ll   1/1     Running   9          9d
myapp-nfs                      1/1     Running   7          6d23h
myapp-sa                       1/1     Running   1          25h
pod-cm-demo                    1/1     Running   5          4d17h
pod-pvc-demo                   1/1     Running   6          6d4h
redis-vol-nfs                  1/1     Running   7          6d23h
# 读取services资源报权限不足
[root@k8s-master RABC]# kubectl get service
Error from server (Forbidden): services is forbidden: User "kube-user1" cannot list resource"services" in API group "" in the namespace "default"

```

#### 网络模型

##### flannel网络插件
Flannel是一种基于overlay网络的跨主机容器网络解决方案，也就是将TCP数据包封装在另一种网络包里面进行路由转发和通信。
flannel为每个host分配一个subnet，容器从这个subnet中分配IP，这些IP可以在host间路由，容器间无须使用nat和端口映射即可实现跨主机通信，每个subnet都是从一个更大的IP池中划分的，flannel会在每个主机上运行一个叫flannel的agent，其职责就是从池子中分配subnet。
flannel使用etcd存放网络配置，已分配subnet、host的IP等信息。保存在/coreos.com/network/config的键下。
flannel数据包在主机间转发是由backend实现的，支持UDP、Vxlan、host-gw、AWS VPC和GCE路由等多种backend。
- VxLAN： 使用内核中的VxLAN模块封装报文，并通过隧道转发机制承载跨节点的Pod通信
- host-gw: 即Host GateWay，它通过节点上创建到达目标容器地址的路由直接完成报文转发，转发性能较好。此种方式要求各节点必须在同一个二层网络中。
- UDP：使用普通UDP报文封装完成隧道转发，性能较低


VxLAN和Directrouting后端
```shell
# configmap中kube-flannel-cfg的片段默认vxlan后端
  net-conf.json: |
    {
      "Network": "10.244.0.0/16",
      "Backend": {
        "Type": "vxlan"
      }
    }

# 路由表信息
[root@k8s-master network]# ip route
default via 192.168.47.2 dev ens33 proto static metric 100
10.244.0.0/24 dev cni0 proto kernel scope link src 10.244.0.1
10.244.1.0/24 via 10.244.1.0 dev flannel.1 onlink
10.244.2.0/24 via 10.244.2.0 dev flannel.1 onlink
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1
192.168.47.0/24 dev ens33 proto kernel scope link src 192.168.47.141 metric 100
#############################################################
# 修改为Directrouting后端
  net-conf.json: |
    {
      "Network": "10.244.0.0/16",
      "Backend": {
        "Type": "vxlan",
        "Directrouting": true
      }
    }
 # 再次查看路由表信息
[root@k8s-master network]# ip route
default via 192.168.47.2 dev ens33 proto static metric 100
10.244.0.0/24 dev cni0 proto kernel scope link src 10.244.0.1
10.244.1.0/24 via 192.168.47.142 dev ens33
10.244.2.0/24 via 192.168.47.143 dev ens33
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1
192.168.47.0/24 dev ens33 proto kernel scope link src 192.168.47.141 metric 100
```

##### 网络策略

网络策略用于控制分组的Pod资源彼此之间如何进行通信，以及分组的Pod资源如何与其它网络端点进行通信的规范，为kubernetes实现更为精细的流量控制，实现租户隔离机制。使用标准的资源对象NetworkPolicy供管理员按需定义网络访问控制策略。

策略控制器用于监控创建Pod时所生成的新API端点，并按需为其附加网络策略。当发生需要配置策略的事件时，侦听器会监视到变化，控制器随即响应以进行接口配置和策略应用。

Pod的网络流量包含Ingress和Egress两种方向，每种方向的控制策略包含“允许”和“禁止”两种。

###### 部署Canal提供网络策略功能

将calico和flannel结合起来最为网络解决方案

> https://docs.projectcalico.org/v3.8/getting-started/kubernetes/installation/flannel

```shell
[root@k8s-master ~]# kubectl apply -f https://docs.projectcalico.org/v3.8/manifests/canal.yaml

# 会拉取以下三个镜像
[root@k8s-master ~]# docker images | grep "^ca" | awk '{print$1":"$2}'
calico/node:v3.8.0
calico/cni:v3.8.0
calico/pod2daemon-flexvol:v3.8.0
```

查看pod生成情况

```shell
[root@k8s-master ~]# kubectl get pod -n kube-system
NAME                                   READY   STATUS    RESTARTS   AGE
canal-2qlq2                            2/2     Running   0          9m34s
canal-dsh22                            2/2     Running   0          39s
canal-rpm6t                            2/2     Running   0          9m34s
```

定义网络策略资源清单

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
spec:
  podSelector:  # 必须字段，选定应用网络策略的pod，字段为空，则选定当前namespace所有pod
    matchLabels：
    matchExpressions：
  egress: # 列出所有应用在选定的pods上的出站规则，如果字段为空，则限制所有出站流量
  ingress: # 列出所有应用在选定的pods上的入站规则，如果字段为空，则不允许所有入站流量
  policyTypes:  # 列出关联的网络策略类型
  - Egress: # 出站规则类型
      ports:  # 列出出站的目标端口
        - port:
          protocol:
      to:  # 列出此规则选定pods的出站目标
        - ipBlock:
          namespaceSelector:
          podSelector:
  - Ingress: # 入站规则类型
      ports:  # 列出能访问选定pods的端口
        - port:
          protocol:
      from:  # 列出此规则能访问选定pods的源
        - ipBlock:
          namespaceSelector:
          podSelector:
```





测试

```shell
# 建立两个namespace dev和prod，并分别创建以Pod实例
[root@k8s-master flannel]# kubectl get pod -n dev -o wide
NAME        READY   STATUS    RESTARTS   AGE    IP           NODE        NOMINATED NODE   READINESS GATES
myapp-pod   1/1     Running   0          113m   10.244.2.3   k8s-node2   <none>           <none>
[root@k8s-master flannel]# kubectl get pod -n prod -o wide
NAME        READY   STATUS    RESTARTS   AGE    IP           NODE        NOMINATED NODE   READINESS GATES
myapp-pod   1/1     Running   0          113m   10.244.1.2   k8s-node1   <none>           <none>

# 新建一个networkpolicy策略清单，拒绝所有进来的流量ingress
[root@k8s-master flannel]# cat deny-all-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  # 不显示指定ingress字段，默认拒绝所有
  policyTypes:
  - Ingress 

# 在dev名称空间能应用策略
[root@k8s-master flannel]# kubectl apply -f deny-all-ingress.yaml -n dev
networkpolicy.networking.k8s.io/deny-all-ingress created

# 在另一个名称空间prod的Pod内访问dev中的Pod实例 ，无法ping通
[root@k8s-master ~]# kubectl exec -it -n prod myapp-pod -- ping 10.244.2.3
PING 10.244.2.3 (10.244.2.3): 56 data bytes


# 修改策略
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  ingress:
  - {}    # 放行所有入站流量
  policyTypes:
  - Ingress  # 默认拒绝所有

# 应用后立刻可以ping通
[root@k8s-master ~]# kubectl exec -it -n prod myapp-pod -- ping 10.244.2.3
PING 10.244.2.3 (10.244.2.3): 56 data bytes




64 bytes from 10.244.2.3: seq=453 ttl=62 time=0.827 ms
64 bytes from 10.244.2.3: seq=454 ttl=62 time=0.676 ms
64 bytes from 10.244.2.3: seq=455 ttl=62 time=0.522 ms
64 bytes from 10.244.2.3: seq=456 ttl=62 time=0.649 ms
64 bytes from 10.244.2.3: seq=457 ttl=62 time=0.740 ms
64 bytes from 10.244.2.3: seq=458 ttl=62 time=0.509 ms
64 bytes from 10.244.2.3: seq=459 ttl=62 time=0.641 ms


# 以下策略，放行入站的80端口的TCP，拒绝其它所有协议
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-tcp
spec:
  podSelector: {}
  ingress:
  - ports:
    - protocol: TCP
      port: 80
  policyTypes:
  - Ingress
```

```yaml
[root@k8s-master flannel]# cat nginx-allow.yaml
# 规则应用在prod名称空间中持有标签app=nginx的pod上
# 放行来自持有标签ns=dev的名称空间访问80端口的流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nginx-allow
  namespace: prod
spec:
  podSelector:
    matchLabels:
      app: nginx
  ingress:
  - ports:
    - port: 80
  - from:
    - namespaceSelector:
         matchLabels:
           ns: dev
  egress:
  - {}
  policyTypes:
  - Ingress
  - Egress
  
[root@k8s-master scheduler]# cat ../flannel/myapp-allow.yaml
# 放行prod名称空间中来自nginx pod的发往myapp pod的80/TCP访问流量
# 同时放行myapp发往nginx pod的所有流量。
# 允许myapp pod与prod名称空间的任何Pod进行互访。
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: myapp-allow
  namespace: dev
spec:
  podSelector:
    matchLabels:
      app: myapp
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx
    ports:
    - port: 80
  - from:
    - namespaceSelector:
        matchLabels:
          ns: prod
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: nginx
  - to:
    - namespaceSelector:
        matchLabels:
          ns: prod
  policyTypes:
  - Ingress
  - Egress
```

#### Pod资源调度

APIServer接收客户到提交Pod对象创建请求后的操作过程后，会由调度器程序从当前集群中选择一个可用的最佳节点来接收并运行。创建Pod对象时，调度器负责为每一个未经调度的Pod资源、基于一系列的规则从集群中挑选一个合适的节点来运行它。调度过程中，调度器不会修改Pod资源，而是从中读取数据，并根据配置的策略挑选出最合适的节点，而后通过API调用将Pod绑定至挑选出的节点之上以完成调度过程。

调度操作：

- 节点预选（Predicate）：检查每个节点，过滤掉不符合条件的节点
- 节点优选（Priority）：对预选节点进行优先级排序
- 节点择优（Select）：对优选节点进行择优选择

##### 节点亲和调度

节点亲和调度调度程序用来确定Pod对象调度位置的一组规则，这些规则基于节点上的自定义标签和Pod对象上指定的标签选择器进行定义。

pod.spec.affinity.nodeAffinity

类型：

- 硬亲和性（required）：强制性规则，必须满足的规则，不满足则处于Pending状态

- 软亲和性（preferred）：非强制性，尽量满足需求即可，

定义节点规则：

- 为节点配置合乎需求的标签
- 为Pod对象定义合理的标签选择器

**节点硬亲和性**

```shell
# Pod将被调度至有zone标签且值为foo的节点上
[root@k8s-master scheduler]# cat nodeselector-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nodeaffinity-nodeselect
spec:
  containers:
  - name: myapp
    image: ikubernetes/myapp:v7
    imagePullPolicy: IfNotPresent
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - {key: zone, operator: In, values: ["foo"]}
# pod一直处于pending状态
[root@k8s-master scheduler]# kubectl get pod
NAME                      READY   STATUS    RESTARTS   AGE
nodeaffinity-nodeselect   0/1     Pending   0          8s

# 为node1节点打上label
[root@k8s-master scheduler]# kubectl label nodes k8s-node1 zone=foo
node/k8s-node1 labeled

# 查看pod被调度到node1节点上
[root@k8s-master scheduler]# kubectl get pod
NAME                      READY   STATUS              RESTARTS   AGE
nodeaffinity-nodeselect   0/1     ContainerCreating   0          3m59s
[root@k8s-master scheduler]# kubectl get pod -o wide
nodeaffinity-nodeselect   1/1     Running   0          5m23s   10.244.1.9   k8s-node1   <none>           <none>
```

**节点软亲和性**

节点软亲和性为节点机制提供了一种柔性控制逻辑，被调度的Pod对象不再是“必须”而是“应该”放置于某些特定节点之上，条件不满足时，也能接受被编排于其它不符合的节点上，还提供倾向性权重weight，以便于用户定义其优先级。

```shell
[root@k8s-master scheduler]# cat nodeselector-pod-pref.yaml
# Pod更倾向被调度到有zone=foo标签的节点上，其权重为60，
# 如果节点同时具有zone=foo标签，且存在ssd标签（权重为30）,
# 则该节点的权重将会为60+30，pod将会被调度该节点
apiVersion: v1
kind: Pod
metadata:
  name: nodeaffinity-nodeselect-pref
spec:
  containers:
  - name: myapp
    image: ikubernetes/myapp:v7
    imagePullPolicy: IfNotPresent
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - preference:
          matchExpressions:
          - key: zone
            operator: In
            values:
            - foo
        weight: 60
      - preference:
          matchExpressions:
          - key: ssd
            operator: Exists
            values: []
        weight: 30

[root@k8s-master scheduler]# kubectl label nodes k8s-node1 zone=foo
[root@k8s-master scheduler]# kubectl label nodes k8s-node2 ssd=true

[root@k8s-master scheduler]# kubectl apply -f nodeselector-pod-pref.yaml

# 会被调度到node1上
[root@k8s-master scheduler]# kubectl get pod -o wide
NAME                           READY   STATUS    RESTARTS   AGE   IP            NODE        NOMINATED NODE   READINESS GATES
nodeaffinity-nodeselect-pref   1/1     Running   0          10s   10.244.1.15   k8s-node1   <none>           <none>

# 给node2节点打上zone=foo标签
[root@k8s-master scheduler]# kubectl label nodes k8s-node2 zone=foo

[root@k8s-master scheduler]# kubectl apply -f nodeselector-pod-pref.yaml

# 被调度到node2节点上
[root@k8s-master scheduler]# kubectl get pod -o wide
NAME                           READY   STATUS    RESTARTS   AGE    IP            NODE        NOMINATED NODE   READINESS GATES
nodeaffinity-nodeselect-pref   1/1     Running   0          9m5s   10.244.2.10   k8s-node2   <none>           <none>
```

##### Pod资源亲和调度

把一些pod对象组织在相近的位置，反之，成为反亲和性（anti-affinity）

Pod亲和性调度需要各相关的Pod对象运行于“同一位置“，而反亲和性调度则要求它们不能运行于”同一位置“。取决于节点的位置拓扑 spec.affinity.podAffinity.requiredDuringSchedulingIgnoredDuringExecution.topologyKey 

pod.spec.affinity.podAffinity

```yaml
[root@k8s-master scheduler]# cat podselector-pod-require.yaml
apiVersion: v1
kind: Pod
metadata:
  name: podselector-label-require-1
  labels:
    app: myapp
spec:
  containers:
  - name: myapp
    image: ikubernetes/myapp:v7
    imagePullPolicy: IfNotPresent
---
# pod对象将被调度到持有app=myapp的pod对象所在节点
apiVersion: v1
kind: Pod
metadata:
  name: podselector-label-require-2
spec:
  containers:
  - name: busybox
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command: ["sh","-c","sleep 3600"]
  affinity:
    podAffinity:
    # 硬亲和
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels: {app: myapp}
        topologyKey: kubernetes.io/hostname
```

pod.spec.affinity.podAffinity反亲和性

```yaml
# pod对象将被调度到不包含有app=myapp的pod对象所在节点
apiVersion: v1
kind: Pod
metadata:
  name: podselector-label-require-2
spec:
  containers:
  - name: busybox
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command: ["sh","-c","sleep 3600"]
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels: {app: myapp}
        topologyKey: kubernetes.io/hostname
```

##### 污点和容忍度

污点（taints）是定义在节点之上的键值型属性数据，用于让节点拒绝将pod调度运行于其上，除非该Pod对象具有接纳节点污点的容忍度。

污点effect类型：

- Noschedule:不能容忍此污点的新Pod对象，不能被调度此节点，节点现有Pod不受影响，属于强制性约束
- PreferNoSchedule：非强制性约束，不能容忍此污点的新Pod对象尽量不要调度至此节点，不过无其它节点可供调度时，可接受响应的Pod对象
- NoExecute：不能容忍此污点的新Pod对象，不可被调度至此节点，属于强制型约束关系，对现存的Pod有影响

```shell
# 给节点node2定义污点 类型为NoSchedule
[root@k8s-master scheduler]# kubectl taint node k8s-node2 node-type=production:NoSchedule

# deployment的pod对象都被调度到node1上
[root@k8s-master scheduler]# kubectl get pod -o wide
NAME                           READY   STATUS    RESTARTS   AGE     IP            NODE        NOMINATED NODE   READINESS GATES
myapp-deploy-8bcf678d7-2tdlp   1/1     Running   0          7m31s   10.244.1.21   k8s-node1   <none>           <none>
myapp-deploy-8bcf678d7-p9k9k   1/1     Running   0          7m30s   10.244.1.22   k8s-node1   <none>           <none>
```

```shell
# 将节点node1污点effect类型改为NoExecute
# 可查看到，原本在node1上的pod最终被驱逐，转移到node2上
[root@k8s-master scheduler]# kubectl taint node k8s-node1 node-type=production:NoExecute
node/k8s-node1 tainted
[root@k8s-master scheduler]# kubectl get pod -o wide
NAME                           READY   STATUS              RESTARTS   AGE    IP            NODE        NOMINATED NODE   READINESS GATES
myapp-deploy-8bcf678d7-2tdlp   1/1     Terminating         0          8m5s   10.244.1.21   k8s-node1   <none>           <none>
myapp-deploy-8bcf678d7-p9k9k   1/1     Terminating         0          8m4s   10.244.1.22   k8s-node1   <none>           <none>
myapp-deploy-8bcf678d7-sfzlw   0/1     Pending             0          1s     <none>        k8s-node2   <none>           <none>
myapp-deploy-8bcf678d7-zwdxr   0/1     ContainerCreating   0          1s     <none>        k8s-node2   <none>           <none

[root@k8s-master scheduler]# kubectl get pod -o wide
NAME                           READY   STATUS    RESTARTS   AGE   IP            NODE        NOMINATED NODE   READINESS GATES
myapp-deploy-8bcf678d7-sfzlw   1/1     Running   0          35s   10.244.2.17   k8s-node2   <none>           <none>
myapp-deploy-8bcf678d7-zwdxr   1/1     Running   0          35s   10.244.2.16   k8s-node2   <none>           <none>
```

容忍度（tolerations）是定义在Pod对象上的键值型属性数据，用于配置其可容忍的节点污点，而且调度器仅能将Pod对象调度至其能够容忍该节点污点的节点之上。

pod.spec.tolerations定义