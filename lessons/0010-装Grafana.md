# 0010 装 Grafana:把账本画成图(阶段 2.3)

## 三问(阶段动机)

```
✅ 2.1 裸看指标  ✅ 2.2 Prometheus 抄表  ✅ 2.3 Grafana 画图(你在这里)  ⬜ 2.4 对照实验
```

- **这阶段干嘛的:** 装 Grafana,连上 Prometheus,把 KV 缓存使用率画成第一条曲线,用浏览器看。
- **什么需求逼的:** 数字账本给人看太费劲,曲线一眼就能看出趋势和异常——"面多了加水、水多了加面"全靠看图。
- **解决了什么麻烦:** 顺便学会 SSH 端口转发——Mac 浏览器访问远端服务器网页的通用技能。

## 全链路一览

```
你的 Mac 浏览器(http://localhost:3000)
   │  SSH 隧道:ssh -L 3000:localhost:3000 gpu(把服务器的 3000 端口"借"到 Mac 上)
   ▼
Grafana:3000(画图师傅,自己不存数据)
   │  查账(PromQL 查询)
   ▼
Prometheus:9090(仓库)  ← 每15秒抄 ←  vLLM:8000/metrics
```

**Grafana 不存数据**,它只是"看图说话":你配好数据源(Prometheus 的地址),
它帮你把 PromQL 查询结果画成曲线。

## 跟着数据走

1. 服务器上解压启动 grafana(又是一个单目录二进制,前台跑在新窗口)
2. Mac 上开隧道:`ssh -L 3000:localhost:3000 gpu -N`——**这条命令翻译成大白话:**
   "我 Mac 上的 3000 端口,敲门后请转交给服务器那头的 localhost:3000"。`-N` 表示只转发不开 shell
3. Mac 浏览器开 `http://localhost:3000`,默认账号 `admin` / `admin`(首次登录让改密码)
4. 加数据源:Connections → Data sources → Prometheus → URL 填 `http://localhost:9090` → Save & test 变绿
5. 建第一个面板:Dashboards → New → Add visualization → 查询框输入 `vllm:kv_cache_usage_perc` → 看到一条(目前贴地的)线

## 新技术点四要素

**SSH 端口转发(过墙梯/借道)**
- 名字:SSH local port forwarding(`-L`)
- 作用:服务器在安全组/防火墙后面,网页端口不对外开放;用 SSH 隧道把远端端口"借"到本机,浏览器访问 `localhost:3000` 就像服务跑在 Mac 上
- 参数:`ssh -L <本机端口>:<远端看到的地址>:<远端端口> <主机>`;`-N` 只转发不进 shell
- 用法:本项目挂载点——Grafana(3000);以后 Jupyter(8888)、任何内网 Web 都用这招

**Grafana(监控界的"画图师傅")**
- 名字:Grafana,开源可视化平台
- 作用:连各种数据源(Prometheus/MySQL/…),把查询画成仪表板;运维的"驾驶舱"
- 参数:核心概念三个——Data source(连哪个仓库)、Panel(一张图)、Dashboard(一面墙)
- 用法:本项目挂载点——第一个面板画 KV 缓存使用率

## 关键顿悟

- **Grafana 不存数据,只负责画。** 数据在 Prometheus 里;Grafana 挂了数据不丢,反之亦然——分工明确。
- **SSH 隧道是内网访问的瑞士军刀。** 记住 `-L` 这一招,以后访问不到的内网服务都能这样借道。
- **第一条曲线贴地是正常的。** 现在没人用服务,KV 使用率 ≈ 0;下一阶段我们发请求让它跳起来。
- **指标名会随版本漂移。** 本阶段实测:vLLM 0.27 把 `vllm:gpu_cache_usage_perc` 改名为 `vllm:kv_cache_usage_perc`,旧教程的查询全报 no data。唯一可信的是服务自己的 `/metrics`,grep 一下对真名。
