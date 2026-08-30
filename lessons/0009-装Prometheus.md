# 0009 装 Prometheus:让抄表自动化(阶段 2.2)

## 三问(阶段动机)

```
✅ 2.1 裸看指标  ✅ 2.2 Prometheus(你在这里)  ⬜ 2.3 Grafana 画图  ⬜ 2.4 对照实验
```

- **这阶段干嘛的:** 装 Prometheus,让它每 15 秒自动去 vLLM 的 `/metrics` 抄一次账,存起来。
- **什么需求逼的:** 手动 curl 只能看"现在";出了事故要复盘"出事前 10 分钟发生了什么",就得有人持续记账。
- **解决了什么麻烦:** 指标变成历史时间序列,随时能查任意时间段——这是监控系统的地基。

## 全链路一览

```
vLLM:8000/metrics(账本摊开)
   ▲
   │  每 15 秒主动上门抄一次(pull 模型)
Prometheus:9090(抄表员 + 仓库:抄来的账按时间存好)
   │
   ▼
提供查询语言 PromQL(问:"最近 5 分钟每秒吐多少字?")
(下一步:Grafana 来查它,画成曲线)
```

**为什么是"主动上门抄"(pull)而不是"服务自己报"(push):**
抄表员主动上门,谁家没开门(服务挂了)立刻知道;自己报案制,出了事的往往报不出来。
这是 Prometheus 的核心设计选择。

## 跟着数据走

1. 解压出 `prometheus` 一个二进制文件 + 一个配置文件 `prometheus.yml`——**就这么两个东西**
2. 配置文件里登记"抄谁的账":

```yaml
scrape_configs:
  - job_name: vllm            # 给这个抄表任务起个名
    scrape_interval: 15s      # 每 15 秒抄一次(默认值,写出来是为了让你看见)
    static_configs:
      - targets: ["localhost:8000"]   # vLLM 的地址
        # metrics_path 默认就是 /metrics,正好对上
```

3. 启动:`./prometheus --config.file=prometheus.yml`(占着一个前台窗口,和 vLLM 一样)
4. 验证抄到了:浏览器/接口查 `http://localhost:9090/api/v1/query?query=vllm:gpu_cache_usage_perc`

## 新技术点四要素

**Prometheus(监控界的"抄表员+仓库")**
- 名字:Prometheus,CNCF 毕业的监控系统,事实标准
- 作用:定时抓取(pull)各服务的 `/metrics`,按时间存成本地数据库(TSDB),提供查询语言
- 参数:`prometheus.yml` 里 `scrape_interval`(抄表频率)、`targets`(抄谁);命令行 `--storage.tsdb.retention.time`(账存多久,默认 15 天)
- 用法:本项目挂载点——`~/work/prometheus/` 目录,9090 端口

**PromQL(查账的语言)**
- 名字:Prometheus Query Language
- 作用:向时间序列数据库提问。本阶段只用到最简形态:直接写指标名
- 参数/用法:后面 Grafana 里会用到 `rate(vllm:generation_tokens_total[5m])` 这种(5 分钟内的增速)——2.4 细讲

## 关键顿悟

- **监控系统 = 抄表员 + 仓库 + 查询语言**,不是一个神秘黑盒。
- **pull 模型让"服务挂了"自带告警**——抄不到就是出事,简单粗暴但有效。
- **配置即登记。** `prometheus.yml` 本质就是一张"抄表清单",运维改监控 = 改这张清单。
