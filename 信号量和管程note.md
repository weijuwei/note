#### 并发问题
- 多线程并发导致资源竞争
同步概念
- 协调多线程对共享数据的访问
- 任何时刻只能有一个线程执行临界区代码
确保同步的方法
- 底层硬件支持 禁用中断  原子操作（阻塞 忙等） 原子
- 高层次编程抽象  锁

#### 信号量（Semaphore）
信号量是操作系统提供的一种协调
- 共享资源访问的方法
  - 软件同步是平等线程间的一种同步协商机制
  - OS是管理者，地位高于进程
  - 用信号量表示系统资源数量
- 信号是一种抽象数据类型
  - 由一个整型（sem）变量和两个原子操作组成
  - P()操作，申请资源
    - sem减1
    - sem<0,进入等待，否则继续
  - V()操作，释放资源
    - sem加1
    - sem<=0,唤醒一个等待进程  
##### 信号量特性
  - 信号量是被保护的整数变量
    - 初始化完成后，只能通过P()和V()才做修改
    - 由操作系统保证，PV操作是原子操作
  - P()可能阻塞，V()不会阻塞
  - 通常假定信号量是“公平的”
    - 线程不会被无限期阻塞在P()操作
    - 假定信号量等待按先进先出排队
##### 信号量实现
```
classSemaphore{
    int sem;  // 信号量变量
    WaitQueue q;  // 等待队列
}
Semaphore::P(){
    sem--;
    if (sem < 0){
        add this thread t to q; // 添加当前线程到等待队列
        block(p)  // 阻塞当前线程
    }
}
Semaphore::V(){
    sem++;
    if (sem <= 0){
        remove a thread t from q; // 从等待队列中取出一个线程
        wakup(t)  // 唤醒从等待队列中取出的线程
    }
}
```
##### 信号量使用
######  信号分类
- 二进制信号量：资源数目为0或1
- 资源信号量：资源数目为任何非负值
- 两者等价
  - 基于一个可以实现另一个
###### 使用
- 互斥访问
  - 临界区的互斥访问控制
  - 必须成对使用P()和V()操作
    - P()操作保证互斥访问临界资源
    - V()操作使用后释放临界资源
    - PV操作不能次序错误、重复或遗漏
```
# 每类资源设置一个信号量，初始值为1
mutex = new Semaphore(1)

mutex -> P();
Critical Section; // 临界区
mutex -> V();
```
- 条件同步
  - 线程间事件等待
```
# 设置信号量初始值为0
# 线程A M操作依赖于线程B X操作，即，当B的x操作未执行完则A在N操作之前处于阻塞状态
condition = new Semaphore(0)

thread_A
    condition -> P();
    M 操作;
  
thread_B
    X操作;
    conditon -> V();
```
##### 读者-写者问题
- 描述
  - 共享数据的两类使用者
    - 读者：支读取数据，不修改
    - 写者：读取和修改数据
  - 问题描述：对共享数据的读写
    - ‘读 - 读’允许
      - 同一时刻，允许有多个读者同时读
    - ‘读 - 写’互斥
      - 没有写者时读者才能读
      - 没有读者时写者才能写
    - ‘写 - 写’互斥
      - 没有其他写者时写者才能写
###### 用信号量解决读者-写者问题
- 信号量描述每个约束
  - 信号量WriteMutex
    - 控制读写操作的互斥
    - 初始化为1
  - 读者计数Rcount
    - 正在进行读操作的读者数目
    - 初始化为0
  - 信号量CountMutex
    - 控制对读者计数的互斥修改
    - 初始化为1
- 优先策略
  - 读者优先策略
    - 只要有读者正在读状态，后来的读者都能直接进入
    - 如读者持续不断进入，则写者就处于饥饿
  - 写者优先策略
    - 只要有写者就绪，写者应尽快执行写操作
    - 如写者持续不断就绪，则读者就处于饥饿
```
# 读者优先
Write进程

    WriteMutex -> P();
    
    write;
    
    WriteMutex -> V();

Reader进程
    CountMutex -> P();
    if (Rcount == 0)  // 如果是第一个读者，需要进行判断是否有写者
      WriteMutex -> P();
    ++Rcount;
    read;
    
    --Rcount
    if (Rcount == 0)  // 如果是最后一个读者，需要进行判断是否有写者正在等待
      WriteMutex -> V();
    CountMutex -> V();
```

##### 生产者-消费者问题
生产者  --->  缓冲区  --->  消费者
- 有界缓冲区问题描述
  - 一个或多个生产者在生成数据后放在一个缓冲区中
  - 单个消费者虫从缓冲区取出数据处理
  - 任何时刻只能有一个生产者或消费者可访问缓冲区
- 问题分析
  - 任何时刻只能有一个线程操作缓冲区   （互斥访问）
  - 缓冲区空时，消费者必须等待生产者   （条件同步）
  - 缓冲区满时，生产者必须等待消费者   （条件同步）
- 用信号量描述每个约束
  - 二进制信号量mutex      --> 保证对缓冲区的互斥访问
  - 资源信号量fullBuffers（缓冲填充数量）  --> 消费者
  - 资源信号量emptyBuffers（缓冲空闲数量） --> 生产者
###### 信号量实现生产者-消费者问题
```
Class BoundedBuffer{
    mutex = new Semaphore(1);
    fullBuffers = new Semaphore(0);
    emptyBuffers = new Semaphore(n);  // 空闲数量，初始为缓冲区大小
}
Class BoundedBuffer::Deposit(c){
    emptyBuffers -> P();  // 判断是否缓冲空闲数是否为空，空则阻塞
    mutex -> P();
    add c to the buffer;  // 向缓冲添加资源
    mutex -> V();
    fullBuffers -> V();  // 缓冲填充数量+1
}
Class BoundedBuffer::Remove(c){
    fullBuffers -> P();  // 判断缓冲是否问空，空则阻塞
    mutex -> P();
    remove c from buffer;  // 从缓冲取出资源
    mutex -> V();
    emptyBuffers -> V();  // 缓冲区空闲数量+1
}
```

#### 管程（Moniter）
管程是一种用于多线程互斥访问共享资源的程序结构
  - 采用面向对象方法，简化线程间的同步控制
  - 任意时刻最多只有一个线程执行管程代码
  - 正在管程中的线程可临时放弃管程的互斥访问，等待事件出现时恢复
##### 使用
  - 在对象/模块中，收集相关共享数据
  - 定义访问共享数据的方法
##### 组成
  - 一个锁 入口队列处
    - 控制管程代码的互斥访问
  - 0或多个条件变量
    - 管理共享数据的并发访问
##### 条件变量 （Conditon Variable）
- 条件变量是管程内的等待机制
  - 进入管程的线程因资源被占用而进入等待状态
  - 每个条件变量表示一种等待原因，对应一个等待队列
- Wait()操作
  - 将自己阻塞在等待队列中
  - 唤醒一个等待者或释放管程的互斥访问
- Signal()操作
  - 将等待队列中的一个线程唤醒
  - 如果等待队列为空，则等同空操作
- 实现
```
Class Conditon{
    int numWaiting = 0;
    WaitQueue = q;
}
Conditon::Wait(lock){
    nunWaiting++;
    add this thread t to q;
    release(lock);  // 释放锁
    schedule();  // need mutex
    require(lock)  // 调度完成后重新获取锁，取得管程的执行权限
}
Conditon::Signal(){
    if (numWaiting > 0){
        remove a thread t from q;
        wakeup(t); // 唤醒thread
        numWaiting--;
    }
}
```
##### 管程实现生产者-消费者问题
```
class BounderdBuffer{
    Lock lock;
    int count = 0;  //写入缓冲区的数目
    Condition notFull, notEmpty;
}
class BounderBuffer::Deposit(c){
    lock -> Acquire();  // 等待直到锁可用，然后抢占锁
    while (count == n) // 判断是否满足条件变量 
        notFull.Wait(&lock);  // 如果缓冲区满了，则等待在条件变量上
    add c to the buffer;
    count ++;
    notEmpty.Signal();  // 唤醒线程等待队列中的消费者线程取数据，如果有
    lock -> Release();  // 释放锁，唤醒等待者，如果有
}
class BounderBuffer::Remove(c){
    lock -> Acquire();  // 等待直到锁可用，然后抢占锁
    while (count == 0)  // 判断是否满足条件变量
        notEmpty.Wait(&lock)；  // 满足则等待当前条件变量
    remove c from the buffer;
    count --;
    notFull.Signal();  // 唤醒等待队列中的生产者生产数据，如果有
    lock -> Release();  // 释放锁，唤醒等待者，如果有
}
```
##### 管程实现读者-写者问题
```
# 两个基本方法
Database::Read(){  // 读者
    Wait until no writers;
    read database;
    check out - wake up waiting writers;
}
Database::Write(){  // 写者
    Wait until no reader/writers;
    write database;
    check out - wake up waiting readers/writers;
}
# 管程的状态变量
AR = 0;   // 活动的读者
AW = 0;   // 活动的写者
WR = 0;   // 正在等待的读者
WW = 0;   // 正在等待的写者
Lock lock; // 管程互斥锁
Condition okToRead;  // 可读条件
Condition okToWrite; // 可写条件
```

