# 0002 Docker 与权限边界(阶段 0.3~0.4,一次有教学价值的失败)

## 三问(阶段动机)

```
✅ 0.环境准备  ⬜ 1.跑起服务(你在这里:前置条件排查)  ⬜ 2.监控  ⬜ 3.调参  ⬜ 4.压测  ⬜ 5.量化与K8s
```

- **这阶段干嘛的:** 想给 Docker 打通 GPU 透传,结果发现这台租来的机器**从内核层面禁止跑容器**,最后放弃。
- **什么需求逼的:** 生产上推理服务全是容器交付,本想学会这条标准路径。
- **解决了什么麻烦:** 虽败犹荣——练出了"判断一台机器能不能跑 Docker"的诊断方法,这比装成功更值钱。

## 全链路一览

```
Docker 想干一件事:造一个"套娃"(容器里再跑容器)
   │  需要内核给三种权限
   ▼
第 1 关:改网络规则(iptables)  → 被拒,缺 NET_ADMIN  → 绕过 ✅
第 2 关:挂载文件系统(overlayfs)→ 被拒,缺 SYS_ADMIN → 换 fuse-overlayfs 尝试 ❌
第 3 关:创建命名空间(unshare) → 被 seccomp 内核级封锁 ❌ 无解
```

容器 = 用"命名空间"给进程划独立房间。`unshare` 就是"划房间"的动作,被保安(seccomp)直接拦下,后面一切免谈。

## 跟着数据走(排查三连)

1. `service docker start` 报"done" → 但 `docker ps` 连不上。**第一反应:看日志** `tail /var/log/docker.log` → 最后一行写着死因 `iptables ... Permission denied`。
2. 改 `/etc/docker/daemon.json` 加 `"iptables": false, "bridge": "none"` 绕过 → dockerd 活了。
3. 拉镜像又挂:`mount: operation not permitted` → 换 fuse-overlayfs 还挂:`unshare: operation not permitted` → **确诊边界,换路线**。

## 新技术点四要素

**Docker 权限三件套(诊断命令,以后到哪台机器都能用)**
- 名字:capabilities(能力位)+ seccomp(系统调用过滤)
- 作用:Linux 给进程发的"通行证"。`capsh --print` 看你的通行证上盖了哪些章;`Seccomp: 2` = 严格模式,敏感动作一律拦
- 参数:诊断三连——`cat /proc/1/comm`(输出 tini = 你本身就在容器里)、`unshare -m true`(失败 = 跑不了 Docker)、`grep Seccomp /proc/self/status`
- 用法:租到任何新机器,先跑这三条摸底

**registry-mirrors(Docker Hub 国内加速)**
- 名字:Docker 镜像加速器
- 作用:Docker Hub 在国外,直连超时;加速器是国内中转站
- 参数:写进 `/etc/docker/daemon.json` 的 `registry-mirrors`,如 `https://docker.1ms.run`
- 用法:本机已配好(虽然暂时用不上),换到有权限的机器直接生效

## 关键顿悟

- **环境边界问题不硬刚。** 缺权限分两种:配置能绕的(iptables)绕过去;内核封死的(seccomp)立刻换路线,别耗。
- **排障 = 看日志找最后一行。** 一堆报错里,真正的死因永远在最底下那条。
- **便宜租卡平台都不支持 Docker。** AutoDL/gpuhome 这类给你的本来就是容器,套娃被禁是常态——所以 Phase 1 直装 vLLM,不受影响。
